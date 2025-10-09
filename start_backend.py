#!/usr/bin/env python3
"""
SmartHireX Backend API Server
Starts the Flask API server with proper environment setup
"""

import os
import sys
import subprocess

def main():
    print("Starting SmartHireX Backend API Server...")

    # Add project root to 
    # Python path
    project_root = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, project_root)
    
    # Check if database exists
    db_path = os.path.join(project_root, "recruitment.db")
    if not os.path.exists(db_path):
        print("Database not found. Running database setup...")
        try:
            import database_setup
            print(" Database setup completed")
        except Exception as e:
            print(f" Database setup failed: {e}")
            return 1
    
    # Start Flask server
    try:
        from backend.api.app import app
        print(" Flask app imported successfully")
        print(" API will be available at: http://localhost:5000")
        print(" Health check: http://localhost:5000/api/health")
        print(" Use Ctrl+C to stop the server")
        app.run(debug=True, host='0.0.0.0', port=5000)
    except ImportError as e:
        print(f" Import error: {e}")
        print(" Make sure Flask is installed: pip install flask flask-cors")
        return 1
    except Exception as e:
        print(f" Server error: {e}")
        return 1

if __name__ == "__main__":
    exit(main())