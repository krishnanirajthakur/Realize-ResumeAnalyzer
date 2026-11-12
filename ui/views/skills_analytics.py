"""
Skills Analytics & Taxonomy Intelligence View
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from core.matching.skill_extractor import get_skill_matcher

def render_skills_analytics_view():
    st.markdown("## Skills Analytics & Taxonomy Intelligence")
    st.markdown("Aggregated skill demand, candidate coverage, and market taxonomy distribution.")

    history = st.session_state.get("evaluations_history", [])
    active_jd = st.session_state.get("active_jd")

    # Taxonomy overview stats
    matcher = get_skill_matcher()
    total_tax_skills = len(matcher.skills_by_name)
    categories = set(info["category"] for info in matcher.skills_by_name.values())

    col_t1, col_t2, col_t3 = st.columns(3)
    with col_t1:
        st.metric("Curated Taxonomy Skills", total_tax_skills)
    with col_t2:
        st.metric("Technical Categories", len(categories))
    with col_t3:
        st.metric("Candidates in Analytics Pool", len(history))

    st.markdown("---")

    if not history:
        st.info("No candidates in the analytics pool yet. Please evaluate resumes to see pool skill analytics.")
        
        # Display taxonomy explorer
        st.markdown("### Configured Skill Taxonomy Explorer")
        cat_filter = st.selectbox("Filter Category:", ["All Categories"] + sorted(list(categories)))
        
        tax_table = []
        for name, meta in matcher.skills_by_name.items():
            if cat_filter == "All Categories" or meta["category"] == cat_filter:
                tax_table.append({
                    "Skill": name,
                    "Category": meta["category"],
                    "Aliases": ", ".join(meta["aliases"]) if meta["aliases"] else "None"
                })
        st.dataframe(pd.DataFrame(tax_table), use_container_width=True, hide_index=True)
        return

    # 1. Pool Skill Gap Analysis against Active JD
    if active_jd and active_jd.required_skills:
        st.markdown(f"#### Skill Coverage for Requisition: *{active_jd.title}*")
        
        req_skills = active_jd.required_skills
        coverage_counts = {s: 0 for s in req_skills}
        for e in history:
            for s in e.matched_required_skills:
                if s in coverage_counts:
                    coverage_counts[s] += 1
                    
        pool_size = max(1, len(history))
        coverage_df = pd.DataFrame([
            {
                "Required Skill": s,
                "Candidates Possessing": count,
                "Pool Coverage Rate (%)": round((count / pool_size) * 100, 1),
                "Scarcity Status": "Critical Gap (<25%)" if (count / pool_size) < 0.25 else ("Moderate Coverage" if (count / pool_size) < 0.7 else "Abundant")
            }
            for s, count in coverage_counts.items()
        ]).sort_values("Candidates Possessing", ascending=True)

        fig_cov = px.bar(
            coverage_df,
            x="Candidates Possessing",
            y="Required Skill",
            orientation='h',
            color="Pool Coverage Rate (%)",
            color_continuous_scale="Viridis",
            labels={"Candidates Possessing": "Candidate Count"},
            text="Pool Coverage Rate (%)"
        )
        fig_cov.update_layout(
            height=320,
            margin=dict(l=20, r=20, t=10, b=20),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig_cov, use_container_width=True)

    # 2. Overall Applicant Pool Skill Frequency
    st.markdown("---")
    st.markdown("#### Most Common Skills in Candidate Pool")
    
    all_pool_skills = [s for e in history for s in e.candidate.skills]
    if all_pool_skills:
        freq = pd.Series(all_pool_skills).value_counts().reset_index()
        freq.columns = ["Skill", "Candidate Count"]
        
        col_c1, col_c2 = st.columns([1, 1])
        with col_c1:
            fig_pie = px.pie(
                freq.head(10),
                names="Skill",
                values="Candidate Count",
                color_discrete_sequence=px.colors.sequential.Indigo
            )
            fig_pie.update_layout(height=300, margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig_pie, use_container_width=True)
            
        with col_c2:
            st.dataframe(freq.head(15), use_container_width=True, hide_index=True)
