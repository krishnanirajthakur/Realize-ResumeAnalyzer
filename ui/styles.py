"""
Realize - Google Stitch Enterprise CSS Styling
"""
import streamlit as st

def apply_custom_css():
    """Inject enterprise CSS styling matching the Google Stitch design tokens."""
    css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

    /* Global Typography & Background */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        color: #0F172A;
    }
    
    .stApp {
        background-color: #F8FAFC;
    }

    /* Monospace telemetry */
    .font-mono, .telemetry, code {
        font-family: 'JetBrains Mono', monospace !important;
        font-variant-numeric: tabular-nums;
    }

    /* KPI Metric Cards */
    .kpi-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 18px 20px;
        box-shadow: 0 1px 2px 0 rgba(15, 23, 42, 0.05);
        margin-bottom: 12px;
        transition: border-color 0.2s ease, box-shadow 0.2s ease;
    }
    .kpi-card:hover {
        border-color: #C7D2FE;
        box-shadow: 0 4px 6px -1px rgba(15, 23, 42, 0.07);
    }
    .kpi-label {
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        color: #64748B;
        margin-bottom: 6px;
    }
    .kpi-value {
        font-size: 28px;
        font-weight: 700;
        color: #0F172A;
        line-height: 1.2;
    }
    .kpi-subtext {
        font-size: 12px;
        color: #64748B;
        margin-top: 6px;
    }

    /* Skill Chips & Badges */
    .badge-matched-req {
        display: inline-block;
        background-color: #EEF2FF;
        color: #4338CA;
        border: 1px solid #C7D2FE;
        padding: 3px 10px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: 500;
        margin: 2px 4px 2px 0;
    }
    .badge-missing-req {
        display: inline-block;
        background-color: #FFF1F2;
        color: #BE123C;
        border: 1px solid #FECDD3;
        padding: 3px 10px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: 500;
        margin: 2px 4px 2px 0;
    }
    .badge-matched-pref {
        display: inline-block;
        background-color: #F0FDFA;
        color: #0F766E;
        border: 1px solid #99F6E4;
        padding: 3px 10px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: 500;
        margin: 2px 4px 2px 0;
    }
    .badge-additional {
        display: inline-block;
        background-color: #F1F5F9;
        color: #475569;
        border: 1px solid #CBD5E1;
        padding: 3px 10px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: 500;
        margin: 2px 4px 2px 0;
    }

    /* Fit Tier Badges */
    .tier-strong {
        background-color: #F0FDFA;
        color: #0F766E;
        border: 1px solid #99F6E4;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 12px;
        font-weight: 600;
    }
    .tier-moderate {
        background-color: #EEF2FF;
        color: #4338CA;
        border: 1px solid #C7D2FE;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 12px;
        font-weight: 600;
    }
    .tier-partial {
        background-color: #FEF3C7;
        color: #B45309;
        border: 1px solid #FDE68A;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 12px;
        font-weight: 600;
    }
    .tier-limited {
        background-color: #F1F5F9;
        color: #475569;
        border: 1px solid #E2E8F0;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 12px;
        font-weight: 600;
    }

    /* Enterprise White Panel Container */
    .stitch-panel {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 18px;
        box-shadow: 0 1px 2px 0 rgba(15, 23, 42, 0.05);
    }
    .panel-title {
        font-size: 16px;
        font-weight: 600;
        color: #0F172A;
        margin-bottom: 12px;
    }

    /* Progress Capsule */
    .capsule-track {
        background-color: #E2E8F0;
        border-radius: 4px;
        height: 8px;
        width: 100%;
        overflow: hidden;
        margin: 6px 0;
    }
    .capsule-fill {
        height: 100%;
        border-radius: 4px;
    }

    /* Buttons */
    button[kind="primary"] {
        background-color: #4F46E5 !important;
        color: #FFFFFF !important;
        border-radius: 4px !important;
        font-weight: 600 !important;
        border: none !important;
    }
    button[kind="primary"]:hover {
        background-color: #4338CA !important;
    }

    /* Persistent Sidebar Customization */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E2E8F0;
    }
    section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2 {
        font-size: 18px !important;
        color: #0F172A !important;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
