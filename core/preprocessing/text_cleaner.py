"""
Text Normalization, Sanitization, and Header Extraction
"""
import re
import unicodedata
from typing import Optional, Tuple, List

# Common ligature and quote mappings
REPLACEMENTS = {
    "\uf0b7": "•",
    "\u2022": "•",
    "\u2013": "-",
    "\u2014": "-",
    "\u2018": "'",
    "\u2019": "'",
    "\u201c": '"',
    "\u201d": '"',
    "\xa0": " ",
    "\t": " ",
}

EMAIL_REGEX = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b')
PHONE_REGEX = re.compile(
    r'(?:(?:\+?(\d{1,3}))?[-.\s]?)?(?:\(?(\d{3})\)?[-.\s]?)?(\d{3})[-.\s]?(\d{4})'
)
URL_REGEX = re.compile(r'https?://[^\s]+|www\.[^\s]+|linkedin\.com/[^\s]+|github\.com/[^\s]+')

NON_NAME_WORDS = {
    "resume", "curriculum", "vitae", "cv", "page", "profile", "summary", "contact",
    "email", "phone", "address", "experience", "education", "skills", "projects",
    "personal", "details", "objective", "work", "developer", "engineer", "lead"
}

def clean_text(raw_text: str) -> str:
    """Normalize unicode, whitespace, and non-printable characters while preserving structure."""
    if not raw_text:
        return ""
    
    # Unicode decomposition/composition
    text = unicodedata.normalize("NFKC", raw_text)
    
    for old, new in REPLACEMENTS.items():
        text = text.replace(old, new)
        
    # Remove null bytes or non-printable ASCII
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    
    # Collapse horizontal spaces, keeping newlines
    lines = [re.sub(r'[ \t]+', ' ', line).strip() for line in text.splitlines()]
    
    # Remove consecutive empty lines (leave at most one empty line for section separation)
    compact_lines = []
    prev_empty = False
    for line in lines:
        if line == "":
            if not prev_empty:
                compact_lines.append("")
                prev_empty = True
        else:
            compact_lines.append(line)
            prev_empty = False
            
    return "\n".join(compact_lines).strip()

def extract_contact_info(text: str) -> Tuple[Optional[str], Optional[str]]:
    """Extract email and phone for UI presentation only. Never used for scoring."""
    email = None
    phone = None
    
    email_match = EMAIL_REGEX.search(text)
    if email_match:
        email = email_match.group(0).strip()
        
    # Find phone
    for line in text.splitlines()[:15]:
        phone_match = PHONE_REGEX.search(line)
        if phone_match:
            candidate_phone = phone_match.group(0).strip()
            # Verify it has at least 7 digits to avoid matching random years/numbers
            digits = re.sub(r'\D', '', candidate_phone)
            if 7 <= len(digits) <= 15:
                phone = candidate_phone
                break
                
    return email, phone

def extract_candidate_name(text: str, filename: str = "") -> str:
    """Extract candidate name deterministically using top-of-resume heuristics."""
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    
    # Check top 8 non-empty lines
    for line in lines[:8]:
        # Strip phone/email if in line
        sanitized = EMAIL_REGEX.sub('', line)
        sanitized = URL_REGEX.sub('', sanitized)
        sanitized = PHONE_REGEX.sub('', sanitized)
        sanitized = re.sub(r'[^a-zA-Z\s\.\-]', ' ', sanitized).strip()
        
        words = sanitized.split()
        if 2 <= len(words) <= 4:
            # Check if any word is a non-name keyword
            lower_words = [w.lower() for w in words]
            if not any(w in NON_NAME_WORDS for w in lower_words):
                # Ensure each word starts with a capital or has reasonable length
                if all(len(w) >= 2 for w in words):
                    return " ".join([w.capitalize() for w in words])
                    
    # Fallback: extract from filename if informative
    if filename:
        clean_name = re.sub(r'(\.pdf|\.docx|\.txt|_resume|_cv|resume|cv)', '', filename, flags=re.IGNORECASE)
        clean_name = re.sub(r'[-_]', ' ', clean_name).strip()
        words = clean_name.split()
        if 1 <= len(words) <= 4 and not any(w.lower() in NON_NAME_WORDS for w in words):
            return " ".join([w.capitalize() for w in words])
            
    return "Candidate"
