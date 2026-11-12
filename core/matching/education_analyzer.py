"""
Deterministic Education Credential and Major Alignment Analyzer
"""
import re
from typing import Dict, List, Tuple, Any, Optional
from config.settings import DEGREE_TIERS, TECH_MAJORS

DEGREE_NAMES_MAP = {
    5: "Doctorate / Ph.D.",
    4: "Master's Degree",
    3: "Bachelor's Degree",
    2: "Associate Degree / Diploma",
    1: "Secondary / High School",
    0: "Unspecified"
}

class EducationAnalyzer:
    """
    Evaluates educational attainment strictly against configurable degree tiers and majors.
    Explicitly excludes institutional prestige, graduation dates, or personal demographic inferences.
    """
    
    def __init__(self, degree_tiers: Dict[str, int] = None, tech_majors: List[str] = None):
        self.degree_tiers = degree_tiers or DEGREE_TIERS
        self.tech_majors = [m.lower() for m in (tech_majors or TECH_MAJORS)]

    def detect_degree_and_major(self, text: str) -> Tuple[int, str, Optional[str]]:
        """
        Detect highest degree tier, formal name, and recognized major discipline.
        
        Returns:
            (tier_int, formal_name_str, detected_major_str)
        """
        lower = text.lower()
        highest_tier = 0
        formal_name = "Unspecified"
        detected_major = None
        
        # Check degree patterns
        # Sort keys by length descending to match 'master of science' before 'ms'
        sorted_degrees = sorted(self.degree_tiers.keys(), key=lambda x: len(x), reverse=True)
        
        for deg in sorted_degrees:
            # Word boundary check for degrees
            deg_pattern = rf'(?<![a-zA-Z0-9_]){re.escape(deg)}(?![a-zA-Z0-9_])'
            if re.search(deg_pattern, lower):
                tier = self.degree_tiers[deg]
                if tier > highest_tier:
                    highest_tier = tier
                    formal_name = DEGREE_NAMES_MAP.get(tier, deg.title())
                    
        # Check detected major
        for major in self.tech_majors:
            if re.search(rf'\b{re.escape(major)}\b', lower):
                detected_major = major.title()
                break
                
        return highest_tier, formal_name, detected_major

    def analyze_education(
        self, resume_edu_text: str, full_resume_text: str, required_degree: str, preferred_fields: List[str] = None
    ) -> Dict[str, Any]:
        """
        Evaluate candidate education level and discipline alignment against JD requirements.
        """
        target_text = resume_edu_text if resume_edu_text.strip() else full_resume_text
        has_section = bool(resume_edu_text.strip())
        
        cand_tier, cand_degree_name, cand_major = self.detect_degree_and_major(target_text)
        req_clean = (required_degree or "bachelor").strip().lower()
        req_tier = self.degree_tiers.get(req_clean, 3) # Default Bachelor's (tier 3)
        req_degree_name = DEGREE_NAMES_MAP.get(req_tier, req_clean.title())
        
        # Degree alignment logic
        meets_requirement = cand_tier >= req_tier
        if cand_tier == 0:
            base_score = 0.0 if not has_section else 40.0
        elif cand_tier >= req_tier:
            base_score = 100.0
        elif cand_tier == req_tier - 1:
            base_score = 75.0
        else:
            base_score = 40.0
            
        # Major alignment check
        major_match = False
        target_majors = [m.lower() for m in (preferred_fields or [])] if preferred_fields else self.tech_majors
        
        if cand_major:
            if any(tm in cand_major.lower() for tm in target_majors):
                major_match = True
                
        # Final score adjustments (capped at 100)
        final_score = base_score
        if major_match and final_score < 100.0:
            final_score = min(100.0, final_score + 10.0)
            
        explanation_parts = []
        if cand_tier >= req_tier:
            explanation_parts.append(
                f"Candidate holds a {cand_degree_name} (Tier {cand_tier}), satisfying or exceeding the minimum required {req_degree_name} (Tier {req_tier})."
            )
        elif cand_tier > 0:
            explanation_parts.append(
                f"Candidate holds a {cand_degree_name} (Tier {cand_tier}), which is below the benchmark requirement of {req_degree_name} (Tier {req_tier})."
            )
        else:
            explanation_parts.append(
                f"No specific degree credential could be identified in the candidate profile (benchmark requires {req_degree_name})."
            )
            
        if cand_major:
            if major_match:
                explanation_parts.append(f"Major in '{cand_major}' matches target technical disciplines (+bonus applied).")
            else:
                explanation_parts.append(f"Detected field of study: '{cand_major}'.")
                
        return {
            "score": round(final_score, 1),
            "candidate_tier": cand_tier,
            "required_tier": req_tier,
            "candidate_degree": cand_degree_name,
            "required_degree": req_degree_name,
            "candidate_major": cand_major,
            "meets_requirement": meets_requirement,
            "major_match": major_match,
            "has_education_section": has_section or cand_tier > 0,
            "explanation": " ".join(explanation_parts)
        }
