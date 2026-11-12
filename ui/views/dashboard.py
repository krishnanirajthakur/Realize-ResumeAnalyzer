"""
Executive Analytics Dashboard View
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from ui.components import render_kpi_card, render_fit_badge

def render_dashboard_view():
    """Render the executive analytics overview."""
    st.markdown("## Executive Analytics Dashboard")
    st.markdown("Real-time telemetry and candidate distribution across parsed requisitions.")

    evaluations = st.session_state.get("evaluations_history", [])
    
    # Calculate KPIs
    total_candidates = len(evaluations)
    avg_score = round(sum(e.overall_score for e in evaluations) / total_candidates, 1) if total_candidates > 0 else 0.0
    jds_processed = len(set(e.job_description.jd_id for e in evaluations)) if total_candidates > 0 else 0
    flagged_candidates = sum(1 for e in evaluations if len(e.limitations) > 0 or e.confidence_score < 70)

    # 1. Executive Metric KPI Grid
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi_card("Candidates Analysed", str(total_candidates), "Total parsed in session", "neutral")
    with c2:
        delta_type = "positive" if avg_score >= 70 else ("neutral" if avg_score >= 50 else "negative")
        render_kpi_card("Avg Suitability Score", f"{avg_score}%", "Linear weighted index", delta_type)
    with c3:
        render_kpi_card("Active Requisitions", str(max(1, jds_processed)), "Target job profiles", "neutral")
    with c4:
        delta_type = "negative" if flagged_candidates > 0 else "positive"
        render_kpi_card("Requiring Human Review", str(flagged_candidates), "Audit flags / partial data", delta_type)

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    if not evaluations:
        st.info("No candidates evaluated yet in this session. Navigate to 'Resume Analysis' or 'Bulk Screening' to evaluate candidates.")
        
        # Option to load demonstration data
        if st.button("Load Demonstration Applicant Pool (4 Candidates)"):
            with st.spinner("Processing sample candidates against Senior Python & ML Engineer requisition..."):
                from core.parsers.jd_parser import parse_job_description
                from core.parsers.pdf_parser import parse_pdf
                from core.preprocessing.text_cleaner import extract_contact_info, extract_candidate_name
                from core.preprocessing.section_extractor import extract_sections
                from core.matching.skill_extractor import extract_skills_from_text
                from core.scoring.scoring_engine import CandidateScoringEngine
                from core.models import CandidateProfile
                import glob, os

                # Load Sample JD
                jd_path = "data/sample_jds/senior_python_engineer.txt"
                with open(jd_path, "r", encoding="utf-8") as f:
                    jd_raw = f.read()
                jd = parse_job_description(jd_raw, extract_skills_from_text)
                st.session_state["active_jd"] = jd

                engine = CandidateScoringEngine(st.session_state.get("app_config").weights)
                new_evals = []

                # Evaluate sample PDFs
                for pdf_file in glob.glob("data/sample_resumes/*.pdf"):
                    fname = os.path.basename(pdf_file)
                    text, _ = parse_pdf(pdf_file)
                    sections = extract_sections(text)
                    email, phone = extract_contact_info(text)
                    cand_name = extract_candidate_name(text, fname)
                    cand_skills = extract_skills_from_text(text)
                    
                    profile = CandidateProfile(
                        candidate_id=fname,
                        source_filename=fname,
                        name=cand_name,
                        email=email,
                        phone=phone,
                        raw_text=text,
                        clean_text=text,
                        sections=sections,
                        skills=cand_skills
                    )
                    res = engine.evaluate_candidate(profile, jd)
                    new_evals.append(res)

                st.session_state["evaluations_history"] = new_evals
                st.rerun()
        return

    # Visualizations Row
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown("##### Candidate Suitability Score Distribution")
        scores = [e.overall_score for e in evaluations]
        fig_hist = px.histogram(
            x=scores,
            nbins=10,
            range_x=[0, 100],
            labels={"x": "Overall Suitability Score (%)", "y": "Number of Candidates"},
            color_discrete_sequence=["#4F46E5"]
        )
        fig_hist.update_layout(
            height=280,
            margin=dict(l=20, r=20, t=10, b=30),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig_hist, use_container_width=True)

    with col_right:
        st.markdown("##### Applicant Pool Skill Frequency (Top 8)")
        all_skills = [s for e in evaluations for s in e.candidate.skills]
        if all_skills:
            skill_counts = pd.Series(all_skills).value_counts().head(8).reset_index()
            skill_counts.columns = ["Skill", "Frequency"]
            fig_bar = px.bar(
                skill_counts,
                x="Frequency",
                y="Skill",
                orientation='h',
                color_discrete_sequence=["#0D9488"]
            )
            fig_bar.update_layout(
                yaxis=dict(autorange="reversed"),
                height=280,
                margin=dict(l=20, r=20, t=10, b=30),
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(fig_bar, use_container_width=True)

    # Recent Candidates Table
    st.markdown("---")
    st.markdown("##### Recent Candidate Analyses")
    
    table_records = []
    for idx, e in enumerate(evaluations, start=1):
        table_records.append({
            "Rank": idx,
            "Candidate Name": e.candidate.name or "Candidate",
            "File": e.candidate.source_filename,
            "Suitability Score": f"{e.overall_score}%",
            "Fit Tier": e.fit_tier,
            "Skill Match": f"{round(e.components['skill_match'].raw_score, 1)}%",
            "Tenure": f"{e.candidate.experience_years} yrs",
            "Confidence": f"{e.confidence_score}%",
            "Status": "⚠️ Review Required" if len(e.limitations) > 0 else "✓ Verified"
        })
        
    df_table = pd.DataFrame(table_records)
    st.dataframe(df_table, use_container_width=True, hide_index=True)
