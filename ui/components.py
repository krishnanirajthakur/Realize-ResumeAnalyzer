"""
Reusable Streamlit UI Components matching Google Stitch Design
"""
import streamlit as st
import plotly.graph_objects as go
from typing import List, Dict, Any, Optional

def render_kpi_card(label: str, value: str, subtext: str = "", delta_type: str = "neutral"):
    """Render a Google Stitch enterprise KPI card."""
    delta_color = "#0D9488" if delta_type == "positive" else ("#E11D48" if delta_type == "negative" else "#64748B")
    html = f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value font-mono">{value}</div>
        <div class="kpi-subtext" style="color: {delta_color};">{subtext}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def render_fit_badge(tier: str) -> str:
    """Return HTML for a fit tier badge."""
    t_lower = tier.lower()
    if "strong" in t_lower:
        return f'<span class="tier-strong">● {tier}</span>'
    elif "moderate" in t_lower:
        return f'<span class="tier-moderate">● {tier}</span>'
    elif "partial" in t_lower:
        return f'<span class="tier-partial">▲ {tier}</span>'
    else:
        return f'<span class="tier-limited">■ {tier}</span>'

def render_score_capsule(score: float, label: str = ""):
    """Render a progress capsule with color mapped to score tier."""
    if score >= 80:
        fill_color = "#0D9488" # Teal
    elif score >= 65:
        fill_color = "#4F46E5" # Indigo
    elif score >= 50:
        fill_color = "#D97706" # Amber
    else:
        fill_color = "#E11D48" # Rose
        
    html = f"""
    <div style="margin-bottom: 8px;">
        <div style="display: flex; justify-content: space-between; font-size: 13px; font-weight: 500;">
            <span style="color: #334155;">{label}</span>
            <span class="font-mono" style="font-weight: 600; color: #0F172A;">{score}%</span>
        </div>
        <div class="capsule-track">
            <div class="capsule-fill" style="width: {min(100.0, max(0.0, score))}%; background-color: {fill_color};"></div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def render_skills_chips(
    matched_req: List[str], missing_req: List[str], matched_pref: List[str], additional: List[str]
):
    """Render structured skill badge chips by category."""
    st.markdown("##### Mandatory Requirements")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Matched Required ({len(matched_req)})**")
        if matched_req:
            chips = "".join([f'<span class="badge-matched-req">✓ {s}</span>' for s in matched_req])
            st.markdown(chips, unsafe_allow_html=True)
        else:
            st.caption("No required skills matched.")
            
    with col2:
        st.markdown(f"**Missing Required ({len(missing_req)})**")
        if missing_req:
            chips = "".join([f'<span class="badge-missing-req">✕ {s}</span>' for s in missing_req])
            st.markdown(chips, unsafe_allow_html=True)
        else:
            st.caption("None (100% Required Skill Coverage)")
            
    st.markdown("---")
    st.markdown("##### Secondary & Additional Competencies")
    col3, col4 = st.columns(2)
    with col3:
        st.markdown(f"**Matched Preferred ({len(matched_pref)})**")
        if matched_pref:
            chips = "".join([f'<span class="badge-matched-pref">+ {s}</span>' for s in matched_pref])
            st.markdown(chips, unsafe_allow_html=True)
        else:
            st.caption("No preferred skills matched or listed in JD.")
            
    with col4:
        st.markdown(f"**Additional Skills ({len(additional)})**")
        if additional:
            chips = "".join([f'<span class="badge-additional">{s}</span>' for s in additional[:15]])
            st.markdown(chips, unsafe_allow_html=True)
        else:
            st.caption("No additional tools detected.")

def create_radar_chart(candidates_data: List[Dict[str, Any]], categories: List[str]) -> go.Figure:
    """Create a multi-candidate 6-axis competency radar chart in Plotly."""
    fig = go.Figure()
    palette = ["#4F46E5", "#0D9488", "#D97706", "#7C3AED", "#DB2777"]
    
    for idx, cand in enumerate(candidates_data):
        color = palette[idx % len(palette)]
        values = [cand.get(cat, 0.0) for cat in categories]
        # Close polygon
        values.append(values[0])
        closed_cats = categories + [categories[0]]
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=closed_cats,
            name=cand.get("name", f"Candidate {idx+1}"),
            line=dict(color=color, width=2),
            fill='toself',
            fillcolor=f"rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, 0.15)"
        ))
        
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], tickfont=dict(size=10, family="JetBrains Mono")),
            angularaxis=dict(tickfont=dict(size=11, family="Inter", color="#334155"))
        ),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
        margin=dict(l=40, r=40, t=20, b=40),
        height=380,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    return fig

def create_factor_bar_chart(candidates_data: List[Dict[str, Any]], factors: List[str]) -> go.Figure:
    """Create grouped bar chart comparing factor scores across applicants."""
    fig = go.Figure()
    palette = ["#4F46E5", "#0D9488", "#D97706", "#7C3AED", "#DB2777"]
    
    for idx, cand in enumerate(candidates_data):
        color = palette[idx % len(palette)]
        scores = [cand.get(f, 0.0) for f in factors]
        fig.add_trace(go.Bar(
            name=cand.get("name", f"Candidate {idx+1}"),
            x=factors,
            y=scores,
            marker_color=color
        ))
        
    fig.update_layout(
        barmode='group',
        yaxis=dict(range=[0, 100], title="Score (%)", tickfont=dict(family="JetBrains Mono")),
        xaxis=dict(tickfont=dict(size=11, family="Inter")),
        margin=dict(l=20, r=20, t=20, b=40),
        height=320,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    return fig

def render_audit_callout(limitations: List[str], confidence: float):
    """Render an explainable audit & limitations callout banner."""
    conf_color = "#0D9488" if confidence >= 80 else ("#D97706" if confidence >= 60 else "#E11D48")
    lim_html = "".join([f"<li>{l}</li>" for l in limitations]) if limitations else "<li>Complete document sections identified; nominal weight distribution applied.</li>"
    
    html = f"""
    <div style="background-color: #FEF3C7; border: 1px solid #FDE68A; border-radius: 6px; padding: 14px 18px; margin-top: 16px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
            <span style="font-weight: 600; color: #92400E; font-size: 13px;">Audit & Explainability Log</span>
            <span class="font-mono" style="font-size: 12px; font-weight: 600; color: {conf_color};">Confidence: {confidence}%</span>
        </div>
        <ul style="font-size: 12px; color: #78350F; margin: 0; padding-left: 18px;">
            {lim_html}
        </ul>
        <div style="font-size: 11px; color: #92400E; margin-top: 8px;">
            <em>Note: Realize is a deterministic decision-support tool. It does not auto-reject applicants.</em>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
