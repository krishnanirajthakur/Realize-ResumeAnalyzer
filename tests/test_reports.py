"""
Tests for ReportLab PDF Report Generation
"""
from reporting.pdf_generator import generate_candidate_pdf_report
from core.scoring.scoring_engine import CandidateScoringEngine

def test_generate_pdf_report(sample_candidate_profile, sample_job_description):
    engine = CandidateScoringEngine()
    result = engine.evaluate_candidate(sample_candidate_profile, sample_job_description)
    
    pdf_bytes = generate_candidate_pdf_report(result)
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 1000 # Valid PDF document has substantial byte size
    # Check PDF magic bytes '%PDF'
    assert pdf_bytes.startswith(b'%PDF')
