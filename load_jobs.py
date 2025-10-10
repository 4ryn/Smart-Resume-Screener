import pandas as pd
import sqlite3
import os
from datetime import datetime

from config import DB_PATH

CSV_FILE_PATH = "data/job_description.csv"

def validate_csv_structure(df):
    """Validate CSV has required columns and data"""
    required_cols = ["Job Title", "Job Description"]
    
    # Check for required columns (case-insensitive)
    df_cols_lower = [col.lower().strip() for col in df.columns]
    missing_cols = []
    
    for req_col in required_cols:
        if req_col.lower() not in df_cols_lower:
            missing_cols.append(req_col)
    
    if missing_cols:
        # Try to find alternative column names
        alt_mapping = {}
        for col in df.columns:
            col_lower = col.lower().strip()
            if 'title' in col_lower or 'position' in col_lower or 'role' in col_lower:
                alt_mapping['Job Title'] = col
            elif 'description' in col_lower or 'details' in col_lower or 'jd' in col_lower:
                alt_mapping['Job Description'] = col
        
        # If we found alternatives, rename them
        if len(alt_mapping) == 2:
            print(f"📝 Found alternative columns: {alt_mapping}")
            df = df.rename(columns={v: k for k, v in alt_mapping.items()})
        else:
            raise ValueError(f"Missing required columns: {missing_cols}. Found: {list(df.columns)}")
    
    # Check for empty dataframe
    if df.empty:
        raise ValueError("CSV file is empty")
    
    # Check for rows with missing data
    df = df.dropna(subset=['Job Title', 'Job Description'])
    
    if df.empty:
        raise ValueError("No valid job entries found (all rows have missing Title or Description)")
    
    return df

def clean_job_data(row):
    """Clean and validate a single job entry"""
    title = str(row["Job Title"]).strip()
    desc = str(row["Job Description"]).strip()
    
    # Remove 'nan' string values
    if title.lower() == 'nan' or not title:
        return None, None
    if desc.lower() == 'nan' or not desc:
        return None, None
    
    # Check minimum length
    if len(title) < 2:
        print(f"⚠️  Skipping job with too short title: '{title}'")
        return None, None
    
    if len(desc) < 20:
        print(f"⚠️  Skipping job '{title}' with too short description ({len(desc)} chars)")
        return None, None
    
    # Truncate if too long
    if len(title) > 200:
        title = title[:200] + "..."
        print(f"⚠️  Truncated long title to 200 chars")
    
    return title, desc

def clear_job_related_data(cursor):
    """Clear all job-related data for fresh upload"""
    print("\n🗑️  Clearing existing job data...")
    
    # Get counts before clearing
    cursor.execute("SELECT COUNT(*) FROM jobs")
    jobs_before = cursor.fetchone()[0]
    
    try:
        cursor.execute("SELECT COUNT(*) FROM shortlisted_candidates")
        shortlist_before = cursor.fetchone()[0]
    except sqlite3.OperationalError:
        shortlist_before = 0  # Table might not exist yet
    
    print(f"📊 Current data - Jobs: {jobs_before}, Shortlisted: {shortlist_before}")
    
    # Clear data
    cursor.execute("DELETE FROM jobs")
    
    try:
        cursor.execute("DELETE FROM shortlisted_candidates")
        cursor.execute("UPDATE candidates SET match_score = NULL, matched_job_id = NULL")
    except sqlite3.OperationalError:
        pass  # Tables might not exist yet
    
    # Reset auto-increment for clean IDs
    cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('jobs', 'shortlisted_candidates')")
    
    print("✅ Existing job data cleared successfully")

def ensure_tables_exist(cursor):
    """Ensure all required tables exist and have correct schema"""
    print("📋 Ensuring database tables exist...")
    
    # Check if jobs table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='jobs'")
    table_exists = cursor.fetchone() is not None
    
    if not table_exists:
        # Create new table with correct schema
        cursor.execute("""
            CREATE TABLE jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_title TEXT NOT NULL,
                job_description TEXT NOT NULL,
                jd_summary TEXT DEFAULT NULL
            )
        """)
        print("✅ Created 'jobs' table")
    else:
        # Check current schema
        cursor.execute("PRAGMA table_info(jobs)")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Check if we have 'role' instead of 'job_title'
        if 'role' in columns and 'job_title' not in columns:
            print("⚠️  Table uses 'role' column. Using compatible mode...")
            # We'll handle this in the insert statement
        elif 'job_title' not in columns:
            print("❌ ERROR: jobs table missing both 'role' and 'job_title' columns!")
            raise ValueError("Database schema incompatible")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            skills TEXT,
            experience TEXT,
            education TEXT,
            resume_text TEXT,
            match_score REAL,
            matched_job_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (matched_job_id) REFERENCES jobs(id)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS shortlisted_candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_id INTEGER NOT NULL,
            job_id INTEGER NOT NULL,
            match_score REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (candidate_id) REFERENCES candidates(id),
            FOREIGN KEY (job_id) REFERENCES jobs(id),
            UNIQUE(candidate_id, job_id)
        )
    """)
    
    print("✅ Database tables verified")

def load_job_descriptions():
    """Load job descriptions from CSV into SQLite database"""
    
    print("\n" + "="*70)
    print("🚀 LOADING JOB DESCRIPTIONS")
    print("="*70 + "\n")
    
    # Check if file exists
    if not os.path.exists(CSV_FILE_PATH):
        error_msg = f"❌ File not found: {CSV_FILE_PATH}"
        print(error_msg)
        raise FileNotFoundError(error_msg)
    
    print(f"📁 Reading CSV file: {CSV_FILE_PATH}")
    print(f"📊 File size: {os.path.getsize(CSV_FILE_PATH)} bytes")
    
    # Read CSV with multiple encoding attempts
    df = None
    encodings = ['utf-8-sig', 'utf-8', 'cp1252', 'latin1', 'iso-8859-1']
    
    for encoding in encodings:
        try:
            df = pd.read_csv(CSV_FILE_PATH, encoding=encoding)
            print(f"✅ Successfully read CSV with encoding: {encoding}")
            break
        except UnicodeDecodeError:
            continue
        except Exception as e:
            print(f"❌ Error reading CSV with {encoding}: {str(e)}")
            continue
    
    if df is None:
        raise ValueError("Could not read CSV file with any supported encoding")
    
    print(f"📊 CSV loaded: {len(df)} rows, {len(df.columns)} columns")
    print(f"📋 Columns: {list(df.columns)}")
    
    # Validate and clean CSV structure
    try:
        df = validate_csv_structure(df)
        print(f"✅ CSV validation passed: {len(df)} valid job entries")
    except ValueError as e:
        print(f"❌ CSV Validation Error: {str(e)}")
        raise
    
    # Connect to database
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        print(f"✅ Connected to database: {DB_PATH}")
    except sqlite3.Error as e:
        print(f"❌ Database connection error: {str(e)}")
        raise
    
    try:
        # Ensure tables exist
        ensure_tables_exist(cursor)
        
        # Clear existing data
        clear_job_related_data(cursor)
        conn.commit()
        
        # Insert jobs
        print(f"\n{'='*70}")
        print(f"📥 INSERTING JOB DESCRIPTIONS")
        print(f"{'='*70}\n")
        
        insert_count = 0
        skip_count = 0
        error_count = 0
        
        for index, row in df.iterrows():
            try:
                title, desc = clean_job_data(row)
                
                if title and desc:
                    # Insert without created_at for compatibility
                    cursor.execute(
                        "INSERT INTO jobs (job_title, job_description) VALUES (?, ?)",
                        (title, desc)
                    )
                    insert_count += 1
                    print(f"✅ [{insert_count}] {title[:60]}{'...' if len(title) > 60 else ''}")
                else:
                    skip_count += 1
                    
            except sqlite3.IntegrityError as e:
                print(f"⚠️  Row {index + 2}: Duplicate or constraint violation - {str(e)}")
                error_count += 1
            except Exception as e:
                print(f"❌ Row {index + 2}: Failed to insert - {str(e)}")
                error_count += 1
        
        # Commit changes
        conn.commit()
        
        # Verify insertion
        cursor.execute("SELECT COUNT(*) FROM jobs")
        final_count = cursor.fetchone()[0]
        
        # Print summary
        print(f"\n{'='*70}")
        print(f"📊 LOAD SUMMARY")
        print(f"{'='*70}")
        print(f"✅ Successfully Inserted: {insert_count}")
        print(f"⚠️  Skipped (invalid data): {skip_count}")
        print(f"❌ Errors: {error_count}")
        print(f"📝 Total in CSV: {len(df)}")
        print(f"💾 Final DB Count: {final_count}")
        print(f"{'='*70}\n")
        
        if insert_count == 0:
            print("⚠️  WARNING: No jobs were inserted into the database!")
        elif insert_count != final_count:
            print(f"⚠️  WARNING: Insert count ({insert_count}) doesn't match DB count ({final_count})")
        else:
            print(f"🎉 Success! {insert_count} job description(s) loaded into database")
        
    except Exception as e:
        print(f"\n❌ Error during database operations: {str(e)}")
        import traceback
        traceback.print_exc()
        raise
    
    finally:
        conn.close()
        print("🔒 Database connection closed\n")

if __name__ == "__main__":
    try:
        load_job_descriptions()
    except Exception as e:
        print(f"\n{'='*70}")
        print(f"❌ FATAL ERROR")
        print(f"{'='*70}")
        print(f"Error: {str(e)}")
        print(f"{'='*70}\n")
        exit(1)