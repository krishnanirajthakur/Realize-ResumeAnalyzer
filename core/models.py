"""
ResumeIQ Core Data Models and Types
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime

@dataclass
class CandidateProfile:
    candidate_id: str
    source_filename: str
    name: Optional[str] = "Identified Candidate"
    email: Optional[str] = None
    phone: Optional[str] = None
    raw_text: str = ""
    clean_text: str = ""
    sections: Dict[str, str] = field(default_factory=dict)
    skills: List[str] = field(default_factory=list)
    categorized_skills: Dict[str, List[str]] = field(default_factory=dict)
    experience_years: float = 0.0
    experience_intervals: List[Dict[str, Any]] = field(default_factory=list)
    education_level: str = "Unspecified"
    education_field: Optional[str] = None
    projects_text: str = ""
    parse_errors: List[str] = field(default_factory=list)
    has_experience_section: bool = True
    has_education_section: bool = True
    has_skills_section: bool = True
    has_projects_section: bool = True

@dataclass
class JobDescription:
    jd_id: str
    title: str = "Target Position"
    raw_text: str = ""
    clean_text: str = ""
    required_skills: List[str] = field(default_factory=list)
    preferred_skills: List[str] = field(default_factory=list)
    required_experience_years: float = 0.0
    required_education_level: str = "bachelor"
    preferred_fields: List[str] = field(default_factory=list)
    responsibilities: str = ""
    sections: Dict[str, str] = field(default_factory=dict)

@dataclass
class ComponentScore:
    component_id: str
    name: str
    raw_score: float             # 0.0 to 100.0
    nominal_weight: float        # Default configured weight (e.g. 0.35)
    effective_weight: float      # Re-normalized weight (e.g. 0.40)
    weighted_score: float        # effective_weight * raw_score
    is_missing: bool = False
    evidence: Dict[str, Any] = field(default_factory=dict)
    status_label: str = "Evaluated"

@dataclass
class AnalysisResult:
    evaluation_id: str
    candidate: CandidateProfile
    job_description: JobDescription
    overall_score: float = 0.0
    fit_tier: str = "Evaluating"
    confidence_score: float = 100.0
    components: Dict[str, ComponentScore] = field(default_factory=dict)
    matched_required_skills: List[str] = field(default_factory=list)
    missing_required_skills: List[str] = field(default_factory=list)
    matched_preferred_skills: List[str] = field(default_factory=list)
    additional_skills: List[str] = field(default_factory=list)
    experience_gap_years: float = 0.0
    education_matched: bool = False
    audit_trace: List[str] = field(default_factory=list)
    limitations: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_summary_dict(self) -> Dict[str, Any]:
        return {
            "evaluation_id": self.evaluation_id,
            "filename": self.candidate.source_filename,
            "candidate_name": self.candidate.name or "Candidate",
            "overall_score": round(self.overall_score, 1),
            "fit_tier": self.fit_tier,
            "confidence": round(self.confidence_score, 1),
            "skill_match": round(self.components.get("skill_match", ComponentScore("", "", 0, 0, 0, 0)).raw_score, 1),
            "text_similarity": round(self.components.get("text_similarity", ComponentScore("", "", 0, 0, 0, 0)).raw_score, 1),
            "experience_score": round(self.components.get("experience", ComponentScore("", "", 0, 0, 0, 0)).raw_score, 1),
            "education_score": round(self.components.get("education", ComponentScore("", "", 0, 0, 0, 0)).raw_score, 1),
            "project_score": round(self.components.get("projects", ComponentScore("", "", 0, 0, 0, 0)).raw_score, 1),
            "additional_score": round(self.components.get("additional_skills", ComponentScore("", "", 0, 0, 0, 0)).raw_score, 1),
            "matched_skills_count": len(self.matched_required_skills),
            "missing_skills_count": len(self.missing_required_skills),
            "candidate_exp": round(self.candidate.experience_years, 1),
            "req_exp": round(self.job_description.required_experience_years, 1),
            "exp_gap": round(self.experience_gap_years, 1),
            "education_level": self.candidate.education_level,
            "has_warnings": len(self.limitations) > 0
        }
