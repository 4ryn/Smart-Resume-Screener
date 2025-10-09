import sqlite3
from config import DB_PATH

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_all_jobs():
    """Fetch all jobs from database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM jobs ORDER BY id DESC")
    jobs = [dict(row) for row in cursor.fetchall()]
    conn.close()
    print(f"📊 Database query returned {len(jobs)} jobs")
    return jobs

def get_all_candidates():
    """Fetch all candidates from database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM candidates ORDER BY id DESC")
    candidates = [dict(row) for row in cursor.fetchall()]
    conn.close()
    print(f"📊 Database query returned {len(candidates)} candidates")
    return candidates

def get_matched_candidates():
    """Fetch candidates with match scores"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.id, c.name, c.email, c.match_score, c.matched_job_id,
               j.job_title as job_title
        FROM candidates c
        LEFT JOIN jobs j ON c.matched_job_id = j.id
        WHERE c.match_score IS NOT NULL
        ORDER BY c.match_score DESC
    """)
    matches = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return matches

def get_shortlisted_candidates():
    """Fetch shortlisted candidates"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT sc.id, sc.name, sc.email, sc.match_score, sc.email_sent,
               j.job_title as job_title, j.id as job_id
        FROM shortlisted_candidates sc
        LEFT JOIN jobs j ON sc.job_id = j.id
        ORDER BY sc.match_score DESC
    """)
    shortlist = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return shortlist

def get_dashboard_stats():
    """Get statistics for dashboard"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Total jobs
    cursor.execute("SELECT COUNT(*) as count FROM jobs")
    total_jobs = cursor.fetchone()['count']
    
    # Total candidates
    cursor.execute("SELECT COUNT(*) as count FROM candidates")
    total_candidates = cursor.fetchone()['count']
    
    print(f"📊 Dashboard stats - Jobs: {total_jobs}, Candidates: {total_candidates}")
    
    # Total shortlisted
    cursor.execute("SELECT COUNT(*) as count FROM shortlisted_candidates")
    total_shortlisted = cursor.fetchone()['count']
    
    # Average match score
    cursor.execute("SELECT AVG(match_score) as avg FROM candidates WHERE match_score IS NOT NULL")
    avg_score = cursor.fetchone()['avg'] or 0
    
    # Jobs with summaries
    cursor.execute("SELECT COUNT(*) as count FROM jobs WHERE jd_summary IS NOT NULL")
    summarized_jobs = cursor.fetchone()['count']
    
    # Emails sent
    cursor.execute("SELECT COUNT(*) as count FROM shortlisted_candidates WHERE email_sent = 1")
    emails_sent = cursor.fetchone()['count']
    
    conn.close()
    
    return {
        'total_jobs': total_jobs,
        'total_candidates': total_candidates,
        'total_shortlisted': total_shortlisted,
        'avg_match_score': round(avg_score, 2),
        'summarized_jobs': summarized_jobs,
        'emails_sent': emails_sent
    }