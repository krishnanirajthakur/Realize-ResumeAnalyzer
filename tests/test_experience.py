"""
Tests for Chronological Experience and Overlap Coalescing
"""
from core.matching.experience_analyzer import ExperienceAnalyzer

def test_single_interval():
    analyzer = ExperienceAnalyzer(current_year=2026, current_month=11)
    text = "Software Engineer | 01/2020 - 12/2022"
    intervals = analyzer.extract_date_intervals(text)
    years = analyzer.coalesce_intervals(intervals)
    assert 2.8 <= years <= 3.2

def test_overlapping_intervals_coalesced():
    analyzer = ExperienceAnalyzer(current_year=2026, current_month=11)
    # Job 1: 2019 to 2022 (3 years)
    # Job 2: 2020 to 2021 (1 year, completely concurrent/overlapping with Job 1)
    # True elapsed tenure should be 3 years, NOT 4 years!
    text = """
    Lead Engineer | 2019 - 2022
    Advisory Consultant | 2020 - 2021
    """
    intervals = analyzer.extract_date_intervals(text)
    years = analyzer.coalesce_intervals(intervals)
    assert 2.8 <= years <= 3.2

def test_experience_scoring_alignment():
    analyzer = ExperienceAnalyzer(current_year=2026, current_month=11)
    exp_text = "Senior Engineer | 01/2018 - 12/2023" # 6 years
    result = analyzer.analyze_experience(exp_text, "", required_years=5.0)
    assert result["score"] == 100.0
    assert result["gap_years"] == 1.0

    # Deficit test (e.g. 2.5 years vs 5 years required)
    short_text = "Junior Engineer | 01/2021 - 06/2023" # 2.5 years
    deficit_result = analyzer.analyze_experience(short_text, "", required_years=5.0)
    assert deficit_result["score"] < 100.0
    assert deficit_result["gap_years"] < 0.0
