"""
Boundary-Safe Deterministic Skill Extraction and Taxonomy Matcher
"""
import re
import json
import os
from typing import Dict, List, Set, Tuple, Optional
from config.settings import TAXONOMY_PATH

class SkillTaxonomyMatcher:
    """
    High-precision deterministic skill matcher using boundary-safe regex patterns and alias mapping.
    Prevents false-positive substring matches (e.g. Java in JavaScript, Go in Google, C in Code).
    """
    
    def __init__(self, taxonomy_file: str = TAXONOMY_PATH):
        self.taxonomy_file = taxonomy_file
        self.skills_by_name: Dict[str, Dict] = {}
        self.compiled_patterns: List[Tuple[str, re.Pattern, str]] = [] # (canonical_name, regex, category)
        self.load_taxonomy()

    def load_taxonomy(self):
        """Load skill definitions from JSON and compile boundary-safe regex patterns."""
        if not os.path.exists(self.taxonomy_file):
            return
            
        with open(self.taxonomy_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        skills = data.get("skills", [])
        self.compiled_patterns = []
        self.skills_by_name = {}
        
        for item in skills:
            name = item["name"]
            category = item.get("category", "General")
            aliases = item.get("aliases", [])
            self.skills_by_name[name] = {"category": category, "aliases": aliases}
            
            # Combine canonical name and aliases into regex
            all_terms = [name] + aliases
            for term in all_terms:
                term_clean = term.strip()
                if not term_clean:
                    continue
                
                # Special boundary handling for single-letter and symbol-laden languages
                lower_term = term_clean.lower()
                if lower_term == "c":
                    # Match 'C' when preceded/followed by delimiters, or as 'C language', 'ANSI C'
                    pattern_str = r'(?<![a-zA-Z0-9_])(?:c\s+programming|ansi\s+c|\bc\b(?=\s*[,/|\n\r]|\s+language|\s+code))'
                elif lower_term == "r":
                    pattern_str = r'(?<![a-zA-Z0-9_])(?:r\s+programming|r-lang|\br\b(?=\s*[,/|\n\r]|\s+language|\s+package))'
                elif lower_term == "go":
                    pattern_str = r'(?<![a-zA-Z0-9_])(?:golang|\bgo\b(?=\s*[,/|\n\r]|\s+language|\s+dev|\s+developer))'
                elif lower_term == "c++":
                    pattern_str = r'(?<![a-zA-Z0-9_])(?:c\+\+|cpp|cplusplus)(?![a-zA-Z0-9_])'
                elif lower_term == "c#":
                    pattern_str = r'(?<![a-zA-Z0-9_])(?:c\#|csharp|c-sharp)(?![a-zA-Z0-9_])'
                elif lower_term == ".net core" or lower_term == ".net":
                    pattern_str = r'(?<![a-zA-Z0-9_])(?:\.net(?:\s+core)?|dotnet)(?![a-zA-Z0-9_])'
                else:
                    # General boundary-safe regex
                    escaped = re.escape(lower_term)
                    # Protect both left and right boundaries
                    pattern_str = rf'(?<![a-zA-Z0-9_]){escaped}(?![a-zA-Z0-9_])'
                    
                compiled = re.compile(pattern_str, re.IGNORECASE)
                self.compiled_patterns.append((name, compiled, category))

    def extract_skills(self, text: str) -> List[str]:
        """Extract deduplicated list of canonical skill names found in text."""
        if not text:
            return []
            
        matched_canonical: Set[str] = set()
        
        for canonical_name, pattern, _ in self.compiled_patterns:
            if canonical_name in matched_canonical:
                continue
            if pattern.search(text):
                matched_canonical.add(canonical_name)
                
        # Return sorted list for determinism
        return sorted(list(matched_canonical))

    def categorize_skills(self, skills: List[str]) -> Dict[str, List[str]]:
        """Group detected skills by taxonomy category."""
        categorized: Dict[str, List[str]] = {}
        for skill in skills:
            cat = self.skills_by_name.get(skill, {}).get("category", "Other Technical Skills")
            categorized.setdefault(cat, []).append(skill)
            
        for cat in categorized:
            categorized[cat].sort()
            
        return categorized

    def match_against_jd(
        self, candidate_skills: List[str], required_skills: List[str], preferred_skills: List[str]
    ) -> Dict[str, List[str]]:
        """
        Compare candidate skills against JD required and preferred skills.
        
        Returns:
            {
                "matched_required": [...],
                "missing_required": [...],
                "matched_preferred": [...],
                "missing_preferred": [...],
                "additional_skills": [...]
            }
        """
        cand_set = set(candidate_skills)
        req_set = set(required_skills)
        pref_set = set(preferred_skills)
        
        matched_req = sorted(list(cand_set.intersection(req_set)))
        missing_req = sorted(list(req_set.difference(cand_set)))
        
        matched_pref = sorted(list(cand_set.intersection(pref_set)))
        missing_pref = sorted(list(pref_set.difference(cand_set)))
        
        additional = sorted(list(cand_set.difference(req_set).difference(pref_set)))
        
        return {
            "matched_required": matched_req,
            "missing_required": missing_req,
            "matched_preferred": matched_pref,
            "missing_preferred": missing_pref,
            "additional_skills": additional
        }

# Global Singleton Instance
_MATCHER_INSTANCE: Optional[SkillTaxonomyMatcher] = None

def get_skill_matcher() -> SkillTaxonomyMatcher:
    global _MATCHER_INSTANCE
    if _MATCHER_INSTANCE is None:
        _MATCHER_INSTANCE = SkillTaxonomyMatcher()
    return _MATCHER_INSTANCE

def extract_skills_from_text(text: str) -> List[str]:
    return get_skill_matcher().extract_skills(text)
