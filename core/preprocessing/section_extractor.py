"""
Deterministic Section Boundary Detection and Segmentation
"""
import re
from typing import Dict, List, Tuple

SECTION_KEYWORDS = {
    "skills": [
        r'\btechnical\s+skills\b', r'\bcore\s+competencies\b', r'\bskills\s*(?:&|and)\s*expertise\b',
        r'\bkey\s+skills\b', r'\btechnologies\b', r'\btools\s*(?:&|and)\s*technologies\b',
        r'\bskills\b', r'\bcompetencies\b', r'\btechnical\s+proficiencies\b'
    ],
    "experience": [
        r'\bprofessional\s+experience\b', r'\bwork\s+experience\b', r'\bemployment\s+history\b',
        r'\bcareer\s+history\b', r'\bwork\s+history\b', r'\bexperience\b', r'\bprofessional\s+background\b'
    ],
    "education": [
        r'\beducational\s+qualifications\b', r'\bacademic\s+background\b', r'\beducation\b',
        r'\bqualifications\b', r'\bacademic\s+history\b', r'\bdegrees?\b'
    ],
    "projects": [
        r'\bkey\s+projects\b', r'\bacademic\s+projects\b', r'\bpersonal\s+projects\b',
        r'\btechnical\s+projects\b', r'\bprojects\b', r'\bportfolio\b'
    ],
    "certifications": [
        r'\bcertifications?\s*(?:&|and)\s*licenses?\b', r'\bcertifications?\b',
        r'\bprofessional\s+certifications?\b', r'\bcredentials\b'
    ],
    "summary": [
        r'\bprofessional\s+summary\b', r'\bexecutive\s+summary\b', r'\bcareer\s+objective\b',
        r'\bobjective\b', r'\babout\s+me\b', r'\bprofile\b', r'\bsummary\b'
    ]
}

def extract_sections(text: str) -> Dict[str, str]:
    """Segment document text into distinct logical sections using heading pattern anchors."""
    lines = text.splitlines()
    detected_headers: List[Tuple[int, str]] = []
    
    # Identify heading lines
    for idx, line in enumerate(lines):
        clean_line = line.strip().lower()
        # Heading lines are typically short (1-5 words), often uppercase or title-case, or preceded/followed by whitespace
        if 2 <= len(clean_line) <= 45 and not clean_line.endswith(('.', ',')):
            # Check against section keywords
            for sec_name, patterns in SECTION_KEYWORDS.items():
                for pat in patterns:
                    if re.fullmatch(pat, clean_line) or re.match(r'^(?:[0-9\.\-\#\*\•\s]+)?' + pat + r'[:\s\-]*$', clean_line):
                        detected_headers.append((idx, sec_name))
                        break
                else:
                    continue
                break

    # Build sections dictionary
    sections: Dict[str, str] = {
        "summary": "",
        "skills": "",
        "experience": "",
        "education": "",
        "projects": "",
        "certifications": "",
        "other": ""
    }
    
    if not detected_headers:
        # If no explicit headers were detected, store full text in "other"
        sections["other"] = text
        return sections

    # Partition text between headers
    for i in range(len(detected_headers)):
        start_idx, sec_name = detected_headers[i]
        end_idx = detected_headers[i+1][0] if i + 1 < len(detected_headers) else len(lines)
        
        # Section text (skip the header line itself)
        sec_text = "\n".join(lines[start_idx+1:end_idx]).strip()
        
        # If section already has text, append
        if sections[sec_name]:
            sections[sec_name] += "\n" + sec_text
        else:
            sections[sec_name] = sec_text

    # Content before the first detected header (often contact/summary)
    first_header_idx = detected_headers[0][0]
    if first_header_idx > 0:
        header_text = "\n".join(lines[:first_header_idx]).strip()
        if not sections["summary"]:
            sections["summary"] = header_text
        else:
            sections["other"] = header_text

    return sections
