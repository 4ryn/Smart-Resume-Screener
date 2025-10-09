from flask import Blueprint, request, jsonify
import os
from werkzeug.utils import secure_filename
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))
from process_cvs import process_cvs
from backend.api.utils.db_helper import get_all_candidates

candidates_bp = Blueprint('candidates', __name__)

def clear_candidate_related_data():
    """Clear all candidate-related data for fresh upload"""
    import sqlite3
    from config import DB_PATH
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("🗑️  Clearing all candidate-related data...")
    cursor.execute("DELETE FROM candidates")
    cursor.execute("DELETE FROM shortlisted_candidates")
    conn.commit()
    conn.close()
    print("✅ All candidate-related data cleared.")

UPLOAD_FOLDER = 'data/uploaded_cvs'  # New folder for uploaded CVs
ALLOWED_EXTENSIONS = {'pdf', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@candidates_bp.route('/upload', methods=['POST'])
def upload_cvs():
    """Upload multiple CV files"""
    try:
        print(f"📤 CV upload request received")
        print(f"Request files keys: {list(request.files.keys())}")
        
        if 'files' not in request.files:
            return jsonify({'error': 'No files provided'}), 400
        
        files = request.files.getlist('files')
        print(f"📁 Number of files received: {len(files)}")
        
        if not files or (len(files) == 1 and files[0].filename == ''):
            return jsonify({'error': 'No files selected'}), 400
        
        # Clear and recreate upload folder
        if os.path.exists(UPLOAD_FOLDER):
            import shutil
            shutil.rmtree(UPLOAD_FOLDER)
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
        uploaded = []
        errors = []
        
        for file in files:
            print(f"Processing file: {file.filename}")
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file.save(filepath)
                uploaded.append(filename)
                print(f"✅ Saved: {filename}")
            else:
                error_msg = f'{file.filename} - Invalid file type' if file.filename else 'Empty filename'
                errors.append(error_msg)
                print(f"❌ {error_msg}")
        
        print(f"📊 Upload summary: {len(uploaded)} files uploaded, {len(errors)} errors")
        
        if not uploaded:
            return jsonify({'error': 'No valid CV files were uploaded'}), 400
        
        # Clear existing candidate data first
        clear_candidate_related_data()
        
        # Process only the uploaded files using modified function
        from process_cvs import process_cvs_from_folder
        process_cvs_from_folder(UPLOAD_FOLDER)
        
        # Get count of newly processed candidates
        from backend.api.utils.db_helper import get_all_candidates
        new_candidates = get_all_candidates()
        
        return jsonify({
            'message': f'{len(uploaded)} CVs uploaded, {len(new_candidates)} candidates processed (previous data cleared)',
            'files_uploaded': len(uploaded),
            'candidates_processed': len(new_candidates),
            'uploaded': uploaded,
            'errors': errors
        }), 200
        
    except Exception as e:
        print(f"❌ CV upload error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@candidates_bp.route('/', methods=['GET'])
def get_candidates():
    """Get all candidates"""
    try:
        candidates = get_all_candidates()
        response = jsonify({
            'data': candidates,
            'count': len(candidates),
            'timestamp': __import__('datetime').datetime.now().isoformat()
        })
        # Add cache-busting headers
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response, 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500