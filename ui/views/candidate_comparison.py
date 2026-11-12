"""
Candidate Comparison Matrix View
"""
import streamlit as st
import pandas as pd
from ui.components import create_radar_chart, create_factor_bar_chart, render_fit_badge

def render_candidate_comparison_view():
    st.markdown("## Candidate Comparison Matrix")
    st.markdown("Multi-applicant side-by-side competency radar, factor attribution, and granular qualification comparison.")

    history = st.session_state.get("evaluations_history", [])
    selected_cands = st.session_state.get("selected_comparison_candidates", [])

    if len(history) < 2 and len(selected_cands) < 2:
        st.info("At least 2 evaluated candidates are required for comparison. Please run evaluations on the 'Resume Analysis' or 'Bulk Screening' pages.")
        return

    # Candidate Selection UI
    options_map = {f"{e.candidate.name} ({e.candidate.source_filename}) - {e.overall_score}%": e for e in history}
    
    default_keys = []
    if selected_cands:
        for sc in selected_cands:
            for k, v in options_map.items():
                if v.candidate.candidate_id == sc.candidate.candidate_id:
                    default_keys.append(k)
                    break
    else:
        default_keys = list(options_map.keys())[:min(3, len(options_map))]

    selected_keys = st.multiselect(
        "Choose 2 to 5 Candidates to Compare:",
        options=list(options_map.keys()),
        default=default_keys
    )

    if len(selected_keys) < 2:
        st.warning("Please select at least 2 candidates to generate side-by-side comparison telemetry.")
        return
    elif len(selected_keys) > 5:
        st.warning("Please select at most 5 candidates for optimal readability.")
        selected_keys = selected_keys[:5]

    candidates_to_compare = [options_map[k] for k in selected_keys]

    # Prepare Data for Visualizations
    categories = ["Skills", "Similarity", "Experience", "Education", "Projects", "Preferred"]
    cand_chart_data = []
    
    for c in candidates_to_compare:
        cand_chart_data.append({
            "name": c.candidate.name or "Candidate",
            "Skills": c.components["skill_match"].raw_score,
            "Similarity": c.components["text_similarity"].raw_score,
            "Experience": c.components["experience"].raw_score,
            "Education": c.components["education"].raw_score,
            "Projects": c.components["projects"].raw_score,
            "Preferred": c.components["additional_skills"].raw_score,
            "Overall": c.overall_score
        })

    st.markdown("---")
    
    # Visual Comparison Split
    col_radar, col_bar = st.columns([1, 1])
    
    with col_radar:
        st.markdown("##### 6-Axis Competency Coverage")
        st.caption("Normalized multidimensional fit profiles across core assessment factors.")
        radar_fig = create_radar_chart(cand_chart_data, categories)
        st.plotly_chart(radar_fig, use_container_width=True)

    with col_bar:
        st.markdown("##### Factor Attribution Across Applicants")
        st.caption("Direct factor score comparison across selected applicants.")
        bar_fig = create_factor_bar_chart(cand_chart_data, categories)
        st.plotly_chart(bar_fig, use_container_width=True)

    # Granular Side-by-Side Comparison Table
    st.markdown("---")
    st.markdown("##### Granular Attribute Comparison Matrix")

    # Build attribute comparison columns
    matrix_rows = [
        {"Attribute": "Overall Suitability Score"},
        {"Attribute": "Advisory Fit Tier"},
        {"Attribute": "Assessment Confidence"},
        {"Attribute": "Mandatory Skills Match (%)"},
        {"Attribute": "Matched Mandatory Skills"},
        {"Attribute": "Missing Mandatory Skills"},
        {"Attribute": "Verified Non-Overlapping Experience"},
        {"Attribute": "Experience Gap vs JD"},
        {"Attribute": "Highest Attained Education"},
        {"Attribute": "Field / Major Alignment"},
        {"Attribute": "Lexical Cosine Similarity (%)"},
        {"Attribute": "Project Relevance (%)"},
        {"Attribute": "Source File"}
    ]

    for cand in candidates_to_compare:
        c_name = cand.candidate.name or "Candidate"
        matrix_rows[0][c_name] = f"{cand.overall_score}%"
        matrix_rows[1][c_name] = cand.fit_tier
        matrix_rows[2][c_name] = f"{cand.confidence_score}%"
        matrix_rows[3][c_name] = f"{round(cand.components['skill_match'].raw_score, 1)}%"
        matrix_rows[4][c_name] = ", ".join(cand.matched_required_skills) if cand.matched_required_skills else "None"
        matrix_rows[5][c_name] = ", ".join(cand.missing_required_skills) if cand.missing_required_skills else "None"
        matrix_rows[6][c_name] = f"{cand.candidate.experience_years} years"
        matrix_rows[7][c_name] = f"{cand.experience_gap_years} years"
        matrix_rows[8][c_name] = cand.candidate.education_level
        matrix_rows[9][c_name] = cand.candidate.education_field or "N/A"
        matrix_rows[10][c_name] = f"{round(cand.components['text_similarity'].raw_score, 1)}%"
        matrix_rows[11][c_name] = f"{round(cand.components['projects'].raw_score, 1)}%"
        matrix_rows[12][c_name] = cand.candidate.source_filename

    df_matrix = pd.DataFrame(matrix_rows)
    st.dataframe(df_matrix, use_container_width=True, hide_index=True)
