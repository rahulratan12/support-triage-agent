import os

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "sample_support_tickets.csv")

try:
    sample_df = pd.read_csv(_PATH)
    sample_df.columns = [c.strip().lower() for c in sample_df.columns]
    _corpus = sample_df["issue"].fillna("").tolist()
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(_corpus)
except Exception:  # missing/invalid sample file -> fall back to templates
    sample_df = None


def retrieve_similar(issue):
    if sample_df is None or "response" not in sample_df.columns:
        return None
    vec = vectorizer.transform([issue])
    sim = cosine_similarity(vec, X)
    idx = sim.argmax()
    if sim[0][idx] > 0.3:
        return sample_df.iloc[idx]
    return None
