import sqlite3
import ollama
from config import OLLAMA_MODEL, DB_PATH
import numpy as np

def extract_skills_from_cv(cv_text):
    """Extract skills and experience using LLM."""
    prompt = f"""
    Extract key skills and years of experience from the following CV:

    {cv_text}

    Provide the output in structured format:
    Skills: (comma-separated list)
    Experience: (years of experience)
    """

    try:
        response = ollama.chat(model=OLLAMA_MODEL, messages=[{"role": "user", "content": prompt}])
        return response["message"]["content"]
    except Exception as e:
        print(f"LLM error extracting skills: {e}")
        return "Skills: , Experience: 0"

def get_embedding(text):
    """Safely get embedding from Ollama."""
    try:
        result = ollama.embeddings(model=OLLAMA_MODEL, prompt=text)
        return np.array(result["embedding"])
    except Exception as e:
        print(f"Embedding error: {e}")
        return np.zeros(4096)

def cosine_similarity(a, b):
    """Computes cosine similarity between two numpy vectors."""
    if np.linalg.norm(a) == 0 or np.linalg.norm(b) == 0:
        return 0.0
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

def compute_match_score(jd_summary, cv_summary):
    """Computes cosine similarity between JD and CV summaries."""
    emb_jd = get_embedding(jd_summary)
    emb_cv = get_embedding(cv_summary)
    similarity = cosine_similarity(emb_jd, emb_cv)
    return round(similarity * 100, 2) 

def process_candidate_matching():
    """Matches candidates with jobs based on skills and semantic embeddings."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Fetch all unscreened candidates
    cursor.execute("SELECT id, cv_text FROM candidates WHERE match_score IS NULL")
    candidates = cursor.fetchall()

    # Fetch job summaries
    cursor.execute("SELECT id, jd_summary FROM jobs WHERE jd_summary IS NOT NULL")
    jobs = cursor.fetchall()

    if not candidates or not jobs:
        print("No candidates or job descriptions available.")
        return

    print(f"🔍 Processing {len(candidates)} candidates against {len(jobs)} jobs...")

    for candidate_id, cv_text in candidates:
        print(f"📋 Processing candidate {candidate_id}...")
        
        # Extract summarized CV content
        cv_summary = extract_skills_from_cv(cv_text)

        best_score = 0
        best_job_id = None

        for job_id, jd_summary in jobs:
            score = compute_match_score(jd_summary, cv_summary)
            print(f"  Job {job_id}: {score}% match")

            if score > best_score:
                best_score = score
                best_job_id = job_id

        # Store match result
        try:
            cursor.execute(
                "UPDATE candidates SET match_score = ?, matched_job_id = ? WHERE id = ?",
                (best_score, best_job_id, candidate_id)
            )
            print(f"✅ Candidate {candidate_id} matched to job {best_job_id} with score {best_score}%")
        except Exception as e:
            print(f"❌ DB error updating match for candidate {candidate_id}: {e}")

    conn.commit()
    conn.close()
    print("🎉 Matching process complete.")

if __name__ == "__main__":
    process_candidate_matching()
