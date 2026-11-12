"""
Executive Analytics Dashboard View - Realize
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from ui.components import render_kpi_card, render_fit_badge

def render_dashboard_view():
    """Render the executive analytics overview."""
    st.markdown("## Executive Analytics Dashboard")
    st.markdown("Real-time telemetry and candidate distribution across parsed requisitions in **Realize**.")

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
        render_kpi_card("Active Requisitions", str(max(0, jds_processed)), "Target job profiles", "neutral")
    with c4:
        delta_type = "negative" if flagged_candidates > 0 else "positive"
        render_kpi_card("Requiring Human Review", str(flagged_candidates), "Audit flags / partial data", delta_type)

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    if not evaluations:
        st.info("No candidate resumes evaluated yet in this active session.")
        st.markdown(
            """
            <div style="background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px; padding: 28px; text-align: center; margin-top: 16px;">
                <div style="font-size: 18px; font-weight: 600; color: #0F172A; margin-bottom: 8px;">
                    Welcome to Realize
                </div>
                <div style="font-size: 13px; color: #64748B; max-width: 560px; margin: 0 auto 16px auto; line-height: 1.6;">
                    Upload resumes and benchmark Job Descriptions to compute transparent candidate suitability indicators,
                    identify verified competencies, evaluate tenure gaps, and export audit-ready reports.
                </div>
                <div style="font-size: 12px; color: #4F46E5; font-weight: 500;">
                    Select <b>Resume Analysis Workspace</b> for individual candidate screening, or <b>Bulk Screening & Ranking</b> to process multiple documents.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
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
