"""
Project Relevance and Scope Alignment Analyzer
"""
import re
from typing import Dict, List, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from core.preprocessing.text_cleaner import clean_text

class ProjectAnalyzer:
    """
    Evaluates candidate project narrative alignment against target JD responsibilities
    and technical competencies using classical TF-IDF cosine distance and keyword density.
    """
    
    def analyze_projects(
        self, projects_text: str, full_resume_text: str, jd_responsibilities: str, required_skills: List[str]
    ) -> Dict[str, Any]:
        """
        Evaluate candidate project descriptions for relevance, key technology application, and responsibility overlap.
        """
        target_text = projects_text.strip() if projects_text.strip() else full_resume_text.strip()
        resp_text = jd_responsibilities.strip()
        has_section = bool(projects_text.strip())
        
        # If no project text available
        if not target_text or (not has_section and len(target_text) < 100):
            return {
                "score": 0.0,
                "has_projects_section": False,
                "project_skills_applied": [],
                "responsibility_overlap_pct": 0.0,
                "explanation": "No distinct technical projects section identified in the candidate document."
            }
            
        # 1. Check which required skills are mentioned in projects
        lower_proj = target_text.lower()
        applied_skills = []
        for s in required_skills:
            if re.search(rf'(?<![a-zA-Z0-9_]){re.escape(s.lower())}(?![a-zA-Z0-9_])', lower_proj):
                applied_skills.append(s)
                
        skill_coverage = len(applied_skills) / max(1, len(required_skills))
        
        # 2. Text similarity between projects and JD responsibilities
        sim_pct = 0.0
        if resp_text and len(resp_text) > 30:
            try:
                vec = TfidfVectorizer(ngram_range=(1, 2), stop_words='english', sublinear_tf=True)
                tfidf = vec.fit_transform([clean_text(target_text), clean_text(resp_text)])
                sim_pct = float(cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]) * 100.0
                sim_pct = max(0.0, min(100.0, sim_pct))
            except Exception:
                sim_pct = 0.0
        else:
            # Fallback when responsibilities are brief: weight skill coverage more heavily
            sim_pct = skill_coverage * 100.0
            
        # Combined Project Score: 50% skill application in projects, 50% responsibility/domain similarity
        combined_score = round(0.5 * (skill_coverage * 100.0) + 0.5 * sim_pct, 1)
        
        explanation = (
            f"Candidate applied {len(applied_skills)}/{len(required_skills)} required technical competencies "
            f"in project narratives (e.g. {', '.join(applied_skills[:4]) if applied_skills else 'None'}). "
            f"Responsibility/deliverable alignment measured at {round(sim_pct, 1)}%."
        )
        
        return {
            "score": combined_score,
            "has_projects_section": has_section,
            "project_skills_applied": applied_skills,
            "responsibility_overlap_pct": round(sim_pct, 1),
            "explanation": explanation
        }
