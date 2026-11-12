"""
Evaluation Reports & Export Center View
"""
import streamlit as st
import pandas as pd
from reporting.pdf_generator import generate_candidate_pdf_report
from reporting.csv_exporter import export_batch_to_csv
from ui.components import render_fit_badge

def render_evaluation_reports_view():
    st.markdown("## Evaluation Reports & Export Center")
    st.markdown("Generate and download enterprise PDF evaluation briefs and structured CSV screening logs.")

    history = st.session_state.get("evaluations_history", [])

    if not history:
        st.info("No candidates evaluated yet in this session. Run an evaluation to generate downloadable reports.")
        return

    col_cand, col_actions = st.columns([2, 1])

    with col_cand:
        st.markdown("#### Select Candidate for PDF Report")
        cand_map = {f"{e.candidate.name} ({e.candidate.source_filename}) - {e.overall_score}%": e for e in history}
        selected_key = st.selectbox("Candidate Profile:", list(cand_map.keys()))
        selected_result = cand_map[selected_key]

    with col_actions:
        st.markdown("#### Quick Export Actions")
        # PDF Generation
        pdf_bytes = generate_candidate_pdf_report(selected_result)
        cand_filename_safe = (selected_result.candidate.name or "candidate").replace(" ", "_").lower()
        st.download_button(
            label="Download Candidate PDF Report",
            data=pdf_bytes,
            file_name=f"resumeiq_report_{cand_filename_safe}.pdf",
            mime="application/pdf",
            type="primary",
            use_container_width=True
        )
        
        # Batch CSV Export
        all_csv = export_batch_to_csv(history)
        st.download_button(
            label="Export All Candidates (CSV)",
            data=all_csv,
            file_name="resumeiq_all_candidates_summary.csv",
            mime="text/csv",
            use_container_width=True
        )

    # Document Preview Card
    st.markdown("---")
    st.markdown("#### Report Executive Summary Preview")

    with st.container():
        st.markdown(f"### {selected_result.candidate.name}")
        st.markdown(f"**Target Role:** {selected_result.job_description.title}")
        
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric("Overall Score", f"{selected_result.overall_score}%")
        with m2:
            st.metric("Fit Classification", selected_result.fit_tier)
        with m3:
            st.metric("Audit Confidence", f"{selected_result.confidence_score}%")
        with m4:
            st.metric("Tenure Gap", f"{selected_result.experience_gap_years} yrs")

        st.markdown("##### Factor Breakdown Table")
        factor_records = []
        for c_id, comp in selected_result.components.items():
            factor_records.append({
                "Component": comp.name,
                "Nominal Weight": f"{round(comp.nominal_weight * 100)}%",
                "Effective Weight": f"{round(comp.effective_weight * 100, 1)}%",
                "Score": f"{round(comp.raw_score, 1)}%",
                "Weighted Contribution": f"{round(comp.weighted_score, 1)}%",
                "Status": "⚠️ Missing Section" if comp.is_missing else "✓ Verified"
            })
        st.dataframe(pd.DataFrame(factor_records), use_container_width=True, hide_index=True)

        st.markdown("##### Skills Alignment Summary")
        st.markdown(f"**Matched Required:** {', '.join(selected_result.matched_required_skills) if selected_result.matched_required_skills else 'None'}")
        st.markdown(f"**Missing Required:** {', '.join(selected_result.missing_required_skills) if selected_result.missing_required_skills else 'None'}")
        st.markdown(f"**Matched Preferred:** {', '.join(selected_result.matched_preferred_skills) if selected_result.matched_preferred_skills else 'None'}")

        if selected_result.limitations:
            st.warning("Audit Notices:\n" + "\n".join([f"- {l}" for l in selected_result.limitations]))
