"""
Tests for TF-IDF Cosine Similarity Engine
"""
from core.matching.similarity_engine import SimilarityEngine

def test_identical_text_similarity():
    engine = SimilarityEngine()
    text = "Senior Python engineer building microservices with Docker and PostgreSQL."
    result = engine.compute_similarity(text, text)
    assert result["similarity_score"] >= 99.0
    assert result["cosine_coefficient"] >= 0.99

def test_disjoint_text_similarity():
    engine = SimilarityEngine()
    text1 = "Culinary arts and professional chef kitchen operations."
    text2 = "Kubernetes cloud infrastructure terraform automation."
    result = engine.compute_similarity(text1, text2)
    assert result["similarity_score"] < 15.0

def test_empty_text_similarity():
    engine = SimilarityEngine()
    result = engine.compute_similarity("", "Target JD description.")
    assert result["similarity_score"] == 0.0
    assert result["cosine_coefficient"] == 0.0

def test_boundedness():
    engine = SimilarityEngine()
    res = engine.compute_similarity(
        "Python developer with machine learning experience",
        "Python data scientist with machine learning knowledge"
    )
    assert 0.0 <= res["similarity_score"] <= 100.0
