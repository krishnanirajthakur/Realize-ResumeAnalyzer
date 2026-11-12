"""
Pytest Test Configuration and Shared Fixtures
"""
import sys
import os

# Add root directory to python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from core.models import CandidateProfile, JobDescription
from core.matching.skill_extractor import SkillTaxonomyMatcher

@pytest.fixture
def skill_matcher():
    return SkillTaxonomyMatcher()

@pytest.fixture
def sample_candidate_profile():
    resume_raw = """
        Dr. Elena Rostova
        Email: elena@example.com
        
        Professional Summary:
        Senior Machine Learning Engineer with 6 years experience in Python, Scikit-Learn, Docker, and PostgreSQL.
        
        Technical Skills:
        Python, Scikit-Learn, Docker, Kubernetes, PostgreSQL, SQL, AWS, Git
        
        Professional Experience:
        Machine Learning Engineer | Apex Labs
        01/2020 - Present
        Developed predictive ML pipelines using Python, Scikit-Learn, and PostgreSQL.
        
        Software Engineer | DataCorp
        01/2018 - 12/2019
        Built backend data services with Python and SQL.
        
        Educational Qualifications:
        Doctorate in Computer Science | Stanford University
        
        Key Projects:
        NLP Search Engine: Built TF-IDF text search microservice with Python, Scikit-Learn, Docker, and PostgreSQL.
        """
    return CandidateProfile(
        candidate_id="cand_001",
        source_filename="Elena_Rostova.pdf",
        name="Elena Rostova",
        email="elena@example.com",
        phone="+1-555-0192",
        raw_text=resume_raw,
        clean_text=resume_raw,
        sections={
            "skills": "Python, Scikit-Learn, Docker, Kubernetes, PostgreSQL, SQL, AWS, Git",
            "experience": "01/2020 - Present\n01/2018 - 12/2019",
            "education": "Doctorate in Computer Science | Stanford University",
            "projects": "NLP Search Engine: Built TF-IDF text search microservice with Python, Scikit-Learn, Docker, and PostgreSQL."
        },
        skills=["Python", "Scikit-Learn", "Docker", "Kubernetes", "PostgreSQL", "SQL", "AWS", "Git"],
        experience_years=6.0,
        education_level="Doctorate / Ph.D.",
        education_field="Computer Science"
    )

@pytest.fixture
def sample_job_description():
    return JobDescription(
        jd_id="jd_001",
        title="Senior Python & ML Engineer",
        raw_text="Job Title: Senior Python & ML Engineer\nRequired Skills: Python, Scikit-Learn, Docker, PostgreSQL\nPreferred Skills: Kubernetes, AWS\nRequired Experience: 5 years\nEducation: Bachelor in Computer Science",
        clean_text="Job Title: Senior Python & ML Engineer. Required Skills: Python, Scikit-Learn, Docker, PostgreSQL.",
        required_skills=["Python", "Scikit-Learn", "Docker", "PostgreSQL"],
        preferred_skills=["Kubernetes", "AWS"],
        required_experience_years=5.0,
        required_education_level="bachelor",
        preferred_fields=["Computer Science"],
        responsibilities="Build machine learning pipelines and microservices in Python."
    )
