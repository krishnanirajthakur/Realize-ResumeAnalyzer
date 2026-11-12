"""
Bulk Resume Screening & Ranking View - Realize
"""
import streamlit as st
import pandas as pd
from core.models import CandidateProfile, JobDescription, AnalysisResult
from core.parsers.pdf_parser import parse_pdf
from core.parsers.docx_parser import parse_docx
from core.parsers.jd_parser import parse_job_description
from core.preprocessing.text_cleaner import clean_text, extract_contact_info, extract_candidate_name
from core.preprocessing.section_extractor import extract_sections
from core.matching.skill_extractor import extract_skills_from_text
from core.scoring.scoring_engine import CandidateScoringEngine
from reporting.csv_exporter import export_batch_to_csv
from ui.components import render_kpi_card, render_fit_badge

def render_bulk_screening_view():
    st.markdown("## Bulk Resume Screening & Ranking")
    st.markdown("High-throughput batch evaluation with resilient fault tolerance and transparent candidate ranking.")

    # Target Job Description Selection
    st.markdown("#### 1. Target Requisition Benchmark")
    active_jd = st.session_state.get("active_jd")

    if active_jd:
        st.success(f"Active Benchmark: **{active_jd.title}** ({len(active_jd.required_skills)} required skills, {active_jd.required_experience_years} yrs exp)")
    else:
        st.info("No benchmark Job Description currently active. Provide the target Job Description below:")
        
    with st.expander("📝 Provide / Update Benchmark Job Description", expanded=(active_jd is None)):
        jd_input_mode = st.radio("Benchmark Input Method:", ["Paste JD Text", "Upload JD File"], horizontal=True, key="bulk_jd_mode")
        jd_input_text = ""
        if jd_input_mode == "Paste JD Text":
            jd_input_text = st.text_area("Paste Target Job Description:", height=150, placeholder="Paste requirements and qualifications...")
        else:
            jd_upload = st.file_uploader("Upload JD Document:", type=["pdf", "docx", "txt"], key="bulk_jd_upload")
            if jd_upload:
                try:
                    if jd_upload.name.lower().endswith(".pdf"):
                        jd_input_text, _ = parse_pdf(jd_upload)
                    elif jd_upload.name.lower().endswith(".docx"):
                        jd_input_text, _ = parse_docx(jd_upload)
                    else:
                        jd_input_text = jd_upload.read().decode("utf-8", errors="ignore")
                except Exception as e:
                    st.error(f"Error reading JD: {str(e)}")

        if st.button("Set as Active Benchmark Role", use_container_width=True):
            if jd_input_text.strip():
                new_jd = parse_job_description(jd_input_text, extract_skills_from_text)
                st.session_state["active_jd"] = new_jd
                st.success(f"Benchmark set to: '{new_jd.title}'")
                st.rerun()
            else:
                st.warning("Please provide valid JD text first.")

    active_jd = st.session_state.get("active_jd")
    if not active_jd:
        return

    # File Ingestion Section
    st.markdown("---")
    st.markdown("#### 2. Candidate Document Ingestion")
    
    uploaded_files = st.file_uploader(
        "Upload Multiple Candidate Resumes (PDF or DOCX):",
        type=["pdf", "docx"],
        accept_multiple_files=True,
        key="bulk_file_uploader",
        help="Select multiple candidate resume files to evaluate simultaneously against the benchmark requisition."
    )

    # Start Batch Evaluation
    if uploaded_files:
        st.caption(f"{len(uploaded_files)} candidate resume document(s) staged for batch evaluation.")
        if st.button(f"Process Batch ({len(uploaded_files)} Resumes)", type="primary", use_container_width=True):
            progress_bar = st.progress(0.0)
            status_text = st.empty()
            
            engine = CandidateScoringEngine(st.session_state.get("app_config").weights)
            batch_results = []
            failed_files = []

            for idx, file_item in enumerate(uploaded_files):
                fname = file_item.name
                status_text.text(f"Evaluating ({idx+1}/{len(uploaded_files)}): {fname}...")
                try:
                    # Ingest
                    if fname.lower().endswith(".pdf"):
                        raw_text, _ = parse_pdf(file_item)
                    else:
                        raw_text, _ = parse_docx(file_item)
                        
                    clean_res = clean_text(raw_text)
                    sections = extract_sections(clean_res)
                    email, phone = extract_contact_info(clean_res)
                    cand_name = extract_candidate_name(clean_res, fname)
                    cand_skills = extract_skills_from_text(clean_res)
                    
                    profile = CandidateProfile(
                        candidate_id=fname,
                        source_filename=fname,
                        name=cand_name,
                        email=email,
                        phone=phone,
                        raw_text=raw_text,
                        clean_text=clean_res,
                        sections=sections,
                        skills=cand_skills
                    )
                    
                    res = engine.evaluate_candidate(profile, active_jd)
                    batch_results.append(res)
                except Exception as e:
                    # Fault tolerance: do not halt the entire batch
                    failed_files.append((fname, str(e)))
                    
                progress_bar.progress((idx + 1) / len(uploaded_files))

            status_text.text("Batch evaluation completed.")
            
            # Store in session state
            st.session_state["bulk_batch_results"] = batch_results
            st.session_state["bulk_failed_files"] = failed_files
            
            # Also merge into general evaluation history
            existing = st.session_state.get("evaluations_history", [])
            seen_ids = set(r.candidate.candidate_id for r in batch_results)
            merged = [e for e in existing if e.candidate.candidate_id not in seen_ids] + batch_results
            st.session_state["evaluations_history"] = merged
            
            st.rerun()

    # Display Batch Results
    batch_results = st.session_state.get("bulk_batch_results", [])
    failed_files = st.session_state.get("bulk_failed_files", [])

    if failed_files:
        st.error(f"⚠️ {len(failed_files)} file(s) failed during parsing and were isolated without halting the batch.")
        for fname, err in failed_files:
            st.caption(f"- `{fname}`: {err}")

    if not batch_results:
        return

    st.markdown("---")
    st.markdown("#### 3. Batch Evaluation Telemetry & Ranking")

    # KPI Summary Row
    avg_score = round(sum(r.overall_score for r in batch_results) / len(batch_results), 1)
    top_score = max(r.overall_score for r in batch_results)
    strong_fits = sum(1 for r in batch_results if r.overall_score >= 80)
    
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        render_kpi_card("Processed Resumes", str(len(batch_results)), "Successfully evaluated", "neutral")
    with k2:
        render_kpi_card("Average Score", f"{avg_score}%", "Batch mean suitability", "positive" if avg_score >= 70 else "neutral")
    with k3:
        render_kpi_card("Top Match Score", f"{top_score}%", "Highest ranked applicant", "positive")
    with k4:
        render_kpi_card("Strong Fit Candidates", str(strong_fits), "Score ≥ 80.0%", "positive" if strong_fits > 0 else "neutral")

    # Controls: Filter, Search, Sort
    c_f1, c_f2, c_f3 = st.columns([2, 1, 1])
    with c_f1:
        search_query = st.text_input("Filter Candidates by Name or Skill:", placeholder="Search e.g. Python, Docker, Sarah...")
    with c_f2:
        tier_filter = st.selectbox("Filter by Fit Tier:", ["All Tiers", "Strong Fit", "Moderate Fit", "Partial Fit", "Limited Fit"])
    with c_f3:
        sort_by = st.selectbox("Sort By:", ["Overall Score (Desc)", "Skill Match (Desc)", "Tenure (Desc)", "Confidence (Desc)"])

    # Apply Filters
    filtered_results = batch_results.copy()
    if search_query:
        sq = search_query.lower()
        filtered_results = [
            r for r in filtered_results
            if sq in r.candidate.name.lower() or any(sq in s.lower() for s in r.candidate.skills)
        ]
    if tier_filter != "All Tiers":
        filtered_results = [r for r in filtered_results if r.fit_tier == tier_filter]
        
    # Apply Sorting
    if sort_by == "Overall Score (Desc)":
        filtered_results.sort(key=lambda x: x.overall_score, reverse=True)
    elif sort_by == "Skill Match (Desc)":
        filtered_results.sort(key=lambda x: x.components["skill_match"].raw_score, reverse=True)
    elif sort_by == "Tenure (Desc)":
        filtered_results.sort(key=lambda x: x.candidate.experience_years, reverse=True)
    elif sort_by == "Confidence (Desc)":
        filtered_results.sort(key=lambda x: x.confidence_score, reverse=True)

    # Ranking Table Dataframe
    table_data = []
    for rank, r in enumerate(filtered_results, start=1):
        table_data.append({
            "Rank": rank,
            "Candidate Name": r.candidate.name or "Candidate",
            "File": r.candidate.source_filename,
            "Overall Score": f"{r.overall_score}%",
            "Fit Tier": r.fit_tier,
            "Skills Match": f"{round(r.components['skill_match'].raw_score, 1)}%",
            "Verified Tenure": f"{r.candidate.experience_years} yrs",
            "Tenure Gap": f"{r.experience_gap_years} yrs",
            "Degree": r.candidate.education_level,
            "Confidence": f"{r.confidence_score}%",
        })

    df_display = pd.DataFrame(table_data)
    st.dataframe(df_display, use_container_width=True, hide_index=True)

    # Export & Candidate Selection Action Bar
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    col_act1, col_act2 = st.columns([1, 1])
    
    with col_act1:
        # CSV Export
        csv_data = export_batch_to_csv(filtered_results)
        st.download_button(
            label="Download Complete Batch Ranking (CSV)",
            data=csv_data,
            file_name=f"realize_batch_{active_jd.title.replace(' ', '_').lower()}.csv",
            mime="text/csv",
            use_container_width=True
        )
        
    with col_act2:
        # Quick Multi-Candidate Selection for Comparison
        candidate_options = [f"{r.candidate.name} ({r.candidate.source_filename})" for r in filtered_results]
        selected_for_compare = st.multiselect(
            "Select candidates to send to Comparison Matrix (2-5):",
            options=candidate_options,
            default=candidate_options[:min(3, len(candidate_options))]
        )
        if st.button("Save Selection to Comparison Matrix", use_container_width=True):
            selected_objs = []
            for opt in selected_for_compare:
                fname = opt.split("(")[-1].replace(")", "").strip()
                match = next((r for r in filtered_results if r.candidate.source_filename == fname), None)
                if match:
                    selected_objs.append(match)
            st.session_state["selected_comparison_candidates"] = selected_objs
            st.success(f"{len(selected_objs)} candidates staged for comparison. Navigate to 'Candidate Comparison' page.")
