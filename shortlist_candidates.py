import sqlite3
from config import DB_PATH

def shortlist_candidates(threshold=50):
    """
    Shortlists candidates with match score ≥ threshold and stores them
    in 'shortlisted_candidates' table, avoiding duplicates.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create table if it doesn't exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS shortlisted_candidates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        candidate_id INTEGER,
        name TEXT,
        email TEXT,
        job_id INTEGER,
        match_score REAL,
        UNIQUE(candidate_id, job_id),
        FOREIGN KEY(candidate_id) REFERENCES candidates(id),
        FOREIGN KEY(job_id) REFERENCES jobs(id)
    )
    """)

    # Fetch candidates who meet the score threshold
    cursor.execute("""
        SELECT id, name, email, matched_job_id, match_score 
        FROM candidates 
        WHERE match_score >= ?
    """, (threshold,))
    shortlisted = cursor.fetchall()

    if not shortlisted:
        print(f"No candidates met the {threshold}% threshold.")
        conn.close()
        return

    # Insert shortlisted candidates, avoiding duplicates
    for candidate_id, name, email, job_id, score in shortlisted:
        cursor.execute("""
            INSERT OR IGNORE INTO shortlisted_candidates 
            (candidate_id, name, email, job_id, match_score)
            VALUES (?, ?, ?, ?, ?)
        """, (candidate_id, name, email, job_id, score))

    conn.commit()
    conn.close()
    print(f"{len(shortlisted)} candidates shortlisted with match score ≥ {threshold}%.")

# Run the function
if __name__ == "__main__":
    shortlist_candidates()
