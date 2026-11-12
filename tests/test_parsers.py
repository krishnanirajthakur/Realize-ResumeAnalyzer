"""
Tests for PDF, DOCX, and Job Description Parsers
"""
import pytest
import os
from core.parsers.pdf_parser import parse_pdf, PDFParsingError
from core.parsers.docx_parser import parse_docx, DOCXParsingError
from core.parsers.jd_parser import parse_job_description, extract_years_required, extract_required_education
from core.matching.skill_extractor import extract_skills_from_text

def test_parse_sample_pdf():
    pdf_path = "data/sample_resumes/Dr_Elena_Rostova.pdf"
    assert os.path.exists(pdf_path), "Sample PDF should exist."
    text, meta = parse_pdf(pdf_path)
    assert len(text) > 100
    assert "Elena Rostova" in text
    assert meta["format"] == "PDF"
    assert meta["page_count"] >= 1

def test_parse_sample_docx():
    docx_path = "data/sample_resumes/Marcus_Chen.docx"
    assert os.path.exists(docx_path), "Sample DOCX should exist."
    text, meta = parse_docx(docx_path)
    assert len(text) > 100
    assert "Marcus Chen" in text
    assert meta["format"] == "DOCX"

def test_corrupt_pdf_handling():
    corrupted_bytes = b"This is not a valid PDF file stream."
    with pytest.raises(PDFParsingError):
        parse_pdf(corrupted_bytes)

def test_corrupt_docx_handling():
    corrupted_bytes = b"Invalid docx binary content."
    with pytest.raises(DOCXParsingError):
        parse_docx(corrupted_bytes)

def test_jd_parser_extraction():
    sample_text = """
    Job Title: Lead Cloud & Data Architect
    Responsibilities:
    Design scalable big data pipelines and orchestrate cloud resources.
    Requirements:
    - 7+ years of experience in distributed systems.
    - Master's degree in Computer Science or Software Engineering.
    - Required Skills: Python, AWS, Docker, Kubernetes, SQL.
    - Nice to have: Terraform, Spark.
    """
    jd = parse_job_description(sample_text, extract_skills_from_text)
    assert "Architect" in jd.title
    assert jd.required_experience_years == 7.0
    assert jd.required_education_level == "master"
    assert "Python" in jd.required_skills
    assert "Docker" in jd.required_skills
