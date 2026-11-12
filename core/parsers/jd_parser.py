"""
Job Description Parser and Requirement Extractor
"""
import re
import uuid
from typing import Dict, List, Tuple, Optional
from core.models import JobDescription
from core.preprocessing.text_cleaner import clean_text
from core.preprocessing.section_extractor import extract_sections

JD_SECTION_KEYWORDS = {
    "required_skills": [
        r'\brequired\s+skills\b', r'\btechnical\s+requirements\b', r'\bmust\s+have\b',
        r'\brequirements\b', r'\bminimum\s+qualifications\b', r'\btechnical\s+stack\b'
    ],
    "preferred_skills": [
        r'\bpreferred\s+skills\b', r'\bnice\s+to\s+have\b', r'\bdesired\s+qualifications\b',
        r'\bgood\s+to\s+have\b', r'\bpreferred\s+qualifications\b', r'\bplus\b'
    ],
    "responsibilities": [
        r'\bresponsibilities\b', r'\bduties\b', r'\bwhat\s+you(?:\'ll|\s+will)\s+do\b',
        r'\brole\s+overview\b', r'\bkey\s+deliverables\b', r'\bthe\s+role\b'
    ],
    "education": [
        r'\beducation\b', r'\bqualifications\b', r'\beducational\s+requirements\b'
    ]
}

def extract_years_required(text: str) -> float:
    """Extract required years of experience from JD text deterministically."""
    patterns = [
        # e.g. "5+ years", "at least 3 years", "minimum of 4-6 years", "5 to 7 years"
        r'(?:minimum|at\s+least)?\s*(\d{1,2})\s*(?:\+|\s*to\s*\d{1,2}|\s*-\s*\d{1,2})?\s*(?:years?|yrs?)(?:\s+of)?(?:\s+relevant|\s+work|\s+professional)?\s*experience',
        r'experience\s*(?:of|:)?\s*(?:minimum|at\s+least)?\s*(\d{1,2})\s*(?:\+|\s*to\s*\d{1,2}|\s*-\s*\d{1,2})?\s*(?:years?|yrs?)',
        r'(\d{1,2})\s*\+\s*years?'
    ]
    
    for pat in patterns:
        match = re.search(pat, text, re.IGNORECASE)
        if match:
            try:
                val = float(match.group(1))
                if 0.5 <= val <= 25:
                    return val
            except (ValueError, IndexError):
                continue
                
    return 0.0

def extract_required_education(text: str) -> Tuple[str, List[str]]:
    """Identify required degree tier and target disciplines from JD text."""
    lower_text = text.lower()
    
    level = "bachelor"  # Standard default
    if any(k in lower_text for k in ["phd", "ph.d", "doctorate"]):
        level = "doctorate"
    elif any(k in lower_text for k in ["master's", "masters", "ms in", "m.tech", "mba"]):
        level = "master"
    elif any(k in lower_text for k in ["bachelor's", "bachelors", "bs in", "b.tech", "b.e."]):
        level = "bachelor"
    elif any(k in lower_text for k in ["associate", "diploma"]):
        level = "associate"
        
    majors = []
    major_keywords = [
        "computer science", "data science", "software engineering",
        "information technology", "electrical engineering", "mathematics",
        "statistics", "artificial intelligence"
    ]
    for m in major_keywords:
        if m in lower_text:
            majors.append(m.title())
            
    return level, majors

def extract_job_title(text: str) -> str:
    """Identify target job title from JD text."""
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    
    # Common job title indicators
    for line in lines[:5]:
        clean_l = re.sub(r'^(?:Job Title|Role|Position|Title)\s*:\s*', '', line, flags=re.IGNORECASE).strip()
        lower_l = clean_l.lower()
        if any(term in lower_l for term in [
            "engineer", "developer", "scientist", "analyst", "architect",
            "manager", "lead", "specialist", "consultant", "administrator"
        ]) and len(clean_l.split()) <= 6:
            return clean_l
            
    if lines:
        first_line = lines[0]
        if len(first_line.split()) <= 6:
            return first_line
            
    return "Target Position"

def parse_job_description(raw_jd_text: str, skill_extractor_func = None) -> JobDescription:
    """Parse Job Description text into structured JobDescription model."""
    sanitized = clean_text(raw_jd_text)
    sections = extract_sections(sanitized)
    
    title = extract_job_title(sanitized)
    req_exp = extract_years_required(sanitized)
    edu_level, preferred_majors = extract_required_education(sanitized)
    
    # Responsibilities text
    resp_text = sections.get("experience", "") or sections.get("projects", "") or sections.get("other", "")
    
    # Skills extraction if extractor provided
    req_skills = []
    pref_skills = []
    
    if skill_extractor_func:
        # Check specific section or full text
        skills_text = sections.get("skills", "") or sanitized
        extracted = skill_extractor_func(skills_text)
        req_skills = extracted
        
        # If preferred section is identified, extract preferred
        pref_text = ""
        for line_block in sanitized.split("\n\n"):
            if re.search(r'\b(?:preferred|nice\s+to\s+have|plus|desired)\b', line_block, re.I):
                pref_text += "\n" + line_block
                
        if pref_text:
            pref_extracted = skill_extractor_func(pref_text)
            pref_skills = [s for s in pref_extracted if s not in req_skills]
            
    return JobDescription(
        jd_id=str(uuid.uuid4())[:8],
        title=title,
        raw_text=raw_jd_text,
        clean_text=sanitized,
        required_skills=req_skills,
        preferred_skills=pref_skills,
        required_experience_years=req_exp,
        required_education_level=edu_level,
        preferred_fields=preferred_majors,
        responsibilities=resp_text,
        sections=sections
    )
