from flask import Flask, jsonify
from flask_cors import CORS
import os
import sys

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from backend.api.routes.jobs import jobs_bp
from backend.api.routes.candidates import candidates_bp
from backend.api.routes.matching import matching_bp
from backend.api.routes.dashboard import dashboard_bp

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend
@app.route('/')
def home():
    return jsonify({"message": "Smart Resume Screener backend is running successfully!"})

# Example: add another test route
@app.route('/ping')
def ping():
    return jsonify({"status": "ok"})
# Register blueprints
app.register_blueprint(jobs_bp, url_prefix='/api/jobs')
app.register_blueprint(candidates_bp, url_prefix='/api/candidates')
app.register_blueprint(matching_bp, url_prefix='/api/matching')
app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'message': 'SmartHireX API is running'}), 200

if __name__ == '__main__':
    print(" Starting SmartHireX API Server...")
    print("API running at: http://localhost:5000")
    print("Health check: http://localhost:5000/api/health")
    app.run(debug=True, host='0.0.0.0', port=5000)