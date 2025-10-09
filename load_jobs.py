import pandas as pd
import sqlite3
import os

from config import DB_PATH

CSV_FILE_PATH = "data/job_description.csv" 
def load_job_descriptions():
    if not os.path.exists(CSV_FILE_PATH):
        print(f"File not found: {CSV_FILE_PATH}")
        return

    try:
        df = pd.read_csv(CSV_FILE_PATH, encoding="utf-8-sig")
    except UnicodeDecodeError:
        df = pd.read_csv(CSV_FILE_PATH, encoding="cp1252")  


    # Column check
    required_cols = ["Job Title", "Job Description"]
    if not all(col in df.columns for col in required_cols):
        print("CSV must contain columns: 'Job Title' and 'Job Description'")
        return

    # DB connection
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Clear existing job-related data for fresh processing
    print("🗑️  Clearing existing job data...")
    
    # Get count before clearing
    cursor.execute("SELECT COUNT(*) FROM jobs")
    jobs_before = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM shortlisted_candidates")
    shortlist_before = cursor.fetchone()[0]
    
    print(f"📊 Before clearing - Jobs: {jobs_before}, Shortlisted: {shortlist_before}")
    
    cursor.execute("DELETE FROM jobs")
    cursor.execute("DELETE FROM shortlisted_candidates")
    # Reset match scores in candidates table
    cursor.execute("UPDATE candidates SET match_score = NULL, matched_job_id = NULL")
    
    # Reset auto-increment for clean IDs
    cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('jobs', 'shortlisted_candidates')")
    
    conn.commit()
    print("✅ Existing job data cleared.")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_title TEXT NOT NULL,
            job_description TEXT NOT NULL,
            jd_summary TEXT DEFAULT NULL
        )
    """)

    # Insert rows with error handling
    insert_count = 0
    for index, row in df.iterrows():
        try:
            title = str(row["Job Title"]).strip()
            desc = str(row["Job Description"]).strip()
            if title and desc:
                cursor.execute(
                    "INSERT INTO jobs (job_title, job_description) VALUES (?, ?)",
                    (title, desc)
                )
                insert_count += 1
                print(f"✅ Inserted job: {title}")
        except Exception as e:
            print(f"Failed to insert row {index}: {e}")

    conn.commit()
    conn.close()

    print(f"🎉 {insert_count} job descriptions successfully loaded into the database.")


if __name__ == "__main__":
    load_job_descriptions()
