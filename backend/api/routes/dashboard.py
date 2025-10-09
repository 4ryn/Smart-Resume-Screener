from flask import Blueprint, jsonify
from backend.api.utils.db_helper import get_dashboard_stats

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get dashboard statistics"""
    try:
        stats = get_dashboard_stats()
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/data', methods=['GET'])
def get_all_data():
    """Get all database data for viewing"""
    try:
        import sqlite3
        from config import DB_PATH
        
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get all candidates
        cursor.execute("SELECT * FROM candidates ORDER BY id DESC")
        candidates = [dict(row) for row in cursor.fetchall()]
        
        # Get all jobs
        cursor.execute("SELECT * FROM jobs ORDER BY id DESC") 
        jobs = [dict(row) for row in cursor.fetchall()]
        
        # Get shortlisted candidates
        cursor.execute("""
            SELECT sc.*, j.job_title 
            FROM shortlisted_candidates sc
            LEFT JOIN jobs j ON sc.job_id = j.id
            ORDER BY sc.match_score DESC
        """)
        shortlisted = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return jsonify({
            'candidates': candidates,
            'jobs': jobs,
            'shortlisted': shortlisted,
            'summary': {
                'total_candidates': len(candidates),
                'total_jobs': len(jobs),
                'total_shortlisted': len(shortlisted),
                'matched_candidates': len([c for c in candidates if c['match_score']])
            }
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500