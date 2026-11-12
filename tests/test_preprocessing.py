"""
Tests for Text Preprocessing, Tokenization, and Section Segmentation
"""
from core.preprocessing.text_cleaner import clean_text, extract_contact_info, extract_candidate_name
from core.preprocessing.tokenizer import tokenize_words, remove_stopwords
from core.preprocessing.section_extractor import extract_sections

def test_clean_text_normalization():
    dirty_text = "Experienced\xa0Engineer with   multiple \uf0b7 bullet\tpoints and \u201csmart quotes\u201d."
    cleaned = clean_text(dirty_text)
    assert "\xa0" not in cleaned
    assert "\uf0b7" not in cleaned
    assert "•" in cleaned
    assert '"smart quotes"' in cleaned

def test_extract_contact_info():
    text = "John Doe\nEmail: john.doe@example.org\nPhone: (555) 234-5678\nSummary of work."
    email, phone = extract_contact_info(text)
    assert email == "john.doe@example.org"
    assert "555" in phone and "234" in phone

def test_extract_candidate_name():
    text = "Dr. Elena Rostova\nSenior AI Scientist\nelena@example.com"
    name = extract_candidate_name(text)
    assert "Elena" in name

def test_tokenize_preserves_tech_symbols():
    text = "Specialist in C++, C#, .NET Core, Node.js, and CI/CD automation."
    tokens = tokenize_words(text)
    assert "c++" in tokens
    assert "c#" in tokens
    assert ".net" in tokens
    assert "ci/cd" in tokens

def test_section_extractor():
    text = """
    Jane Smith
    Technical Skills:
    Python, SQL, Docker
    
    Work Experience:
    Software Engineer at Acme Corp (2020 - 2023)
    
    Educational Qualifications:
    B.S. in Computer Science
    
    Key Projects:
    Built web platform.
    """
    sections = extract_sections(text)
    assert "skills" in sections
    assert "Python, SQL, Docker" in sections["skills"]
    assert "Software Engineer" in sections["experience"]
    assert "Computer Science" in sections["education"]
    assert "web platform" in sections["projects"]
