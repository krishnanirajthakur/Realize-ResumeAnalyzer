"""
Classical Supervised Machine Learning Benchmark and Evaluation Engine
"""
from typing import Dict, List, Tuple, Any, Optional
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report
)

class ModelEvaluator:
    """
    Evaluates classical supervised ML models (Logistic Regression, Linear SVM)
    on labeled resume/candidate datasets with genuine empirical metrics.
    """
    
    def __init__(self, model_type: str = "logistic_regression", test_size: float = 0.25, random_state: int = 42):
        self.model_type = model_type
        self.test_size = test_size
        self.random_state = random_state
        self.vectorizer = TfidfVectorizer(max_features=1000, ngram_range=(1, 2), stop_words='english')
        
        if model_type == "linear_svm":
            self.model = LinearSVC(C=1.0, random_state=random_state)
        else:
            self.model = LogisticRegression(C=1.0, max_iter=500, random_state=random_state)
            
    def train_and_evaluate(
        self, df: pd.DataFrame, text_col: str = "text", label_col: str = "label"
    ) -> Dict[str, Any]:
        """
        Train classical classifier and produce genuine evaluation metrics and feature coefficients.
        """
        # Data validation
        if text_col not in df.columns or label_col not in df.columns:
            raise ValueError(f"Columns '{text_col}' and '{label_col}' must exist in the dataset.")
            
        clean_df = df.dropna(subset=[text_col, label_col])
        if len(clean_df) < 10:
            raise ValueError("Dataset requires at least 10 labeled samples for training and evaluation.")
            
        X_raw = clean_df[text_col].astype(str)
        y_raw = clean_df[label_col]
        
        # Check class distribution
        unique_labels = np.unique(y_raw)
        if len(unique_labels) < 2:
            raise ValueError("Dataset must contain at least two target classes (e.g. 0/1 or fit/unfit).")
            
        X_train, X_test, y_train, y_test = train_test_split(
            X_raw, y_raw, test_size=self.test_size, random_state=self.random_state, stratify=y_raw
        )
        
        # TF-IDF Vectorization
        X_train_vec = self.vectorizer.fit_transform(X_train)
        X_test_vec = self.vectorizer.transform(X_test)
        
        # Model Training
        self.model.fit(X_train_vec, y_train)
        y_pred = self.model.predict(X_test_vec)
        
        # Compute Genuine Metrics
        acc = float(accuracy_score(y_test, y_pred))
        prec = float(precision_score(y_test, y_pred, average='weighted', zero_division=0))
        rec = float(recall_score(y_test, y_pred, average='weighted', zero_division=0))
        f1 = float(f1_score(y_test, y_pred, average='weighted', zero_division=0))
        cm = confusion_matrix(y_test, y_pred).tolist()
        report = classification_report(y_test, y_pred, output_dict=True, zero_division=0)
        
        # Extract Feature Importance / Top Coefficients
        feature_names = self.vectorizer.get_feature_names_out()
        top_features: List[Tuple[str, float]] = []
        
        if hasattr(self.model, "coef_"):
            coefs = self.model.coef_[0] if len(self.model.coef_.shape) > 1 else self.model.coef_
            sorted_idx = np.argsort(coefs)
            
            # Top positive and negative predictors
            top_pos = [(feature_names[i], round(float(coefs[i]), 4)) for i in sorted_idx[-10:][::-1]]
            top_neg = [(feature_names[i], round(float(coefs[i]), 4)) for i in sorted_idx[:10]]
            top_features = top_pos
        else:
            top_neg = []
            
        return {
            "model_type": self.model_type,
            "sample_count": len(clean_df),
            "train_size": len(X_train),
            "test_size": len(X_test),
            "classes": [str(c) for c in unique_labels],
            "metrics": {
                "accuracy": round(acc * 100.0, 2),
                "precision": round(prec * 100.0, 2),
                "recall": round(rec * 100.0, 2),
                "f1_score": round(f1 * 100.0, 2)
            },
            "confusion_matrix": cm,
            "classification_report": report,
            "top_positive_features": top_features,
            "top_negative_features": top_neg,
        }
