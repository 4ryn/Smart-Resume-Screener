import sqlite3
import ollama
from config import OLLAMA_MODEL, DB_PATH

def summarize_job_description(jd_text):
    """Uses Ollama LLM to extract key skills, experience, and qualifications from JD."""
    prompt = f"""
    Extract and summarize key elements from the following job description:
    
    Job Description:
    {jd_text}

    Provide the summary in the following structured format:
    Skills: (comma-separated list)
    Experience: (years required)
    Qualifications: (list the required degrees, certifications, etc.)
    
    """

    response = ollama.chat(model=OLLAMA_MODEL, messages=[{"role": "user", "content": prompt}])
    
    return response["message"]["content"]  
def process_job_descriptions():
    """Fetches JDs from SQLite, summarizes them using Ollama, and updates the database."""
    # Connect to SQLite
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Fetch job descriptions that have not been summarized
    cursor.execute("SELECT id, job_description FROM jobs WHERE jd_summary IS NULL")
    jobs = cursor.fetchall()
    
    if not jobs:
        print("All JDs are already summarized.")
        return

    # Process each JD
    for job_id, jd_text in jobs:
        summary = summarize_job_description(jd_text)

        # Update database with the summary
        cursor.execute("UPDATE jobs SET jd_summary = ? WHERE id = ?", (summary, job_id))
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    print("Job descriptions summarized and stored in the database.")

if __name__ == "__main__":
    process_job_descriptions()