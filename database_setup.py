import sqlite3

# Database file path
DB_PATH = "recruitment.db"

def connect_db():
    """Establish a connection to the SQLite database."""
    return sqlite3.connect(DB_PATH)

def create_tables():
    """Create necessary tables if they do not exist."""
    with connect_db() as conn:
        cursor = conn.cursor()

        # Create jobs table with job summary
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL,
            job_description TEXT NOT NULL,
            jd_summary TEXT DEFAULT NULL
        );
        ''')

        # Create candidates table with match score & matched job ID
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT DEFAULT NULL,
            cv_text TEXT NOT NULL,
            match_score REAL DEFAULT NULL,
            matched_job_id INTEGER DEFAULT NULL,
            FOREIGN KEY(matched_job_id) REFERENCES jobs(id)
        );
        ''')

        # Create shortlisted candidates table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS shortlisted_candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id INTEGER NOT NULL,
            name TEXT,
            candidate_id INTEGER NOT NULL,
            match_score REAL DEFAULT NULL,
            email TEXT DEFAULT NULL,
            FOREIGN KEY(job_id) REFERENCES jobs(id),
            FOREIGN KEY(candidate_id) REFERENCES candidates(id)
        );
        ''')

        conn.commit()
        print("Tables created successfully!")
        

def add_missing_columns():
    """Check for missing columns and add them dynamically."""
    with connect_db() as conn:
        cursor = conn.cursor()

        # Helper function to check and add columns
        def check_and_add_column(table, column, column_type):
            cursor.execute(f"PRAGMA table_info({table})")
            columns = [col[1] for col in cursor.fetchall()]
            if column not in columns:
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {column_type} DEFAULT NULL")
                print(f"Column '{column}' added to '{table}' table.")

        # Adding missing columns if they don’t exist
        check_and_add_column("jobs", "jd_summary", "TEXT")
        check_and_add_column("candidates", "email", "TEXT")
        check_and_add_column("candidates", "match_score", "REAL")
        check_and_add_column("candidates", "matched_job_id", "INTEGER")
        check_and_add_column("shortlisted_candidates", "match_score", "REAL")
        check_and_add_column("shortlisted_candidates", "email", "TEXT")

        conn.commit()
        print("All necessary columns are ensured!")

if __name__ == "__main__":
    create_tables()
    add_missing_columns()
    print(" SQLite Database & Tables Setup Completed Successfully!")
