"""
ResumeIQ - Resume & Candidate Analysis System
Enterprise Streamlit Application Entry Point
"""
import streamlit as st
import os
import sys

# Ensure root directory is on Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.settings import AppConfig
from ui.styles import apply_custom_css
from ui.views import (
    render_dashboard_view,
    render_resume_analysis_view,
    render_bulk_screening_view,
    render_candidate_comparison_view,
    render_skills_analytics_view,
    render_evaluation_reports_view,
    render_model_evaluation_view,
    render_settings_view
)

def init_session_state():
    """Initialize persistent Streamlit session state."""
    if "app_config" not in st.session_state:
        st.session_state["app_config"] = AppConfig()
    if "evaluations_history" not in st.session_state:
        st.session_state["evaluations_history"] = []
    if "active_jd" not in st.session_state:
        st.session_state["active_jd"] = None
    if "active_single_result" not in st.session_state:
        st.session_state["active_single_result"] = None
    if "selected_comparison_candidates" not in st.session_state:
        st.session_state["selected_comparison_candidates"] = []

def main():
    # Streamlit Page Setup
    st.set_page_config(
        page_title="ResumeIQ - Candidate & Resume Analysis System",
        page_icon="🎯",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Apply Google Stitch CSS Design Tokens
    apply_custom_css()
    init_session_state()

    # Enterprise Sidebar Navigation
    with st.sidebar:
        st.markdown(
            """
            <div style="padding: 10px 0 16px 0; border-bottom: 1px solid #E2E8F0;">
                <div style="font-size: 20px; font-weight: 700; color: #4F46E5; letter-spacing: -0.02em;">
                    ResumeIQ
                </div>
                <div style="font-size: 11px; color: #64748B; font-weight: 500;">
                    Talent Intelligence & Candidate Analysis
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

        pages = [
            "Executive Dashboard",
            "Resume Analysis Workspace",
            "Bulk Screening & Ranking",
            "Candidate Comparison Matrix",
            "Skills Analytics & Taxonomy",
            "Evaluation Reports (PDF/CSV)",
            "Dataset & Model Evaluation",
            "Settings & Parameters"
        ]

        icons = {
            "Executive Dashboard": "📊",
            "Resume Analysis Workspace": "🔍",
            "Bulk Screening & Ranking": "📁",
            "Candidate Comparison Matrix": "⚖️",
            "Skills Analytics & Taxonomy": "🧠",
            "Evaluation Reports (PDF/CSV)": "📑",
            "Dataset & Model Evaluation": "📈",
            "Settings & Parameters": "⚙️"
        }

        selected_page = st.radio(
            "System Navigation:",
            pages,
            format_func=lambda x: f"{icons[x]}  {x}",
            label_visibility="collapsed"
        )

        st.markdown("---")
        
        # Session Telemetry Pill
        history = st.session_state.get("evaluations_history", [])
        active_jd = st.session_state.get("active_jd")
        
        st.markdown(
            f"""
            <div style="font-size: 11px; color: #64748B; line-height: 1.6;">
                <div><b>Session Pool:</b> <span class="font-mono">{len(history)} candidates</span></div>
                <div><b>Benchmark Role:</b> {active_jd.title if active_jd else 'Not Loaded'}</div>
                <div style="margin-top: 8px; color: #0D9488; font-weight: 600;">✓ Classical ML (Zero-AI)</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Route to Selected Page
    if selected_page == "Executive Dashboard":
        render_dashboard_view()
    elif selected_page == "Resume Analysis Workspace":
        render_resume_analysis_view()
    elif selected_page == "Bulk Screening & Ranking":
        render_bulk_screening_view()
    elif selected_page == "Candidate Comparison Matrix":
        render_candidate_comparison_view()
    elif selected_page == "Skills Analytics & Taxonomy":
        render_skills_analytics_view()
    elif selected_page == "Evaluation Reports (PDF/CSV)":
        render_evaluation_reports_view()
    elif selected_page == "Dataset & Model Evaluation":
        render_model_evaluation_view()
    elif selected_page == "Settings & Parameters":
        render_settings_view()

if __name__ == "__main__":
    main()
