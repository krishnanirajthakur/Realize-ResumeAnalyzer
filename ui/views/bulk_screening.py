"""
Bulk Resume Screening & Ranking View
"""
import streamlit as st
import pandas as pd
import os
import glob
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
    
    col_j1, col_j2 = st.columns([2, 1])
    with col_j1:
        if active_jd:
            st.success(f"Current Benchmark: **{active_jd.title}** ({len(active_jd.required_skills)} required skills, {active_jd.required_experience_years} yrs exp)")
        else:
            st.warning("No benchmark job description loaded yet.")
            
    with col_j2:
        if st.button("Reload Sample Benchmark JD", use_container_width=True):
            jd_path = "data/sample_jds/senior_python_engineer.txt"
            with open(jd_path, "r", encoding="utf-8") as f:
                jd_raw = f.read()
            st.session_state["active_jd"] = parse_job_description(jd_raw, extract_skills_from_text)
            st.rerun()

    active_jd = st.session_state.get("active_jd")
    if not active_jd:
        st.info("Please load or select a target Job Description before processing resumes in bulk.")
        return

    # File Ingestion Section
    st.markdown("---")
    st.markdown("#### 2. Candidate Document Ingestion")
    
    upload_tab, sample_tab = st.tabs(["Upload Batch Files (PDF / DOCX)", "Process Sample Applicant Repository"])
    
    batch_files_to_process = []
    
    with upload_tab:
        uploaded_files = st.file_uploader(
            "Select multiple PDF or DOCX resumes:",
            type=["pdf", "docx"],
            accept_multiple_files=True,
            key="bulk_file_uploader"
        )
        if uploaded_files:
            batch_files_to_process = [(f.name, f) for f in uploaded_files]
            st.caption(f"{len(uploaded_files)} files staged for processing.")

    with sample_tab:
        sample_paths = glob.glob("data/sample_resumes/*.pdf") + glob.glob("data/sample_resumes/*.docx")
        st.write(f"Bundled demonstration resumes available: **{len(sample_paths)} files**")
        if st.button("Stage All Sample Resumes for Evaluation", use_container_width=True):
            batch_files_to_process = [(os.path.basename(p), p) for p in sample_paths]
            st.session_state["staged_sample_batch"] = batch_files_to_process
            st.success(f"Staged {len(batch_files_to_process)} sample resumes.")

    if not batch_files_to_process and "staged_sample_batch" in st.session_state:
        batch_files_to_process = st.session_state["staged_sample_batch"]

    # Start Batch Evaluation
    if batch_files_to_process:
        if st.button(f"Process Batch ({len(batch_files_to_process)} Resumes)", type="primary", use_container_width=True):
            progress_bar = st.progress(0.0)
            status_text = st.empty()
            
            engine = CandidateScoringEngine(st.session_state.get("app_config").weights)
            batch_results = []
            failed_files = []

            for idx, (fname, file_item) in enumerate(batch_files_to_process):
                status_text.text(f"Evaluating ({idx+1}/{len(batch_files_to_process)}): {fname}...")
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
                    
                progress_bar.progress((idx + 1) / len(batch_files_to_process))

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
        search_query = st.text_input("Filter Candidates by Name or Skill:", placeholder="Search e.g. Python, Docker, Elena...")
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
            file_name=f"resumeiq_batch_{active_jd.title.replace(' ', '_').lower()}.csv",
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
