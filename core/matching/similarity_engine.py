"""
TF-IDF Lexical Similarity Engine
"""
from typing import Dict, List, Tuple, Any
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from core.preprocessing.text_cleaner import clean_text

class SimilarityEngine:
    """
    Computes lexical similarity between candidate resumes and job descriptions using
    classical TF-IDF N-Gram Vectorization and Cosine Distance.
    
    Explicit Note: This measures lexical vocabulary and n-gram overlap;
    it is deterministic and does not claim black-box semantic reasoning.
    """
    
    def __init__(self, ngram_range: Tuple[int, int] = (1, 2), sublinear_tf: bool = True):
        self.ngram_range = ngram_range
        self.sublinear_tf = sublinear_tf
        
    def compute_similarity(self, resume_text: str, jd_text: str) -> Dict[str, Any]:
        """
        Compute TF-IDF cosine similarity percentage and top overlapping terms.
        
        Returns:
            {
                "similarity_score": float (0.0 to 100.0),
                "cosine_coefficient": float (0.0 to 1.0),
                "top_matching_terms": List[Tuple[str, float]],
                "resume_vocab_size": int,
                "jd_vocab_size": int,
                "explanation": str
            }
        """
        res_clean = clean_text(resume_text).strip()
        jd_clean = clean_text(jd_text).strip()
        
        if not res_clean or not jd_clean:
            return {
                "similarity_score": 0.0,
                "cosine_coefficient": 0.0,
                "top_matching_terms": [],
                "resume_vocab_size": 0,
                "jd_vocab_size": 0,
                "explanation": "Insufficient text content in resume or job description to compute lexical similarity."
            }
            
        vectorizer = TfidfVectorizer(
            ngram_range=self.ngram_range,
            sublinear_tf=self.sublinear_tf,
            stop_words='english',
            token_pattern=r'(?u)\b[a-zA-Z0-9_\-\.\+#]{2,}\b'
        )
        
        try:
            tfidf_matrix = vectorizer.fit_transform([res_clean, jd_clean])
            feature_names = np.array(vectorizer.get_feature_names_out())
            
            # Cosine similarity between row 0 (resume) and row 1 (JD)
            sim_matrix = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
            raw_cosine = float(sim_matrix[0][0])
            
            # Clamp between 0.0 and 1.0
            clamped_cosine = max(0.0, min(1.0, raw_cosine))
            similarity_pct = round(clamped_cosine * 100.0, 2)
            
            # Identify top overlapping terms (element-wise product of TF-IDF vectors)
            res_vec = tfidf_matrix[0].toarray().flatten()
            jd_vec = tfidf_matrix[1].toarray().flatten()
            product = res_vec * jd_vec
            
            # Top indices with non-zero mutual weight
            non_zero_indices = np.where(product > 0)[0]
            top_terms: List[Tuple[str, float]] = []
            
            if len(non_zero_indices) > 0:
                sorted_idx = non_zero_indices[np.argsort(product[non_zero_indices])[::-1]]
                for idx in sorted_idx[:15]:
                    term = feature_names[idx]
                    weight = round(float(product[idx]), 4)
                    top_terms.append((term, weight))
                    
            explanation = (
                f"Lexical similarity computed at {similarity_pct}% based on TF-IDF cosine distance "
                f"over unigrams and bigrams. {len(top_terms)} shared salient terms identified."
            )
            
            return {
                "similarity_score": similarity_pct,
                "cosine_coefficient": round(clamped_cosine, 4),
                "top_matching_terms": top_terms,
                "resume_vocab_size": int(np.count_nonzero(res_vec)),
                "jd_vocab_size": int(np.count_nonzero(jd_vec)),
                "explanation": explanation
            }
            
        except Exception as e:
            return {
                "similarity_score": 0.0,
                "cosine_coefficient": 0.0,
                "top_matching_terms": [],
                "resume_vocab_size": 0,
                "jd_vocab_size": 0,
                "explanation": f"Error computing TF-IDF similarity: {str(e)}"
            }
