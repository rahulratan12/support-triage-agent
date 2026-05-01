import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

sample_df = pd.read_csv("data/sample_support_tickets.csv")

corpus = sample_df["issue"].fillna("").tolist()

vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(corpus)

def retrieve_similar(issue):
    vec = vectorizer.transform([issue])
    sim = cosine_similarity(vec, X)
    idx = sim.argmax()
    score = sim[0][idx]

    if score > 0.3:
        return sample_df.iloc[idx]

    return None