from flask import Blueprint, jsonify
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))
from match_candidates import process_candidate_matching
from shortlist_candidates import shortlist_candidates
from interview_scheduler import schedule_interviews
from backend.api.utils.db_helper import get_matched_candidates, get_shortlisted_candidates

matching_bp = Blueprint('matching', __name__)

@matching_bp.route('/match', methods=['POST'])
def trigger_matching():
    """Trigger candidate-job matching"""
    try:
        process_candidate_matching()
        return jsonify({'message': 'Matching completed successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@matching_bp.route('/results', methods=['GET'])
def get_match_results():
    """Get matching results"""
    try:
        matches = get_matched_candidates()
        return jsonify(matches), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@matching_bp.route('/shortlist', methods=['POST'])
def trigger_shortlisting():
    """Trigger candidate shortlisting"""
    try:
        shortlist_candidates()
        return jsonify({'message': 'Shortlisting completed successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@matching_bp.route('/shortlist', methods=['GET'])
def get_shortlist():
    """Get shortlisted candidates"""
    try:
        shortlist = get_shortlisted_candidates()
        return jsonify(shortlist), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@matching_bp.route('/schedule', methods=['POST'])
def trigger_scheduling():
    """Trigger interview scheduling"""
    try:
        schedule_interviews()
        return jsonify({'message': 'Interviews scheduled and emails sent'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500