"""
Composite Candidate Scoring Engine and Explainable Audit Generator
"""
import uuid
from typing import Dict, List, Any, Optional, Set
from core.models import CandidateProfile, JobDescription, ComponentScore, AnalysisResult
from config.settings import DEFAULT_WEIGHTS
from core.scoring.renormalizer import renormalize_weights
from core.matching.skill_extractor import get_skill_matcher
from core.matching.similarity_engine import SimilarityEngine
from core.matching.experience_analyzer import ExperienceAnalyzer
from core.matching.education_analyzer import EducationAnalyzer
from core.matching.project_analyzer import ProjectAnalyzer

def determine_fit_tier(score: float) -> str:
    """Classify into transparent advisory fit tiers without automated rejection."""
    if score >= 80.0:
        return "Strong Fit"
    elif score >= 65.0:
        return "Moderate Fit"
    elif score >= 50.0:
        return "Partial Fit"
    else:
        return "Limited Fit"

class CandidateScoringEngine:
    """
    Evaluates candidate profiles against job benchmarks using configurable linear weights,
    dynamic missing-component re-normalization, and transparent mathematical traces.
    """
    
    def __init__(self, weights: Dict[str, float] = None):
        self.nominal_weights = (weights or DEFAULT_WEIGHTS).copy()
        self.similarity_engine = SimilarityEngine()
        self.experience_analyzer = ExperienceAnalyzer()
        self.education_analyzer = EducationAnalyzer()
        self.project_analyzer = ProjectAnalyzer()
        self.skill_matcher = get_skill_matcher()

    def set_weights(self, weights: Dict[str, float]):
        self.nominal_weights = weights.copy()

    def evaluate_candidate(
        self, candidate: CandidateProfile, jd: JobDescription
    ) -> AnalysisResult:
        """
        Execute comprehensive candidate analysis and return fully explainable AnalysisResult.
        """
        audit_trace: List[str] = []
        limitations: List[str] = []
        missing_components: Set[str] = set()

        audit_trace.append(f"Initiated deterministic evaluation for candidate '{candidate.name}' against role '{jd.title}'.")
        
        # 1. Required Skills Score
        skill_match_data = self.skill_matcher.match_against_jd(
            candidate.skills, jd.required_skills, jd.preferred_skills
        )
        matched_req = skill_match_data["matched_required"]
        missing_req = skill_match_data["missing_required"]
        matched_pref = skill_match_data["matched_preferred"]
        addl_skills = skill_match_data["additional_skills"]
        
        if len(jd.required_skills) > 0:
            req_skill_score = (len(matched_req) / len(jd.required_skills)) * 100.0
            req_skill_score = round(max(0.0, min(100.0, req_skill_score)), 1)
        else:
            req_skill_score = 100.0
            
        audit_trace.append(
            f"Required Skills: {len(matched_req)}/{len(jd.required_skills)} matched -> Score: {req_skill_score}%."
        )
        if not candidate.skills:
            missing_components.add("skill_match")

        # 2. Preferred & Additional Skills Score
        if len(jd.preferred_skills) > 0:
            pref_ratio = len(matched_pref) / len(jd.preferred_skills)
            extra_ratio = min(len(addl_skills), 5) / 5.0
            addl_score = round(min(100.0, (pref_ratio * 80.0) + (extra_ratio * 20.0)), 1)
        else:
            # When no preferred skills in JD, award based on additional relevant technical skills
            extra_ratio = min(len(addl_skills), 6) / 6.0
            addl_score = round(extra_ratio * 100.0, 1)
            
        audit_trace.append(
            f"Preferred/Additional Skills: {len(matched_pref)} preferred, {len(addl_skills)} extra -> Score: {addl_score}%."
        )

        # 3. TF-IDF Lexical Similarity Score
        sim_data = self.similarity_engine.compute_similarity(candidate.clean_text, jd.clean_text)
        sim_score = sim_data["similarity_score"]
        audit_trace.append(
            f"TF-IDF Cosine Lexical Similarity: Cosine coefficient = {sim_data['cosine_coefficient']} -> Score: {sim_score}%."
        )

        # 4. Experience Alignment Score
        exp_data = self.experience_analyzer.analyze_experience(
            candidate.sections.get("experience", ""),
            candidate.clean_text,
            jd.required_experience_years
        )
        exp_score = exp_data["score"]
        candidate.experience_years = exp_data["candidate_years"]
        if not exp_data["has_experience_section"] and exp_data["candidate_years"] == 0.0:
            missing_components.add("experience")
            limitations.append("Professional experience section could not be reliably parsed from the document.")
        audit_trace.append(f"Experience Analysis: {exp_data['explanation']} -> Score: {exp_score}%.")

        # 5. Education Level Score
        edu_data = self.education_analyzer.analyze_education(
            candidate.sections.get("education", ""),
            candidate.clean_text,
            jd.required_education_level,
            jd.preferred_fields
        )
        edu_score = edu_data["score"]
        candidate.education_level = edu_data["candidate_degree"]
        candidate.education_field = edu_data["candidate_major"]
        if not edu_data["has_education_section"]:
            missing_components.add("education")
            limitations.append("Educational credential details could not be identified.")
        audit_trace.append(f"Education Analysis: {edu_data['explanation']} -> Score: {edu_score}%.")

        # 6. Project Relevance Score
        proj_data = self.project_analyzer.analyze_projects(
            candidate.sections.get("projects", ""),
            candidate.clean_text,
            jd.responsibilities,
            jd.required_skills
        )
        proj_score = proj_data["score"]
        if not proj_data["has_projects_section"]:
            missing_components.add("projects")
            limitations.append("Distinct project descriptions were not detected in resume.")
        audit_trace.append(f"Project Relevance: {proj_data['explanation']} -> Score: {proj_score}%.")

        # Dynamic Re-normalization
        effective_weights, confidence, renorm_warnings = renormalize_weights(
            self.nominal_weights, missing_components
        )
        limitations.extend(renorm_warnings)

        # Construct ComponentScore objects
        components: Dict[str, ComponentScore] = {
            "skill_match": ComponentScore(
                component_id="skill_match",
                name="Mandatory Skills Match",
                raw_score=req_skill_score,
                nominal_weight=self.nominal_weights["skill_match"] / 100.0,
                effective_weight=effective_weights["skill_match"],
                weighted_score=round(effective_weights["skill_match"] * req_skill_score, 2),
                is_missing="skill_match" in missing_components,
                evidence={
                    "matched": matched_req,
                    "missing": missing_req,
                    "total_required": len(jd.required_skills)
                }
            ),
            "text_similarity": ComponentScore(
                component_id="text_similarity",
                name="Lexical Similarity (TF-IDF)",
                raw_score=sim_score,
                nominal_weight=self.nominal_weights["text_similarity"] / 100.0,
                effective_weight=effective_weights["text_similarity"],
                weighted_score=round(effective_weights["text_similarity"] * sim_score, 2),
                is_missing=False,
                evidence={
                    "top_terms": sim_data["top_matching_terms"],
                    "cosine": sim_data["cosine_coefficient"]
                }
            ),
            "experience": ComponentScore(
                component_id="experience",
                name="Experience Alignment",
                raw_score=exp_score,
                nominal_weight=self.nominal_weights["experience"] / 100.0,
                effective_weight=effective_weights["experience"],
                weighted_score=round(effective_weights["experience"] * exp_score, 2),
                is_missing="experience" in missing_components,
                evidence=exp_data
            ),
            "education": ComponentScore(
                component_id="education",
                name="Education Qualification",
                raw_score=edu_score,
                nominal_weight=self.nominal_weights["education"] / 100.0,
                effective_weight=effective_weights["education"],
                weighted_score=round(effective_weights["education"] * edu_score, 2),
                is_missing="education" in missing_components,
                evidence=edu_data
            ),
            "projects": ComponentScore(
                component_id="projects",
                name="Project Relevance",
                raw_score=proj_score,
                nominal_weight=self.nominal_weights["projects"] / 100.0,
                effective_weight=effective_weights["projects"],
                weighted_score=round(effective_weights["projects"] * proj_score, 2),
                is_missing="projects" in missing_components,
                evidence=proj_data
            ),
            "additional_skills": ComponentScore(
                component_id="additional_skills",
                name="Preferred & Complementary Skills",
                raw_score=addl_score,
                nominal_weight=self.nominal_weights["additional_skills"] / 100.0,
                effective_weight=effective_weights["additional_skills"],
                weighted_score=round(effective_weights["additional_skills"] * addl_score, 2),
                is_missing=False,
                evidence={
                    "matched_preferred": matched_pref,
                    "additional_skills": addl_skills[:10]
                }
            )
        }

        # Calculate Composite Overall Score
        overall_score = sum(comp.weighted_score for comp in components.values())
        overall_score = round(max(0.0, min(100.0, overall_score)), 1)
        fit_tier = determine_fit_tier(overall_score)
        
        audit_trace.append(
            f"Final Re-normalized Score: {overall_score}% | Fit Tier: {fit_tier} | Assessment Confidence: {confidence}%."
        )

        return AnalysisResult(
            evaluation_id=str(uuid.uuid4())[:8],
            candidate=candidate,
            job_description=jd,
            overall_score=overall_score,
            fit_tier=fit_tier,
            confidence_score=confidence,
            components=components,
            matched_required_skills=matched_req,
            missing_required_skills=missing_req,
            matched_preferred_skills=matched_pref,
            additional_skills=addl_skills,
            experience_gap_years=exp_data["gap_years"],
            education_matched=edu_data["meets_requirement"],
            audit_trace=audit_trace,
            limitations=limitations
        )
