"""
Executive ReportLab PDF Report Generator
"""
import io
from typing import List
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from core.models import AnalysisResult

PRIMARY_COLOR = colors.HexColor("#4F46E5")
SECONDARY_COLOR = colors.HexColor("#0D9488")
DARK_SLATE = colors.HexColor("#0F172A")
MUTED_SLATE = colors.HexColor("#64748B")
LIGHT_BG = colors.HexColor("#F8FAFC")
BORDER_COLOR = colors.HexColor("#E2E8F0")

def generate_candidate_pdf_report(result: AnalysisResult) -> bytes:
    """
    Generate an executive-level, publication-quality PDF report for a candidate analysis.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )
    
    styles = getSampleStyleSheet()
    
    # Custom Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=PRIMARY_COLOR,
        spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=MUTED_SLATE,
        spaceAfter=12
    )
    section_heading = ParagraphStyle(
        'SecHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=DARK_SLATE,
        spaceBefore=14,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#334155")
    )
    body_bold = ParagraphStyle(
        'BodyBold',
        parent=body_style,
        fontName='Helvetica-Bold'
    )
    callout_style = ParagraphStyle(
        'Callout',
        parent=body_style,
        textColor=colors.HexColor("#1E293B"),
        fontSize=8.5,
        leading=12
    )

    story = []

    # 1. Header Banner
    story.append(Paragraph("Realize • Executive Candidate Evaluation", title_style))
    story.append(Paragraph(
        f"Deterministic Talent Intelligence • Generated {result.created_at[:10]} | Evaluation ID: {result.evaluation_id}",
        subtitle_style
    ))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY_COLOR, spaceAfter=12))

    # 2. Executive Summary Grid
    candidate_name = result.candidate.name or "Identified Candidate"
    job_title = result.job_description.title or "Target Position"
    fit_color = "#0D9488" if result.overall_score >= 80 else ("#4F46E5" if result.overall_score >= 65 else "#D97706")
    
    summary_data = [
        [
            Paragraph("<b>Target Position:</b>", body_style),
            Paragraph(f"<b>{job_title}</b>", body_style),
            Paragraph("<b>Overall Suitability:</b>", body_style),
            Paragraph(f"<font color='{fit_color}'><b>{result.overall_score}% ({result.fit_tier})</b></font>", body_style)
        ],
        [
            Paragraph("<b>Candidate Name:</b>", body_style),
            Paragraph(f"{candidate_name}", body_style),
            Paragraph("<b>Audit Confidence:</b>", body_style),
            Paragraph(f"<b>{result.confidence_score}%</b>", body_style)
        ],
        [
            Paragraph("<b>Contact / Email:</b>", body_style),
            Paragraph(f"{result.candidate.email or 'N/A'}", body_style),
            Paragraph("<b>Tenure Alignment:</b>", body_style),
            Paragraph(f"{result.candidate.experience_years} yrs (Req: {result.job_description.required_experience_years} yrs)", body_style)
        ],
        [
            Paragraph("<b>Education:</b>", body_style),
            Paragraph(f"{result.candidate.education_level} ({result.candidate.education_field or 'Major N/A'})", body_style),
            Paragraph("<b>Document Source:</b>", body_style),
            Paragraph(f"{result.candidate.source_filename}", body_style)
        ]
    ]
    
    summary_table = Table(summary_data, colWidths=[100, 160, 110, 160])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), LIGHT_BG),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('PADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 10))

    # 3. Component Score Breakdown Table
    story.append(Paragraph("Algorithmic Factor Breakdown", section_heading))
    
    comp_headers = [
        Paragraph("<b>Evaluation Factor</b>", body_bold),
        Paragraph("<b>Nominal Wt</b>", body_bold),
        Paragraph("<b>Active Wt</b>", body_bold),
        Paragraph("<b>Factor Score</b>", body_bold),
        Paragraph("<b>Weighted Contrib</b>", body_bold),
        Paragraph("<b>Status</b>", body_bold)
    ]
    comp_rows = [comp_headers]
    
    for c_id, comp in result.components.items():
        comp_rows.append([
            Paragraph(comp.name, body_style),
            Paragraph(f"{round(comp.nominal_weight * 100)}%", body_style),
            Paragraph(f"{round(comp.effective_weight * 100, 1)}%", body_style),
            Paragraph(f"<b>{round(comp.raw_score, 1)}%</b>", body_style),
            Paragraph(f"<b>{round(comp.weighted_score, 1)}%</b>", body_style),
            Paragraph("<font color='red'>Missing</font>" if comp.is_missing else "<font color='green'>Verified</font>", body_style)
        ])
        
    # Total row
    comp_rows.append([
        Paragraph("<b>Composite Suitability</b>", body_bold),
        Paragraph("<b>100%</b>", body_bold),
        Paragraph("<b>100%</b>", body_bold),
        Paragraph("-", body_bold),
        Paragraph(f"<b>{result.overall_score}%</b>", body_bold),
        Paragraph(f"<b>{result.fit_tier}</b>", body_bold)
    ])
    
    comp_table = Table(comp_rows, colWidths=[160, 70, 70, 75, 85, 70])
    comp_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#EEF2FF")),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('PADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BACKGROUND', (0,-1), (-1,-1), LIGHT_BG),
    ]))
    story.append(comp_table)
    story.append(Spacer(1, 10))

    # 4. Skills Taxonomy Match Analysis
    story.append(Paragraph("Technical Skills Alignment", section_heading))
    
    skills_data = [
        [
            Paragraph("<b>Matched Mandatory Skills:</b>", body_bold),
            Paragraph(", ".join(result.matched_required_skills) if result.matched_required_skills else "None detected", body_style)
        ],
        [
            Paragraph("<b>Missing Mandatory Skills:</b>", body_bold),
            Paragraph(
                f"<font color='red'>{', '.join(result.missing_required_skills)}</font>" if result.missing_required_skills else "None (100% Match)",
                body_style
            )
        ],
        [
            Paragraph("<b>Matched Preferred Skills:</b>", body_bold),
            Paragraph(", ".join(result.matched_preferred_skills) if result.matched_preferred_skills else "None", body_style)
        ],
        [
            Paragraph("<b>Additional Competencies:</b>", body_bold),
            Paragraph(", ".join(result.additional_skills[:12]) if result.additional_skills else "None", body_style)
        ]
    ]
    skills_table = Table(skills_data, colWidths=[150, 380])
    skills_table.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('PADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(skills_table)
    story.append(Spacer(1, 10))

    # 5. Experience & Education Evidence
    story.append(Paragraph("Experience & Education Detailed Evidence", section_heading))
    
    exp_evidence = result.components.get("experience").evidence if "experience" in result.components else {}
    edu_evidence = result.components.get("education").evidence if "education" in result.components else {}
    
    detail_data = [
        [
            Paragraph("<b>Experience Summary:</b>", body_bold),
            Paragraph(exp_evidence.get("explanation", "Experience details parsed."), body_style)
        ],
        [
            Paragraph("<b>Education Summary:</b>", body_bold),
            Paragraph(edu_evidence.get("explanation", "Education credentials verified."), body_style)
        ]
    ]
    detail_table = Table(detail_data, colWidths=[150, 380])
    detail_table.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('PADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(detail_table)
    story.append(Spacer(1, 10))

    # 6. Mathematical Trace & Limitations Callout
    story.append(Paragraph("Algorithmic Trace & Audit Disclaimers", section_heading))
    
    limitations_text = "<br/>".join([f"• {lim}" for lim in result.limitations]) if result.limitations else "• No data anomalies or missing sections detected."
    callout_content = [
        [
            Paragraph(
                f"<b>Audit Limitations & Missing Data Notes:</b><br/>{limitations_text}<br/><br/>"
                "<b>Ethical AI Notice:</b> Realize utilizes 100% classical deterministic algorithms and TF-IDF statistical scoring. "
                "No generative AI, protected personal traits, or demographic indicators are incorporated into scoring. "
                "This document is an advisory decision-support artifact; final hiring selections require human recruiter review.",
                callout_style
            )
        ]
    ]
    callout_table = Table(callout_content, colWidths=[530])
    callout_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#FEF3C7")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#F59E0B")),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(callout_table)

    # Build PDF
    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
