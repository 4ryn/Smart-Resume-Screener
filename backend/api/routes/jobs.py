from flask import Blueprint, request, jsonify
import os
import pandas as pd
from werkzeug.utils import secure_filename
import sys

# Import existing scripts
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))
from load_jobs import load_job_descriptions
from jd_summarizer import process_job_descriptions
from backend.api.utils.db_helper import get_all_jobs

jobs_bp = Blueprint('jobs', __name__)

def clear_job_related_data():
    """Clear all job-related data for fresh upload"""
    import sqlite3
    from config import DB_PATH
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("🗑️  Clearing all job-related data...")
    cursor.execute("DELETE FROM jobs")
    cursor.execute("DELETE FROM shortlisted_candidates") 
    cursor.execute("UPDATE candidates SET match_score = NULL, matched_job_id = NULL")
    conn.commit()
    conn.close()
    print("✅ All job-related data cleared.")

UPLOAD_FOLDER = 'data'
ALLOWED_EXTENSIONS = {'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@jobs_bp.route('/upload', methods=['POST'])
def upload_job_csv():
    """Upload and process job description CSV"""
    try:
        print(f"📤 Job upload request received")
        print(f"Request files: {list(request.files.keys())}")
        print(f"Request form data: {dict(request.form)}")
        
        if 'file' not in request.files:
            print("❌ No 'file' key in request.files")
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        print(f"📁 File received: {file.filename}")
        
        if file.filename == '':
            print("❌ Empty filename")
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            print(f"❌ Invalid file type: {file.filename}")
            return jsonify({'error': 'Invalid file type. Only CSV allowed'}), 400
        
        # Ensure upload directory exists
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
        filename = secure_filename('job_description.csv')
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        print(f"💾 Saving file to: {filepath}")
        file.save(filepath)
        
        # Clear existing job data first (load_jobs.py will also do this)
        clear_job_related_data()
        # Call existing load_jobs.py logic
        load_job_descriptions()
        
        # Get count of newly loaded jobs
        from backend.api.utils.db_helper import get_all_jobs
        new_jobs = get_all_jobs()
        
        return jsonify({
            'message': f'Successfully uploaded {len(new_jobs)} job descriptions (previous data cleared)',
            'jobs_uploaded': len(new_jobs),
            'next_step': 'Call /api/jobs/summarize to process job descriptions'
        }), 200
        
    except Exception as e:
        print(f"❌ Upload error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@jobs_bp.route('/summarize', methods=['POST'])
def summarize_jobs():
    """Trigger JD summarization using LLM"""
    try:
        process_job_descriptions()
        return jsonify({'message': 'Job descriptions summarized successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@jobs_bp.route('/', methods=['GET'])
def get_jobs():
    """Get all jobs"""
    try:
        jobs = get_all_jobs()
        response = jsonify({
            'data': jobs,
            'count': len(jobs),
            'timestamp': __import__('datetime').datetime.now().isoformat()
        })
        # Add cache-busting headers
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response, 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@jobs_bp.route('/clear', methods=['POST'])
def clear_all_data():
    """Clear all recruitment data for fresh start"""
    try:
        import sqlite3
        from config import DB_PATH
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        print("🗑️  Clearing ALL recruitment data...")
        cursor.execute("DELETE FROM jobs")
        cursor.execute("DELETE FROM candidates")
        cursor.execute("DELETE FROM shortlisted_candidates")
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'All recruitment data cleared successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500