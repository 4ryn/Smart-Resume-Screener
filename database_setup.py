"""
Complete database migration script to align with your existing schema
Fixes column name mismatches between your database.py and load_jobs.py
"""

import sqlite3
from config import DB_PATH

def fix_database():
    """Migrate database to ensure compatibility"""
    print("\n" + "="*70)
    print("🔧 DATABASE MIGRATION & FIX SCRIPT")
    print("="*70 + "\n")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        print(f"✅ Connected to: {DB_PATH}")
        
        # Check current jobs table structure
        cursor.execute("PRAGMA table_info(jobs)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        print(f"\n📋 Current 'jobs' table columns:")
        for col in columns:
            print(f"   - {col[1]} ({col[2]})")
        
        changes_made = []
        
        # Fix 1: Rename 'role' to 'job_title' if needed
        if 'role' in column_names and 'job_title' not in column_names:
            print(f"\n🔄 Migrating 'role' column to 'job_title'...")
            
            # SQLite doesn't support direct column rename, so we need to:
            # 1. Create new table with correct schema
            # 2. Copy data
            # 3. Drop old table
            # 4. Rename new table
            
            cursor.execute("""
                CREATE TABLE jobs_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_title TEXT NOT NULL,
                    job_description TEXT NOT NULL,
                    jd_summary TEXT DEFAULT NULL
                )
            """)
            
            # Copy data from old table
            cursor.execute("""
                INSERT INTO jobs_new (id, job_title, job_description, jd_summary)
                SELECT id, role, job_description, jd_summary FROM jobs
            """)
            
            # Get count to verify
            cursor.execute("SELECT COUNT(*) FROM jobs")
            old_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM jobs_new")
            new_count = cursor.fetchone()[0]
            
            if old_count == new_count:
                # Drop old table and rename new one
                cursor.execute("DROP TABLE jobs")
                cursor.execute("ALTER TABLE jobs_new RENAME TO jobs")
                conn.commit()
                print(f"✅ Renamed 'role' → 'job_title' ({new_count} rows migrated)")
                changes_made.append("Renamed 'role' to 'job_title'")
            else:
                print(f"❌ Data mismatch! Old: {old_count}, New: {new_count}")
                cursor.execute("DROP TABLE jobs_new")
                return False
        
        elif 'job_title' in column_names:
            print(f"\n✅ 'job_title' column already exists")
        
        # Fix 2: Add created_at column if it doesn't exist
        cursor.execute("PRAGMA table_info(jobs)")
        column_names = [col[1] for col in cursor.fetchall()]
        
        if 'created_at' not in column_names:
            print(f"\n🔄 Adding 'created_at' column...")
            cursor.execute("""
                ALTER TABLE jobs 
                ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            """)
            conn.commit()
            print(f"✅ Added 'created_at' column")
            changes_made.append("Added 'created_at' column")
        else:
            print(f"\n✅ 'created_at' column already exists")
        
        # Verify final structure
        cursor.execute("PRAGMA table_info(jobs)")
        columns = cursor.fetchall()
        
        print(f"\n📋 Updated 'jobs' table structure:")
        for col in columns:
            print(f"   ✓ {col[1]} ({col[2]})")
        
        # Show current data
        cursor.execute("SELECT COUNT(*) FROM jobs")
        job_count = cursor.fetchone()[0]
        
        if job_count > 0:
            cursor.execute("SELECT id, job_title FROM jobs LIMIT 3")
            sample_jobs = cursor.fetchall()
            print(f"\n📊 Current jobs in database: {job_count}")
            print(f"   Sample jobs:")
            for job in sample_jobs:
                print(f"   - [{job[0]}] {job[1]}")
        else:
            print(f"\n📊 Database is empty (0 jobs)")
        
        # Check candidates table
        print(f"\n🔍 Checking candidates table...")
        cursor.execute("PRAGMA table_info(candidates)")
        cand_columns = [col[1] for col in cursor.fetchall()]
        
        required_cand_cols = ['id', 'name', 'email', 'cv_text', 'match_score', 'matched_job_id']
        missing_cand_cols = [col for col in required_cand_cols if col not in cand_columns]
        
        if missing_cand_cols:
            print(f"   ⚠️  Missing columns: {missing_cand_cols}")
        else:
            print(f"   ✅ All required columns present")
        
        conn.close()
        
        print(f"\n{'='*70}")
        print(f"✅ DATABASE MIGRATION COMPLETE")
        print(f"{'='*70}")
        
        if changes_made:
            print(f"\n📝 Changes made:")
            for change in changes_made:
                print(f"   ✓ {change}")
        else:
            print(f"\n📝 No changes needed - database already up to date")
        
        print(f"\n{'='*70}\n")
        
        return True
        
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print(f"✅ Column already exists, no migration needed")
            return True
        else:
            print(f"❌ Database error: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def verify_database():
    """Verify database structure is correct"""
    print("\n" + "="*70)
    print("🔍 DATABASE VERIFICATION")
    print("="*70 + "\n")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print(f"📋 Tables in database:")
        for table in tables:
            if table[0] != 'sqlite_sequence':
                cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
                count = cursor.fetchone()[0]
                print(f"   ✓ {table[0]} ({count} rows)")
        
        # Check jobs table structure
        print(f"\n📊 Jobs table structure:")
        cursor.execute("PRAGMA table_info(jobs)")
        for col in cursor.fetchall():
            print(f"   ✓ {col[1]} ({col[2]})")
        
        # Check for required columns
        cursor.execute("PRAGMA table_info(jobs)")
        column_names = [col[1] for col in cursor.fetchall()]
        
        required_cols = ['id', 'job_title', 'job_description', 'jd_summary']
        missing = [col for col in required_cols if col not in column_names]
        
        if missing:
            print(f"\n❌ Missing required columns: {missing}")
            return False
        else:
            print(f"\n✅ All required columns present!")
            return True
        
    except Exception as e:
        print(f"❌ Verification error: {str(e)}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🚀 DATABASE MIGRATION TOOL")
    print("="*70)
    
    # Run migration
    success = fix_database()
    
    if success:
        # Verify the changes
        verify_success = verify_database()
        
        if verify_success:
            print("\n" + "="*70)
            print("✅ ALL CHECKS PASSED - Database is ready!")
            print("="*70)
            print("\nNext steps:")
            print("1. Upload your CSV: curl -X POST -F 'file=@jd.csv' http://localhost:5000/api/jobs/upload")
            print("2. Or run directly: python load_jobs.py")
            print("3. Summarize jobs: python jd_summarizer.py\n")
            exit(0)
        else:
            print("\n❌ Verification failed")
            exit(1)
    else:
        print("\n❌ Migration failed")
        exit(1)