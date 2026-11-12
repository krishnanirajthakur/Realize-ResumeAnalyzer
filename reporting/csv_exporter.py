"""
Bulk Candidate Screening CSV Export Engine
"""
import io
import pandas as pd
from typing import List, Dict, Any
from core.models import AnalysisResult

def export_batch_to_csv(results: List[AnalysisResult]) -> str:
    """
    Export batch analysis results into a clean, structured CSV format.
    """
    records = []
    for idx, res in enumerate(results, start=1):
        rec = {
            "Rank": idx,
            "Candidate Name": res.candidate.name or "Candidate",
            "Filename": res.candidate.source_filename,
            "Overall Score (%)": round(res.overall_score, 1),
            "Fit Tier": res.fit_tier,
            "Confidence (%)": round(res.confidence_score, 1),
            "Mandatory Skills Score (%)": round(res.components.get("skill_match").raw_score if "skill_match" in res.components else 0, 1),
            "Lexical Similarity (%)": round(res.components.get("text_similarity").raw_score if "text_similarity" in res.components else 0, 1),
            "Experience Score (%)": round(res.components.get("experience").raw_score if "experience" in res.components else 0, 1),
            "Education Score (%)": round(res.components.get("education").raw_score if "education" in res.components else 0, 1),
            "Project Score (%)": round(res.components.get("projects").raw_score if "projects" in res.components else 0, 1),
            "Candidate Tenure (Years)": round(res.candidate.experience_years, 1),
            "Required Tenure (Years)": round(res.job_description.required_experience_years, 1),
            "Tenure Gap (Years)": round(res.experience_gap_years, 1),
            "Education Level": res.candidate.education_level,
            "Major / Discipline": res.candidate.education_field or "N/A",
            "Matched Required Skills": "; ".join(res.matched_required_skills),
            "Missing Required Skills": "; ".join(res.missing_required_skills),
            "Matched Preferred Skills": "; ".join(res.matched_preferred_skills),
            "Audit Limitations": "; ".join(res.limitations) if res.limitations else "None"
        }
        records.append(rec)
        
    df = pd.DataFrame(records)
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    return csv_buffer.getvalue()
