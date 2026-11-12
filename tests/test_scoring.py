"""
Tests for Candidate Scoring Engine, Dynamic Re-normalization, and Audit Traces
"""
from core.scoring.scoring_engine import CandidateScoringEngine, determine_fit_tier
from core.scoring.renormalizer import renormalize_weights
from config.settings import DEFAULT_WEIGHTS

def test_default_weights_sum_to_100():
    total = sum(DEFAULT_WEIGHTS.values())
    assert abs(total - 100.0) < 1e-4

def test_renormalization_missing_experience():
    nominal = DEFAULT_WEIGHTS.copy()
    # If experience (20%) is missing:
    missing = {"experience"}
    effective_weights, confidence, warnings = renormalize_weights(nominal, missing)
    
    assert effective_weights["experience"] == 0.0
    # Sum of active effective weights must equal exactly 1.0 (100%)
    active_sum = sum(effective_weights.values())
    assert abs(active_sum - 1.0) < 1e-4
    assert confidence == 80.0
    assert len(warnings) > 0

def test_candidate_scoring_execution(sample_candidate_profile, sample_job_description):
    engine = CandidateScoringEngine()
    result = engine.evaluate_candidate(sample_candidate_profile, sample_job_description)
    
    assert 0.0 <= result.overall_score <= 100.0
    assert result.overall_score >= 75.0 # Strong/Moderate match candidate
    assert result.fit_tier in ["Strong Fit", "Moderate Fit"]
    assert len(result.audit_trace) >= 5
    assert "skill_match" in result.components

def test_determine_fit_tier():
    assert determine_fit_tier(88.5) == "Strong Fit"
    assert determine_fit_tier(72.0) == "Moderate Fit"
    assert determine_fit_tier(54.0) == "Partial Fit"
    assert determine_fit_tier(35.0) == "Limited Fit"
