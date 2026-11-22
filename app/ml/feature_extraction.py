import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.ml.preprocessing import preprocess_text


def compute_tfidf_similarity(resume_text: str, job_text: str) -> dict:
    """
    Computes TF-IDF vectors for resume text and job description,
    calculates Cosine Similarity, and identifies top shared vocabulary keywords.

    Returns:
    {
        "similarity": 0.74,         # Normalized cosine similarity in [0.0, 1.0]
        "percentage": 74.0,         # Scaled 0 - 100
        "top_shared_terms": [...],  # Top overlapping terms by TF-IDF weight
        "feature_count": int        # Total features extracted
    }
    """
    clean_resume = preprocess_text(resume_text)
    clean_job = preprocess_text(job_text)

    if not clean_resume or not clean_job:
        return {
            "similarity": 0.0,
            "percentage": 0.0,
            "top_shared_terms": [],
            "feature_count": 0,
        }

    corpus = [clean_resume, clean_job]

    try:
        vectorizer = TfidfVectorizer(
            max_features=5000,
            ngram_range=(1, 2),
            stop_words="english",
            norm="l2",
            sublinear_tf=True,
        )

        tfidf_matrix = vectorizer.fit_transform(corpus)
        sim_matrix = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
        score = float(sim_matrix[0][0])
        score = max(0.0, min(1.0, score))  # Clamp between 0.0 and 1.0

        # Extract top shared salient keywords
        feature_names = np.array(vectorizer.get_feature_names_out())
        vec_resume = tfidf_matrix[0].toarray()[0]
        vec_job = tfidf_matrix[1].toarray()[0]

        # Shared weight is the product of their TF-IDF scores
        overlap_weights = vec_resume * vec_job
        top_indices = np.argsort(overlap_weights)[::-1]

        shared_terms = []
        for idx in top_indices:
            if overlap_weights[idx] > 0 and len(shared_terms) < 12:
                shared_terms.append(str(feature_names[idx]))

        return {
            "similarity": round(score, 4),
            "percentage": round(score * 100, 1),
            "top_shared_terms": shared_terms,
            "feature_count": int(tfidf_matrix.shape[1]),
        }
    except Exception as e:
        # Fallback graceful handler
        return {
            "similarity": 0.0,
            "percentage": 0.0,
            "top_shared_terms": [],
            "feature_count": 0,
            "error": str(e),
        }


def extract_key_phrases(text: str, top_n: int = 15) -> list[str]:
    """Extract top TF-IDF keywords/phrases from a single document."""
    preprocessed = preprocess_text(text)
    if not preprocessed:
        return []

    try:
        vectorizer = TfidfVectorizer(
            max_features=5000,
            ngram_range=(1, 2),
            stop_words="english",
        )
        matrix = vectorizer.fit_transform([preprocessed])
        feature_names = vectorizer.get_feature_names_out()
        scores = matrix.toarray()[0]
        top_indices = np.argsort(scores)[::-1][:top_n]
        return [feature_names[i] for i in top_indices if scores[i] > 0]
    except Exception:
        return []
