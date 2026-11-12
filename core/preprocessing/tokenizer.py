"""
Tokenizer, Lemmatizer, and Keyword Preservation
"""
import re
from typing import List, Set

TECH_PROTECTED_TOKENS = {
    "c++", "c#", ".net", "node.js", "next.js", "vue.js", "react.js", "angular.js",
    "ci/cd", "tcp/ip", "rest", "sql", "nosql", "aws", "gcp", "azure", "k8s",
    "r&d", "et/etl", "scrum", "agile", "tdd", "devops", "ml", "ai", "nlp"
}

# Standard English stopwords
STANDARD_STOPWORDS: Set[str] = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can't", "cannot", "could", "couldn't",
    "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during",
    "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't",
    "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here",
    "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i",
    "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's",
    "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself",
    "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought",
    "our", "ours", "ourselves", "out", "over", "own", "same", "shan't", "she",
    "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such", "than",
    "that", "that's", "the", "their", "theirs", "them", "themselves", "then", "there",
    "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this",
    "those", "through", "to", "too", "under", "until", "up", "very", "was", "wasn't",
    "we", "we'd", "we'll", "we're", "we've", "were", "weren't", "what", "what's",
    "when", "when's", "where", "where's", "which", "while", "who", "who's", "whom",
    "why", "why's", "with", "won't", "would", "wouldn't", "you", "you'd", "you'll",
    "you're", "you've", "your", "yours", "yourself", "yourselves"
}

def tokenize_words(text: str) -> List[str]:
    """Tokenize text into lowercase words while preserving technical symbols like C++, C#, .NET."""
    if not text:
        return []
    
    # Pattern matches protected tech words or standard alphanumeric words
    pattern = r'(?:\b[a-zA-Z0-9]+(?:\.[a-zA-Z0-9]+)+\b|c\+\+|c\#|\.net|\b[a-zA-Z0-9_\-\/]+\b)'
    tokens = re.findall(pattern, text.lower())
    return tokens

def remove_stopwords(tokens: List[str], custom_exclusions: Set[str] = None) -> List[str]:
    """Remove standard stopwords while strictly preserving technical vocabulary."""
    exclusions = custom_exclusions or set()
    cleaned = []
    for token in tokens:
        if token in TECH_PROTECTED_TOKENS:
            cleaned.append(token)
        elif token not in STANDARD_STOPWORDS and token not in exclusions:
            if len(token) > 1 or token in {"c", "r"}:  # Preserve programming languages C and R
                cleaned.append(token)
    return cleaned

def lemmatize_tokens(tokens: List[str]) -> List[str]:
    """Safely lemmatize tokens using NLTK WordNet if available, otherwise return tokens."""
    try:
        from nltk.stem import WordNetLemmatizer
        lemmatizer = WordNetLemmatizer()
        return [lemmatizer.lemmatize(t) if t not in TECH_PROTECTED_TOKENS else t for t in tokens]
    except Exception:
        return tokens
