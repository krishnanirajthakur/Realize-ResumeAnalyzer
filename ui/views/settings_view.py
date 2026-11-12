"""
System Settings and Parameter Configuration View
"""
import streamlit as st
import json
import os
from config.settings import DEFAULT_WEIGHTS, AppConfig, TAXONOMY_PATH
from core.matching.skill_extractor import get_skill_matcher

def render_settings_view():
    st.markdown("## System Configuration & Parameters")
    st.markdown("Customize scoring weight allocations, skill taxonomy definitions, and evaluation thresholds.")

    app_config: AppConfig = st.session_state.get("app_config")
    
    # 1. Scoring Weights Configuration
    st.markdown("#### 1. Candidate Scoring Engine Weights")
    st.caption("Adjust the contribution of each evaluation component. The total sum must strictly equal 100%.")

    current_weights = app_config.weights.copy()
    
    col_w1, col_w2 = st.columns(2)
    with col_w1:
        w_skills = st.slider("Mandatory Skills Match Weight (%):", 0, 100, int(current_weights["skill_match"]))
        w_sim = st.slider("TF-IDF Lexical Similarity Weight (%):", 0, 100, int(current_weights["text_similarity"]))
        w_exp = st.slider("Chronological Experience Weight (%):", 0, 100, int(current_weights["experience"]))
    with col_w2:
        w_edu = st.slider("Educational Level Weight (%):", 0, 100, int(current_weights["education"]))
        w_proj = st.slider("Project Relevance Weight (%):", 0, 100, int(current_weights["projects"]))
        w_addl = st.slider("Preferred & Additional Skills Weight (%):", 0, 100, int(current_weights["additional_skills"]))

    total_weight = w_skills + w_sim + w_exp + w_edu + w_proj + w_addl
    
    if total_weight == 100:
        st.success(f"✓ Total Weight: **{total_weight}%** (Valid)")
    else:
        st.error(f"⚠️ Total Weight: **{total_weight}%** (Must equal exactly 100%. Deficit/Surplus: {100 - total_weight}%)")

    col_btn1, col_btn2 = st.columns([1, 1])
    with col_btn1:
        if st.button("Save Scoring Weights", type="primary", disabled=(total_weight != 100), use_container_width=True):
            app_config.weights = {
                "skill_match": float(w_skills),
                "text_similarity": float(w_sim),
                "experience": float(w_exp),
                "education": float(w_edu),
                "projects": float(w_proj),
                "additional_skills": float(w_addl),
            }
            st.session_state["app_config"] = app_config
            st.success("Scoring weights successfully updated and persisted for session.")
            st.rerun()

    with col_btn2:
        if st.button("Reset Weights to System Defaults", use_container_width=True):
            app_config.weights = DEFAULT_WEIGHTS.copy()
            st.session_state["app_config"] = app_config
            st.success("Weights restored to default settings.")
            st.rerun()

    # 2. Skill Taxonomy Extension
    st.markdown("---")
    st.markdown("#### 2. Skill Taxonomy Management")
    st.caption("Extend the curated taxonomy with custom domain-specific competencies and aliases.")

    matcher = get_skill_matcher()

    with st.expander("➕ Add New Skill to Taxonomy", expanded=False):
        c_s1, c_s2 = st.columns(2)
        with c_s1:
            new_skill_name = st.text_input("Canonical Skill Name (e.g. 'GraphQL'):")
            new_skill_cat = st.selectbox(
                "Category:",
                [
                    "Programming Languages", "Web & Frontend", "Backend Frameworks",
                    "Databases & Storage", "Cloud & Infrastructure", "DevOps & Containers",
                    "Data Science & Classical ML", "Big Data Engineering", "Testing & QA",
                    "Developer Tools", "Business Intelligence & Analytics", "Methodologies"
                ]
            )
        with c_s2:
            new_skill_aliases = st.text_input("Comma-Separated Aliases (e.g. 'apollo, gql'):")

        if st.button("Add Skill to Curated Taxonomy", use_container_width=True):
            if new_skill_name:
                aliases_list = [a.strip() for a in new_skill_aliases.split(",") if a.strip()]
                # Load current taxonomy
                if os.path.exists(TAXONOMY_PATH):
                    with open(TAXONOMY_PATH, "r", encoding="utf-8") as f:
                        tax_data = json.load(f)
                else:
                    tax_data = {"skills": []}
                    
                # Check if exists
                existing_names = [s["name"].lower() for s in tax_data["skills"]]
                if new_skill_name.lower() in existing_names:
                    st.warning(f"Skill '{new_skill_name}' already exists in taxonomy.")
                else:
                    tax_data["skills"].append({
                        "name": new_skill_name,
                        "category": new_skill_cat,
                        "aliases": aliases_list
                    })
                    with open(TAXONOMY_PATH, "w", encoding="utf-8") as f:
                        json.dump(tax_data, f, indent=2)
                    matcher.load_taxonomy()
                    st.success(f"Added '{new_skill_name}' to taxonomy!")
                    st.rerun()

    # 3. Privacy & Compliance Policies
    st.markdown("---")
    st.markdown("#### 3. Privacy, Fairness & Algorithmic Guardrails")
    st.markdown(
        """
        - **Zero Demographic Scoring**: Candidate attributes such as race, gender, age, nationality, address, and profile pictures are completely absent from scoring formulas.
        - **Decision-Support Architecture**: ResumeIQ provides transparent mathematical ranking indicators; candidates are never automatically disqualified or rejected.
        - **Zero Generative AI**: All algorithms are deterministic, auditable, and locally executed.
        """
    )
