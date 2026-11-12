"""
Tests for Education Tier Alignment and Major Mapping
"""
from core.matching.education_analyzer import EducationAnalyzer

def test_higher_degree_attained():
    analyzer = EducationAnalyzer()
    text = "Candidate holds a Doctorate (Ph.D.) in Computer Science from MIT."
    res = analyzer.analyze_education(text, "", required_degree="bachelor")
    assert res["score"] == 100.0
    assert res["meets_requirement"] is True
    assert res["candidate_tier"] == 5

def test_matching_major_bonus():
    analyzer = EducationAnalyzer()
    text = "Bachelor of Science in Computer Science."
    res = analyzer.analyze_education(text, "", required_degree="master")
    # Bachelor is tier 3, master is tier 4 -> Base score 75 + major bonus 10 = 85
    assert res["major_match"] is True
    assert res["score"] == 85.0

def test_lower_unrelated_degree():
    analyzer = EducationAnalyzer()
    text = "Secondary high school certificate with general studies."
    res = analyzer.analyze_education(text, "", required_degree="bachelor")
    assert res["meets_requirement"] is False
    assert res["score"] <= 40.0
