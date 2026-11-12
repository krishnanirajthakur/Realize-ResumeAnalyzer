"""
Single Resume Analysis Workspace View - Realize
"""
import streamlit as st
from core.models import CandidateProfile, JobDescription
from core.parsers.pdf_parser import parse_pdf
from core.parsers.docx_parser import parse_docx
from core.parsers.jd_parser import parse_job_description
from core.preprocessing.text_cleaner import clean_text, extract_contact_info, extract_candidate_name
from core.preprocessing.section_extractor import extract_sections
from core.matching.skill_extractor import extract_skills_from_text, get_skill_matcher
from core.scoring.scoring_engine import CandidateScoringEngine
from ui.components import (
    render_score_capsule, render_skills_chips, render_fit_badge, render_audit_callout
)

def render_resume_analysis_view():
    st.markdown("## Resume Analysis Workspace")
    st.markdown("Deep-dive deterministic evaluation of an individual candidate against a target job requisition.")

    # Input Section: 2 Columns (Resume vs Job Description)
    col_resume, col_jd = st.columns([1, 1])

    with col_resume:
        st.markdown("#### 1. Candidate Resume Source")
        resume_text = ""
        resume_filename = "Uploaded_Resume"
        
        uploaded_file = st.file_uploader(
            "Upload Candidate Resume (PDF or DOCX):",
            type=["pdf", "docx"],
            key="single_resume_uploader",
            help="Upload an authentic candidate resume document in PDF or DOCX format."
        )
        if uploaded_file is not None:
            resume_filename = uploaded_file.name
            try:
                if uploaded_file.name.lower().endswith(".pdf"):
                    resume_text, _ = parse_pdf(uploaded_file)
                else:
                    resume_text, _ = parse_docx(uploaded_file)
                st.success(f"Loaded '{uploaded_file.name}' ({len(resume_text.split())} words extracted)")
            except Exception as e:
                st.error(f"Error parsing resume: {str(e)}")

    with col_jd:
        st.markdown("#### 2. Job Description Benchmark")
        jd_input_method = st.radio("Provide Target Job Description via:", ["Paste JD Text", "Upload JD File (PDF/DOCX/TXT)"], horizontal=True)
        
        jd_text = ""
        if jd_input_method == "Paste JD Text":
            jd_text = st.text_area(
                "Paste Job Description:",
                height=180,
                placeholder="Paste the target job description requirements, responsibilities, and qualifications here..."
            )
        else:
            jd_file = st.file_uploader("Upload JD Document:", type=["pdf", "docx", "txt"], key="single_jd_uploader")
            if jd_file is not None:
                try:
                    if jd_file.name.lower().endswith(".pdf"):
                        jd_text, _ = parse_pdf(jd_file)
                    elif jd_file.name.lower().endswith(".docx"):
                        jd_text, _ = parse_docx(jd_file)
                    else:
                        jd_text = jd_file.read().decode("utf-8", errors="ignore")
                    st.success(f"Loaded '{jd_file.name}'")
                except Exception as e:
                    st.error(f"Error reading JD: {str(e)}")

    if not resume_text or not jd_text:
        st.info("Please upload a Candidate Resume and provide a Job Description above to initiate evaluation.")
        return

    # Interactive Review of Extracted Requirements before analysis
    st.markdown("---")
    with st.expander("🛠️ Review & Modify Extracted Job Requirements (Optional)", expanded=False):
        parsed_jd_preview = parse_job_description(jd_text, extract_skills_from_text)
        
        c_t1, c_t2, c_t3 = st.columns([2, 1, 1])
        with c_t1:
            mod_title = st.text_input("Role Title:", value=parsed_jd_preview.title)
        with c_t2:
            mod_exp = st.number_input("Required Tenure (Years):", value=float(parsed_jd_preview.required_experience_years), min_value=0.0, max_value=25.0, step=0.5)
        with c_t3:
            mod_edu = st.selectbox("Required Degree Level:", ["bachelor", "master", "doctorate", "associate", "unspecified"], index=0)
            
        mod_req_skills = st.multiselect("Mandatory Technical Skills:", options=sorted(list(set(parsed_jd_preview.required_skills + list(get_skill_matcher().skills_by_name.keys())))), default=parsed_jd_preview.required_skills)
        mod_pref_skills = st.multiselect("Preferred / Bonus Skills:", options=sorted(list(set(parsed_jd_preview.preferred_skills + list(get_skill_matcher().skills_by_name.keys())))), default=parsed_jd_preview.preferred_skills)

    # Trigger Evaluation Button
    if st.button("Run Deterministic Candidate Evaluation", type="primary", use_container_width=True):
        with st.spinner("Executing Realize deterministic NLP and scoring engine..."):
            # Construct Final JD
            final_jd = JobDescription(
                jd_id="active_jd",
                title=mod_title,
                raw_text=jd_text,
                clean_text=clean_text(jd_text),
                required_skills=mod_req_skills,
                preferred_skills=mod_pref_skills,
                required_experience_years=mod_exp,
                required_education_level=mod_edu,
                responsibilities=parsed_jd_preview.responsibilities,
                sections=parsed_jd_preview.sections
            )
            st.session_state["active_jd"] = final_jd

            # Parse Candidate Profile
            cand_sections = extract_sections(resume_text)
            cand_email, cand_phone = extract_contact_info(resume_text)
            cand_name = extract_candidate_name(resume_text, resume_filename)
            cand_skills = extract_skills_from_text(resume_text)
            
            profile = CandidateProfile(
                candidate_id=resume_filename,
                source_filename=resume_filename,
                name=cand_name,
                email=cand_email,
                phone=cand_phone,
                raw_text=resume_text,
                clean_text=clean_text(resume_text),
                sections=cand_sections,
                skills=cand_skills
            )

            # Evaluate Candidate
            weights = st.session_state.get("app_config").weights
            engine = CandidateScoringEngine(weights)
            result = engine.evaluate_candidate(profile, final_jd)
            
            st.session_state["active_single_result"] = result
            
            # Save into session history if not already present
            existing_evals = st.session_state.get("evaluations_history", [])
            filtered = [e for e in existing_evals if e.candidate.candidate_id != profile.candidate_id]
            filtered.append(result)
            st.session_state["evaluations_history"] = filtered

    # Render Evaluation Results if available
    result = st.session_state.get("active_single_result")
    if result:
        st.markdown("---")
        
        # Candidate Header Banner
        c_b1, c_b2, c_b3 = st.columns([2, 1, 1])
        with c_b1:
            st.markdown(f"### {result.candidate.name}")
            st.caption(f"Source: `{result.candidate.source_filename}` | Email: {result.candidate.email or 'N/A'} | Phone: {result.candidate.phone or 'N/A'}")
        with c_b2:
            st.markdown("#### Overall Fit")
            st.markdown(render_fit_badge(result.fit_tier), unsafe_allow_html=True)
        with c_b3:
            st.markdown("#### Suitability Index")
            st.markdown(f"<span class='font-mono' style='font-size: 28px; font-weight: 700; color: #4F46E5;'>{result.overall_score}%</span>", unsafe_allow_html=True)

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

        # Factor Breakdown & Skills Matrix Split
        col_meters, col_skills = st.columns([1, 1])
        
        with col_meters:
            st.markdown("##### Explainable Score Breakdown")
            for c_id, comp in result.components.items():
                render_score_capsule(
                    comp.raw_score,
                    f"{comp.name} (Effective Wt: {round(comp.effective_weight*100, 1)}%)"
                )

        with col_skills:
            st.markdown("##### Skills Taxonomy Match Matrix")
            render_skills_chips(
                result.matched_required_skills,
                result.missing_required_skills,
                result.matched_preferred_skills,
                result.additional_skills
            )

        # Detailed Factor Tabs
        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
        tab_sim, tab_exp, tab_edu, tab_proj, tab_audit = st.tabs([
            "Lexical TF-IDF", "Chronological Experience", "Education Alignment", "Project Relevance", "Audit Trail"
        ])

        with tab_sim:
            sim_ev = result.components["text_similarity"].evidence
            st.markdown(f"**TF-IDF Cosine Similarity Coefficient:** `{sim_ev.get('cosine', 0.0)}`")
            st.caption("Measures raw vocabulary and n-gram overlap between sanitized candidate text and target JD.")
            top_terms = sim_ev.get("top_terms", [])
            if top_terms:
                st.markdown("**Top Salient Overlapping Terms:**")
                st.write({term: weight for term, weight in top_terms})
            else:
                st.caption("No significant overlapping n-grams found.")

        with tab_exp:
            exp_ev = result.components["experience"].evidence
            st.markdown(f"**Verified Non-Overlapping Tenure:** `{exp_ev.get('candidate_years', 0.0)} years` (Target: `{exp_ev.get('required_years', 0.0)} years`)")
            st.markdown(f"**Tenure Deficit / Surplus:** `{exp_ev.get('gap_years', 0.0)} years`")
            st.info(exp_ev.get("explanation", ""))
            raw_intervals = exp_ev.get("raw_intervals", [])
            if raw_intervals:
                st.markdown("**Extracted Employment Timeline Intervals:**")
                for interval in raw_intervals:
                    st.markdown(f"- `{interval}`")

        with tab_edu:
            edu_ev = result.components["education"].evidence
            st.markdown(f"**Highest Attained Credential:** `{edu_ev.get('candidate_degree', 'Unspecified')}` (Tier {edu_ev.get('candidate_tier', 0)})")
            st.markdown(f"**Target Role Requirement:** `{edu_ev.get('required_degree', 'Bachelor')}` (Tier {edu_ev.get('required_tier', 3)})")
            st.info(edu_ev.get("explanation", ""))

        with tab_proj:
            proj_ev = result.components["projects"].evidence
            st.markdown(f"**Project Alignment Score:** `{result.components['projects'].raw_score}%`")
            st.info(proj_ev.get("explanation", ""))
            skills_in_proj = proj_ev.get("project_skills_applied", [])
            if skills_in_proj:
                st.markdown(f"**Required Competencies Cited in Projects ({len(skills_in_proj)}):** {', '.join(skills_in_proj)}")

        with tab_audit:
            st.markdown("##### Step-by-Step Mathematical Derivation")
            for log_entry in result.audit_trace:
                st.markdown(f"- `{log_entry}`")

        # Limitations & Warnings Banner
        render_audit_callout(result.limitations, result.confidence_score)
