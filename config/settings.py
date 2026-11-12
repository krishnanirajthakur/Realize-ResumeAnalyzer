"""
ResumeIQ Configuration and Global Settings
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_DIR = os.path.join(BASE_DIR, "config")
DATA_DIR = os.path.join(BASE_DIR, "data")
TAXONOMY_PATH = os.path.join(CONFIG_DIR, "taxonomy.json")

# Initial Default Component Weights (sum to 100.0)
DEFAULT_WEIGHTS: Dict[str, float] = {
    "skill_match": 35.0,        # Matched Required Skills
    "text_similarity": 20.0,    # TF-IDF Cosine Similarity
    "experience": 20.0,         # Chronological Experience Alignment
    "education": 10.0,          # Education Credential & Major
    "projects": 10.0,           # Project Alignment & Keyword Density
    "additional_skills": 5.0,   # Bonus for Preferred/Additional Competencies
}

# Similarity Engine Defaults
DEFAULT_SIMILARITY_CONFIG = {
    "ngram_range": (1, 2),
    "sublinear_tf": True,
    "max_features": 5000,
    "min_df": 1,
}

# Experience Tier Thresholds (years)
EXPERIENCE_THRESHOLDS = {
    "entry": 1.0,
    "mid": 3.0,
    "senior": 5.0,
    "lead": 8.0,
    "principal": 12.0,
}

# Degree Hierarchy (higher number = higher tier)
DEGREE_TIERS = {
    "doctorate": 5,
    "phd": 5,
    "ph.d": 5,
    "postdoc": 5,
    "master": 4,
    "masters": 4,
    "m.tech": 4,
    "mtech": 4,
    "ms": 4,
    "m.s": 4,
    "msc": 4,
    "m.sc": 4,
    "mba": 4,
    "m.b.a": 4,
    "mca": 4,
    "bachelor": 3,
    "bachelors": 3,
    "b.tech": 3,
    "btech": 3,
    "be": 3,
    "b.e": 3,
    "bs": 3,
    "b.s": 3,
    "bsc": 3,
    "b.sc": 3,
    "bca": 3,
    "ba": 3,
    "b.a": 3,
    "b.com": 3,
    "bcom": 3,
    "associate": 2,
    "diploma": 2,
    "polytechnic": 2,
    "high school": 1,
    "secondary": 1,
    "hsc": 1,
    "ssc": 1,
}

# Relevant STEM / Tech majors
TECH_MAJORS = [
    "computer science", "information technology", "software engineering",
    "data science", "artificial intelligence", "machine learning",
    "computer engineering", "electronics", "electrical engineering",
    "mathematics", "statistics", "physics", "computational"
]

@dataclass
class AppConfig:
    weights: Dict[str, float] = field(default_factory=lambda: DEFAULT_WEIGHTS.copy())
    similarity_config: Dict = field(default_factory=lambda: DEFAULT_SIMILARITY_CONFIG.copy())
    experience_thresholds: Dict[str, float] = field(default_factory=lambda: EXPERIENCE_THRESHOLDS.copy())
    degree_tiers: Dict[str, int] = field(default_factory=lambda: DEGREE_TIERS.copy())
    tech_majors: List[str] = field(default_factory=lambda: TECH_MAJORS.copy())

    def validate_weights(self) -> bool:
        total = sum(self.weights.values())
        return abs(total - 100.0) < 1e-4

    def update_weight(self, component: str, value: float) -> None:
        if component in self.weights:
            self.weights[component] = max(0.0, min(100.0, value))
