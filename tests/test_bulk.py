"""
Tests for Bulk Batch Processing and CSV Export
"""
from reporting.csv_exporter import export_batch_to_csv
from core.scoring.scoring_engine import CandidateScoringEngine

def test_export_batch_to_csv(sample_candidate_profile, sample_job_description):
    engine = CandidateScoringEngine()
    res = engine.evaluate_candidate(sample_candidate_profile, sample_job_description)
    
    csv_str = export_batch_to_csv([res])
    assert "Candidate Name" in csv_str
    assert "Elena Rostova" in csv_str
    assert "Overall Score (%)" in csv_str
    assert "Python" in csv_str
