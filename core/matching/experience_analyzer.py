"""
Chronological Experience Extraction, Overlap Coalescing, and Alignment
"""
import re
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional

MONTH_MAP = {
    "jan": 1, "january": 1, "feb": 2, "february": 2, "mar": 3, "march": 3,
    "apr": 4, "april": 4, "may": 5, "jun": 6, "june": 6, "jul": 7, "july": 7,
    "aug": 8, "august": 8, "sep": 9, "sept": 9, "september": 9, "oct": 10, "october": 10,
    "nov": 11, "november": 11, "dec": 12, "december": 12
}

CURRENT_KEYWORDS = {"present", "current", "till date", "now", "ongoing", "to date"}

class ExperienceAnalyzer:
    """
    Analyzes professional experience from resume text and intervals,
    coalesces overlapping dates to prevent double-counting, and scores alignment against JD.
    """
    
    def __init__(self, current_year: int = 2026, current_month: int = 11):
        self.current_year = current_year
        self.current_month = current_month

    def parse_date_token(self, token: str) -> Optional[Tuple[int, int]]:
        """Parse year and month from a date token string."""
        token = token.strip().lower()
        if any(curr in token for curr in CURRENT_KEYWORDS):
            return (self.current_year, self.current_month)
            
        # Match 'Month Year' or 'Month, Year' (e.g. 'Jan 2021', 'March 2019')
        m_match = re.match(r'([a-z]+)[,\s]+(\d{4})', token)
        if m_match:
            month_str, year_str = m_match.groups()
            month = MONTH_MAP.get(month_str[:3], 1)
            year = int(year_str)
            if 1970 <= year <= self.current_year:
                return (year, month)
                
        # Match 'MM/YYYY' or 'MM-YYYY'
        num_match = re.match(r'(\d{1,2})[\/\-](\d{4})', token)
        if num_match:
            month_str, year_str = num_match.groups()
            month = max(1, min(12, int(month_str)))
            year = int(year_str)
            if 1970 <= year <= self.current_year:
                return (year, month)
                
        # Match standalone 'YYYY' (e.g. '2019')
        year_match = re.match(r'\b(19\d{2}|20\d{2})\b', token)
        if year_match:
            year = int(year_match.group(1))
            if 1970 <= year <= self.current_year:
                return (year, 1) # Default to start of year
                
        return None

    def extract_date_intervals(self, text: str) -> List[Tuple[Tuple[int, int], Tuple[int, int], str]]:
        """
        Extract date ranges from text (e.g. 'Jan 2019 - Mar 2022', '2018 - Present').
        Returns list of ((start_yr, start_mo), (end_yr, end_mo), raw_match_str).
        """
        # Patterns for date ranges
        pattern = re.compile(
            r'([a-z]+[\s,]+\d{4}|\d{1,2}[\/\-]\d{4}|\b(?:19|20)\d{2}\b)'
            r'\s*(?:-|–|—|to|until)\s*'
            r'([a-z]+[\s,]+\d{4}|\d{1,2}[\/\-]\d{4}|\b(?:19|20)\d{2}\b|present|current|now|till\s+date)',
            re.IGNORECASE
        )
        
        intervals = []
        for line in text.splitlines():
            matches = pattern.findall(line)
            for start_str, end_str in matches:
                start_pt = self.parse_date_token(start_str)
                end_pt = self.parse_date_token(end_str)
                if start_pt and end_pt:
                    # Ensure start <= end
                    if start_pt <= end_pt:
                        intervals.append((start_pt, end_pt, f"{start_str} - {end_str}"))
                    else:
                        # Reversed dates in text
                        intervals.append((end_pt, start_pt, f"{end_str} - {start_str}"))
        return intervals

    def coalesce_intervals(self, intervals: List[Tuple[Tuple[int, int], Tuple[int, int], str]]) -> float:
        """
        Merge overlapping and contiguous date intervals to calculate genuine non-overlapping tenure.
        Returns total experience in years (rounded to 1 decimal place).
        """
        if not intervals:
            return 0.0
            
        # Convert to month indices from year 1970 (1970 * 12 + 1)
        month_ranges = []
        for start, end, _ in intervals:
            s_idx = start[0] * 12 + start[1]
            e_idx = end[0] * 12 + end[1]
            month_ranges.append((s_idx, e_idx))
            
        # Sort by start index
        month_ranges.sort(key=lambda x: x[0])
        
        # Merge overlapping
        merged = []
        for s, e in month_ranges:
            if not merged:
                merged.append([s, e])
            else:
                prev_s, prev_e = merged[-1]
                if s <= prev_e + 1:  # Overlapping or contiguous
                    merged[-1][1] = max(prev_e, e)
                else:
                    merged.append([s, e])
                    
        total_months = sum(e - s + 1 for s, e in merged)
        total_years = round(total_months / 12.0, 1)
        return total_years

    def analyze_experience(
        self, resume_exp_text: str, full_resume_text: str, required_years: float
    ) -> Dict[str, Any]:
        """
        Comprehensive experience analysis against JD requirement.
        """
        # Prioritize experience section, fallback to full text
        target_text = resume_exp_text if resume_exp_text.strip() else full_resume_text
        intervals = self.extract_date_intervals(target_text)
        cand_years = self.coalesce_intervals(intervals)
        
        # If no intervals detected via date ranges, check for explicit statements like "5 years of experience"
        is_inferred = False
        if cand_years == 0.0:
            exp_mention = re.search(r'(\d{1,2}(?:\.\d)?)\s*\+?\s*(?:years?|yrs?)(?:\s+of)?(?:\s+experience)?', target_text, re.I)
            if exp_mention:
                try:
                    val = float(exp_mention.group(1))
                    if 0.5 <= val <= 35:
                        cand_years = val
                        is_inferred = True
                except ValueError:
                    pass
                    
        has_section = bool(resume_exp_text.strip()) or cand_years > 0.0
        gap_years = round(cand_years - required_years, 1)
        
        # Scoring logic
        if required_years <= 0.0:
            # Entry level role with no tenure prerequisite
            score = 100.0
            explanation = "No minimum experience required by the position; full baseline score awarded."
        elif not has_section and cand_years == 0.0:
            score = 0.0
            explanation = "Experience section or dates could not be verified in the candidate document."
        elif cand_years >= required_years:
            score = 100.0
            explanation = f"Candidate satisfies required tenure ({cand_years} verified years vs {required_years} years required)."
        else:
            # Partial fulfillment formula
            ratio = cand_years / required_years
            score = round(max(0.0, min(100.0, 100.0 * (ratio ** 1.2))), 1)
            explanation = (
                f"Candidate has {cand_years} years of verified experience ({round(ratio*100)}% of required {required_years} years). "
                f"Experience deficit: {abs(gap_years)} years."
            )
            
        return {
            "score": score,
            "candidate_years": cand_years,
            "required_years": required_years,
            "gap_years": gap_years,
            "has_experience_section": has_section,
            "is_inferred": is_inferred,
            "intervals_detected": len(intervals),
            "raw_intervals": [raw for _, _, raw in intervals],
            "explanation": explanation
        }
