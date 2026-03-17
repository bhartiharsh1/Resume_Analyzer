from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def calculate_ats_score(resume_text, job_desc):
    documents = [resume_text, job_desc]

    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(documents)

    score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])

    return round(score[0][0] * 100, 2)