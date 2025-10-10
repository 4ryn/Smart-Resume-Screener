import sqlite3
import ollama
from config import OLLAMA_MODEL, DB_PATH

def summarize_job_description(job_title, jd_text):
    """Uses Ollama LLM to extract key skills, experience, and qualifications from JD."""
    
    # Enhanced prompt specifically designed for the job description format
    prompt = f"""
You are an expert HR analyst. Analyze the following job description and extract key information in a structured format.

JOB TITLE: {job_title}

JOB DESCRIPTION:
{jd_text}

Extract and organize the information in this EXACT format:

**Required Skills:**
Technical Skills: [List all programming languages, tools, frameworks, technologies]
Soft Skills: [List communication, leadership, teamwork, analytical skills]
Domain Knowledge: [Industry-specific knowledge, methodologies]

**Experience Requirements:**
Years Required: [Specify years of experience needed]
Type of Experience: [Describe the type of work experience required]
Preferred Experience: [Additional experience that would be beneficial]

**Educational Qualifications:**
Required Degree: [Bachelor's, Master's, PhD, etc.]
Field of Study: [Computer Science, Engineering, etc.]
Certifications: [List any certifications mentioned - CEH, CISSP, AWS, etc.]

**Key Responsibilities:**
- [List 4-6 main responsibilities]

**Technical Requirements:**
[List specific technical requirements like cloud platforms, databases, programming languages]

**Additional Requirements:**
[Travel, location, security clearance, language skills, work authorization, etc.]

**Nice to Have:**
[Optional qualifications, skills, or experience]

IMPORTANT RULES:
1. If information is not mentioned in the job description, write "Not specified"
2. Be thorough but concise
3. Extract information exactly as stated, don't make assumptions
4. Keep the exact format shown above
5. Focus on factual information from the job description
"""

    try:
        print(f"   🤖 Calling Ollama model: {OLLAMA_MODEL}")
        response = ollama.chat(
            model=OLLAMA_MODEL, 
            messages=[
                {
                    "role": "system", 
                    "content": "You are an expert HR analyst specializing in job description analysis. Provide structured, accurate summaries."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ]
        )
        return response["message"]["content"]
    except Exception as e:
        print(f"   ❌ Ollama API Error: {str(e)}")
        raise

def process_job_descriptions():
    """Fetches JDs from SQLite, summarizes them using Ollama, and updates the database."""
    try:
        # Connect to SQLite
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Check which column name is used for job title
        cursor.execute("PRAGMA table_info(jobs)")
        columns = [col[1] for col in cursor.fetchall()]
        title_column = 'job_title' if 'job_title' in columns else 'role'
        
        print(f"ℹ️  Using '{title_column}' column for job titles")

        # Fetch job descriptions that have not been summarized
        query = f"SELECT id, {title_column}, job_description FROM jobs WHERE jd_summary IS NULL OR jd_summary = ''"
        cursor.execute(query)
        jobs = cursor.fetchall()
        
        if not jobs:
            print("✅ All job descriptions are already summarized.")
            conn.close()
            return

        print(f"\n{'='*60}")
        print(f"📋 Found {len(jobs)} job description(s) to process")
        print(f"{'='*60}\n")
        
        # Process each JD
        processed_count = 0
        failed_count = 0
        
        for idx, (job_id, job_title, jd_text) in enumerate(jobs, 1):
            print(f"\n[{idx}/{len(jobs)}] Processing Job ID: {job_id}")
            print(f"   📌 Job Title: {job_title}")
            
            try:
                # Validate job description
                if not jd_text or len(jd_text.strip()) < 20:
                    print(f"   ⚠️  Job description too short or empty. Skipping...")
                    failed_count += 1
                    continue
                
                print(f"   📝 Description length: {len(jd_text)} characters")
                
                # Generate summary using LLM
                summary = summarize_job_description(job_title, jd_text)
                
                if not summary or len(summary.strip()) < 50:
                    print(f"   ⚠️  Generated summary is too short. Skipping...")
                    failed_count += 1
                    continue
                
                # Update database with the summary
                cursor.execute("UPDATE jobs SET jd_summary = ? WHERE id = ?", (summary, job_id))
                conn.commit()
                
                processed_count += 1
                print(f"   ✅ Successfully summarized (Summary length: {len(summary)} chars)")
                
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
                failed_count += 1
                continue
        
        # Close connection
        conn.close()
        
        # Print summary
        print(f"\n{'='*60}")
        print(f"📊 PROCESSING COMPLETE")
        print(f"{'='*60}")
        print(f"✅ Successfully Processed: {processed_count}")
        print(f"❌ Failed: {failed_count}")
        print(f"📝 Total: {len(jobs)}")
        print(f"{'='*60}\n")
        
        if failed_count > 0:
            print(f"⚠️  {failed_count} job(s) failed to process. Check logs above for details.")
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {str(e)}")
        raise
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 JOB DESCRIPTION SUMMARIZER")
    print("="*60 + "\n")
    process_job_descriptions()