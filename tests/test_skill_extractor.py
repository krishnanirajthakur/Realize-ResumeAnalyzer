"""
Tests for Boundary-Safe Deterministic Skill Extraction and Taxonomy Matching
"""
from core.matching.skill_extractor import SkillTaxonomyMatcher

def test_boundary_safe_matching(skill_matcher):
    # Java should NOT match JavaScript
    text_js = "Frontend specialist skilled in JavaScript, HTML5, and CSS3."
    skills_js = skill_matcher.extract_skills(text_js)
    assert "JavaScript" in skills_js
    assert "Java" not in skills_js

    # Go should NOT match words like 'Google' or 'good'
    text_go = "Good communication skills and experience with Google Cloud search."
    skills_go = skill_matcher.extract_skills(text_go)
    assert "Go" not in skills_go

    # C should NOT match words like 'code' or 'company'
    text_c = "Clean code practices at top enterprise company."
    skills_c = skill_matcher.extract_skills(text_c)
    assert "C" not in skills_c

def test_skill_aliases(skill_matcher):
    text_aliases = "Infrastructure managed with k8s and data stored in postgres database."
    skills = skill_matcher.extract_skills(text_aliases)
    assert "Kubernetes" in skills
    assert "PostgreSQL" in skills

def test_categorization(skill_matcher):
    skills = ["Python", "Docker", "PostgreSQL", "React"]
    categorized = skill_matcher.categorize_skills(skills)
    assert "Programming Languages" in categorized
    assert "Python" in categorized["Programming Languages"]
    assert "DevOps & Containers" in categorized
    assert "Docker" in categorized["DevOps & Containers"]

def test_match_against_jd(skill_matcher):
    cand_skills = ["Python", "SQL", "Docker", "Git", "FastAPI"]
    req_skills = ["Python", "Docker", "Kubernetes"]
    pref_skills = ["FastAPI", "AWS"]
    
    match_data = skill_matcher.match_against_jd(cand_skills, req_skills, pref_skills)
    assert match_data["matched_required"] == ["Docker", "Python"]
    assert match_data["missing_required"] == ["Kubernetes"]
    assert match_data["matched_preferred"] == ["FastAPI"]
    assert "Git" in match_data["additional_skills"]
