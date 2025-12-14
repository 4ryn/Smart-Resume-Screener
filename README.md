# SmartHireX: AI-Enhanced Recruitment Platform with Web Dashboard

**SmartHireX** is an AI-powered, agent-based hiring automation platform with a modern web interface. It leverages large language models (llama3.1:8b) and vector-based similarity scoring to streamline resume parsing, candidate-job matching, and automated interview scheduling. The system features a Flask REST API backend and React dashboard frontend for complete recruitment workflow management.


### Flask REST API Backend
- **RESTful API endpoints** for all recruitment operations
- **File upload handling** for CVs and job descriptions  
- **Real-time processing** with status tracking
- **Database integration** with existing SQLite schema
- **CORS enabled** for frontend integration

### React Dashboard Frontend  
- **Modern UI/UX** with Tailwind CSS styling
- **Drag & drop file uploads** with progress tracking
- **Real-time processing pipeline** visualization
- **Interactive charts and analytics** using Recharts
- **Responsive design** for all screen sizes
- **Two-path user flow**: Candidate/Recruiter vs HR/Company modes

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           SmartHireX Architecture                           │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Input Layer   │    │  Agent Layer    │    │  Output Layer   │
│                 │    │                 │    │                 │
│ • Job Desc.     │───►│ • JD Summarizer │───►│ • Match Scores  │
│ • CV Files      │    │ • CV Extractor  │    │ • Shortlists    │
│ • Config        │    │ • Matching      │    │ • Interviews    │
└─────────────────┘    │ • Shortlisting  │    │ • Emails        │
                       │ • Scheduler     │    └─────────────────┘
                       └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │ LLM Integration │
                    │                 │
                    │ • Llama 3.1:8b  |
                    │ • Embeddings    │
                    │ • Text Gen      │
                    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │   Data Layer    │
                    │                 │
                    │ • SQLite3 DB    │
                    │ • Vector Store  │
                    │ • File Storage  │
                    └─────────────────┘
```

### Agent-Based Architecture Flow

```
Job Description → JD Summarizer Agent → Job Loader → Database
     ↓
CV Files → CV Extractor Agent → Candidate Profiles → Database
     ↓
Matching Agent → Cosine Similarity → Match Scores → Database
     ↓
Shortlisting Agent → Threshold Filter → Shortlisted Candidates
     ↓
Interview Scheduler Agent → Email Integration → Scheduled Interviews
```

---

##  LLM Prompts & AI Integration

### 1. Job Description Summarizer Prompt

**Agent**: `jd_summarizer.py`  
**Purpose**: Extract key qualifications from job descriptions

```python
JD_SUMMARIZER_PROMPT = """
You are an HR expert specializing in job analysis. 

Analyze the following job description and extract the key qualifications, skills, and requirements:

Job Description:
{job_description}

Please provide a concise summary focusing on:
1. Required technical skills
2. Years of experience needed
3. Educational qualifications
4. Key responsibilities
5. Must-have competencies

Format your response as a structured summary that can be used for candidate matching.
Keep it concise but comprehensive.
"""
```

### 2. CV Information Extraction Prompt

**Agent**: `process_cvs.py`  
**Purpose**: Parse and structure resume information

```python
CV_EXTRACTION_PROMPT = """
You are an expert resume parser. Extract structured information from the following resume text:

Resume Content:
{cv_text}

Extract and format the following information:
1. **Name**: Full name of the candidate
2. **Email**: Contact email address
3. **Skills**: List of technical and soft skills (comma-separated)
4. **Experience**: Total years of professional experience
5. **Education**: Highest degree and field of study
6. **Key Achievements**: Notable accomplishments or projects
7. **Job Titles**: Previous job titles and companies

Provide the information in a structured format that can be easily parsed.
If any information is not available, mark it as "Not specified".
"""
```

### 3. Candidate-Job Matching Analysis Prompt

**Agent**: `match_candidates.py`  
**Purpose**: Provide detailed matching rationale

```python
MATCHING_ANALYSIS_PROMPT = """
Analyze the compatibility between this candidate and job requirement:

Candidate Profile:
- Skills: {candidate_skills}
- Experience: {candidate_experience}
- Background: {candidate_background}

Job Requirements:
- Required Skills: {job_skills}
- Experience Level: {job_experience}
- Key Qualifications: {job_qualifications}

Provide:
1. **Match Score Justification**: Explain why this candidate scores {match_score}%
2. **Skill Alignment**: How candidate skills match job requirements
3. **Experience Gap**: Any experience gaps or surpluses
4. **Strengths**: Key strengths that make this candidate suitable
5. **Areas of Concern**: Potential gaps or misalignments
6. **Interview Focus**: Suggested areas to explore in interviews

Keep the analysis concise and actionable.
"""
```

### 4. Interview Email Generation Prompt

**Agent**: `interview_scheduler.py`  
**Purpose**: Generate personalized interview emails

```python
EMAIL_GENERATION_PROMPT = """
Generate a professional interview invitation email for the following scenario:

Candidate: {candidate_name}
Position: {job_title}
Interview Date: {interview_date}
Interview Time: {interview_time}
Company: SmartHireX

The email should:
1. Be professional and welcoming
2. Include all necessary interview details
3. Provide contact information for questions
4. Include any preparation instructions
5. Maintain an encouraging tone

Generate both subject line and email body.
"""
```

### 5. Candidate Assessment Prompt

**Agent**: Used across multiple modules  
**Purpose**: Evaluate candidate suitability

```python
ASSESSMENT_PROMPT = """
Evaluate this candidate's overall suitability for the role:

Candidate: {candidate_name}
Position: {job_title}
Match Score: {match_score}%

Assessment Criteria:
1. **Technical Competence**: Rate 1-10 with justification
2. **Experience Relevance**: How well experience aligns with role
3. **Growth Potential**: Candidate's potential for role advancement
4. **Cultural Fit Prediction**: Based on background and experience
5. **Interview Priority**: High/Medium/Low with reasoning
6. **Red Flags**: Any concerns or areas needing clarification

Provide a comprehensive assessment that helps hiring managers make informed decisions.
"""
```

---

## Features

- **Agent-based design**: modular, functional units (JD Summarizer, CV Extractor, Matching Agent, etc.)
- **LLM-driven information extraction** from resumes and job descriptions
- **Semantic job-candidate matching** using vector embeddings
- **Automated candidate shortlisting** with threshold control
- **One-click interview scheduling** with email integration
- **SQLite3-powered backend** for lightweight deployments

---

## Technologies Used

- **LLM**: LLaMA 3.1:8b via Ollama (`ollama.chat`, `ollama.embeddings`)
- **Database**: SQLite3
- **Email**: Python `smtplib`
- **Matching**: Cosine similarity on dense embeddings
- **File Handling**: `PyMuPDF` for PDF extraction
- **Vector Processing**: NumPy for similarity calculations
- **Text Processing**: Python-docx for document parsing

---

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+ 
- Node.js 16+ and npm
- Ollama (for local LLM)

### Backend Setup (Flask API)

```bash
# 1. Create virtual environment  
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# 2. Install Python dependencies
uv pip install -r requirements.txt

# 3. Install and setup Ollama
# Visit: https://ollama.ai for installation instructions
ollama pull llama3.1:8b

# 4. Initialize database
python database_setup.py

# 5. Start Flask API server
python start_backend.py
# API will be available at: http://localhost:5000
```

### Frontend Setup (React Dashboard)

```bash
# 1. Navigate to frontend directory
cd frontend

# 2. Install Node.js dependencies  
npm install

# 3. Start development server
npm run dev
# Frontend will be available at: http://localhost:3000
```

### Quick Start (Both Servers)

```bash
# Terminal 1 - Backend
python start_backend.py

# Terminal 2 - Frontend  
cd frontend && npm run dev

# Open browser: http://localhost:3000
```

---

## SmartHireX Agents & Execution Flow

```bash
# Step 1: DATABASE INITIALIZATION
# → Sets up SQLite database with required tables
python database_setup.py

# Step 2: JD SUMMARIZING AGENT
# → Uses llama3.1:8b model to extract required qualifications from job descriptions
python jd_summarizer.py

# Step 3: JOB LOADER
# → Loads summarized job descriptions into the jobs table
python load_jobs.py

# Step 4: CV EXTRACTOR AGENT
# → Parses resumes from uploaded PDFs and extracts structured data 
python process_cvs.py

# Step 5: MATCHING AGENT
# → Matches candidates to job descriptions using cosine similarity on embeddings
python match_candidates.py

# Step 6: SHORTLISTING AGENT
# → Filters candidates based on threshold and stores them in a shortlist table
python shortlist_candidates.py

# Step 7: INTERVIEW SCHEDULER AGENT
# → Randomly schedules interviews and sends emails to shortlisted candidates
python interview_scheduler.py
```

---

## Configuration (`config.py`)

```python
# File: config.py
import os
from dotenv import load_dotenv

load_dotenv()

# Database Configuration
DB_PATH = "database/smarthirex.db"

# LLM Configuration
OLLAMA_MODEL = "llama3.1:8b"
OLLAMA_BASE_URL = "http://localhost:11434"

# Matching Configuration
MATCH_THRESHOLD = 0.70  # 70% minimum match score
MAX_SHORTLIST_SIZE = 10

# Email Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = os.getenv("SMTP_USER", "your_email@example.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "your_app_password")

# File Paths
CV_UPLOAD_PATH = "uploads/cvs/"
JD_UPLOAD_PATH = "uploads/job_descriptions/"

# Interview Scheduling
INTERVIEW_TIME_SLOTS = [
    "09:00 AM", "10:30 AM", "02:00 PM", "03:30 PM"
]
INTERVIEW_DURATION_MINUTES = 60
```

---

## 📡 REST API Documentation

The Flask backend provides RESTful endpoints for all recruitment operations:

### Job Management Endpoints

```bash
# Upload job descriptions CSV
POST /api/jobs/upload
Content-Type: multipart/form-data
Body: file (CSV format)

# Trigger AI summarization of job descriptions  
POST /api/jobs/summarize

# Get all jobs
GET /api/jobs
```

### Candidate Management Endpoints

```bash
# Upload multiple CV files
POST /api/candidates/upload  
Content-Type: multipart/form-data
Body: files[] (PDF, DOCX formats)

# Get all candidates
GET /api/candidates
```

### Matching & Shortlisting Endpoints

```bash
# Trigger candidate-job matching
POST /api/matching/match

# Get matching results
GET /api/matching/results

# Create shortlist from top matches
POST /api/matching/shortlist

# Get shortlisted candidates
GET /api/matching/shortlist

# Send interview emails to shortlisted candidates
POST /api/matching/schedule
```

### Dashboard Analytics Endpoint

```bash
# Get dashboard statistics
GET /api/dashboard/stats

# Response format:
{
  "total_jobs": 5,
  "total_candidates": 50,
  "total_shortlisted": 8,
  "avg_match_score": 78.5,
  "summarized_jobs": 5,
  "emails_sent": 3
}
```

### Health Check

```bash
# API health status
GET /api/health

# Response: {"status": "healthy", "message": "SmartHireX API is running"}
```

---

##  Frontend Features  

The React dashboard provides an intuitive interface for the entire recruitment workflow:

### Landing Page
- **Two-path user flow**: Candidate/Recruiter vs HR/Company modes
- **Modern UI/UX** with animated transitions and gradient backgrounds
- **Clear call-to-action** buttons for each user type

### Upload Flow  
- **Drag & drop file uploads** with visual feedback
- **Multi-file support** for CVs (PDF, DOCX) 
- **Single CSV upload** for job descriptions
- **Real-time file validation** and error handling

### Processing Pipeline
- **Visual step-by-step progress** with animated indicators
- **Real-time status updates** during AI processing
- **Automatic progression** through all recruitment stages

### Results Dashboard
- **Interactive analytics** with charts and statistics  
- **Top matches visualization** with score-based color coding
- **One-click actions** for shortlisting and email scheduling
- **Responsive data tables** with sorting and filtering

### Key UI Components
- **Dark theme** with blue/purple accent colors
- **Tailwind CSS** for responsive design
- **Lucide React icons** for consistent iconography  
- **Recharts integration** for data visualization
- **Loading states** and error handling throughout

---

## Database Design

### Database File
The system uses SQLite3 database stored as `recruitment.db` in the project root directory.

### Tables Schema

```sql
-- Candidates Table
CREATE TABLE candidates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    skills TEXT,
    experience TEXT,
    education TEXT,
    cv_file_path TEXT,
    match_score REAL,
    matched_job_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (matched_job_id) REFERENCES jobs(id)
);

-- Jobs Table
CREATE TABLE jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_title TEXT NOT NULL,
    job_description TEXT NOT NULL,
    summarized_qualifications TEXT,
    required_skills TEXT,
    experience_level TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Shortlisted Candidates Table
CREATE TABLE shortlisted_candidates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    candidate_id INTEGER NOT NULL,
    job_id INTEGER NOT NULL,
    match_score REAL NOT NULL,
    interview_scheduled BOOLEAN DEFAULT FALSE,
    interview_date TEXT,
    interview_time TEXT,
    email_sent BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (candidate_id) REFERENCES candidates(id),
    FOREIGN KEY (job_id) REFERENCES jobs(id)
);
```

Refer to `database_setup.py` for complete schema implementation.

---

## Matching Algorithm

### Vector-Based Similarity Matching

1. **Text Preprocessing**: Clean and normalize job descriptions and resumes
2. **Embedding Generation**: Use Ollama's embedding API to convert text to vectors
3. **Similarity Calculation**: Compute cosine similarity between job and candidate vectors
4. **Threshold Filtering**: Only candidates above configurable threshold (default = 70%) are shortlisted
5. **Ranking**: Sort candidates by match score for each position

```python
# Simplified matching algorithm
def calculate_match_score(job_embedding, candidate_embedding):
    """Calculate cosine similarity between job and candidate vectors"""
    dot_product = np.dot(job_embedding, candidate_embedding)
    norm_job = np.linalg.norm(job_embedding)
    norm_candidate = np.linalg.norm(candidate_embedding)
    
    similarity = dot_product / (norm_job * norm_candidate)
    return similarity * 100  
```

---

## Interview Scheduling

### Automated Interview Management

- **Smart Scheduling**: Predefined time slots are intelligently assigned to avoid conflicts
- **Personalized Emails**: Role-specific email templates generated via LLM
- **Status Tracking**: Database records prevent duplicate emails and track interview status
- **Calendar Integration**: Ready for future calendar API integration

### Email Template Structure

```
Subject: Interview Invitation - {Job Title} Position at SmartHireX

Dear {Candidate Name},

We are pleased to invite you for an interview for the {Job Title} position 
based on your strong match score of {Match Score}%.

Interview Details:
- Date: {Interview Date}
- Time: {Interview Time}
- Duration: 60 minutes
- Format: [Video Call/In-Person]

Please confirm your availability by replying to this email.

Best regards,
SmartHireX Hiring Team
```

---

## Project Structure

```
SmartHireX/
├── __pycache__/           # Python cache files
├──backend\api              #backend files
├── data/                      # Data storage directory
│   ├── cvs/                  # Resume files (PDF, DOCX)
│   └── job_descriptions/     # Job description file
├──frontend
├── venv/                     # Python virtual environment
├── .env                      # Environment variables
├── .gitattributes           # Git configuration
├── config.py                # Configuration settings
├── database_setup.py        # Database initialization script
├── interview_scheduler.py   # Interview scheduling agent
├── jd_summarizer.py        # Job description summarizer agent
├── load_jobs.py            # Job loader utility
├── match_candidates.py     # Candidate matching agent
├── process_cvs.py          # CV processing agent
├── README.md               # Project documentation
├── recruitment.db          # SQLite database file
├── shortlist_candidates.py # Candidate shortlisting agent
└──start_backend.py
```

---

## Usage Examples

### 1. Initial Setup
```bash
# Set up the database
python database_setup.py

# Expected output:
# Database and tables created successfully!
```

### 2. Processing Job Descriptions
```bash
# Place job description files in data/job_descriptions/
# Run the JD summarizer
python jd_summarizer.py

# Load jobs into database
python load_jobs.py

# Expected output:
# Job descriptions processed and loaded into database
```

### 3. Processing Candidate Resumes
```bash
# Place resume files (PDF/DOCX) in data/cvs/
python process_cvs.py

# Expected output:
# Processing CV: candidate1.pdf
# Candidate data extracted and saved to database
```

### 4. Running the Matching Pipeline
```bash
# Match candidates to jobs
python match_candidates.py

# Expected output:
# Matching candidates to jobs...
# Match scores calculated and saved

# Shortlist top candidates
python shortlist_candidates.py

# Expected output:
# Shortlisting candidates with score > 70%
# X candidates shortlisted for Y positions
```

### 5. Schedule Interviews
```bash
# Configure email settings in .env file first
python interview_scheduler.py

# Expected output:
# Scheduling interviews for shortlisted candidates...
# Interview emails sent to X candidates
```

### 6. Check Database Status
```python
# Python script to check database contents
import sqlite3

conn = sqlite3.connect('recruitment.db')
cursor = conn.cursor()

# Check candidates
cursor.execute("SELECT COUNT(*) FROM candidates")
print(f"Total candidates: {cursor.fetchone()[0]}")

# Check jobs
cursor.execute("SELECT COUNT(*) FROM jobs")
print(f"Total jobs: {cursor.fetchone()[0]}")

# Check shortlisted candidates
cursor.execute("SELECT COUNT(*) FROM shortlisted_candidates")
print(f"Shortlisted candidates: {cursor.fetchone()[0]}")

conn.close()
```

---

## Environment Configuration

Create a `.env` file in the project root:

```env
# Email Configuration
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# Optional: Override default settings
OLLAMA_BASE_URL=http://localhost:11434
MATCH_THRESHOLD=0.50
MAX_SHORTLIST_SIZE=10
```

---

## File Organization Guidelines

### Data Directory Structure
```
data/
├── cvs/                     # Candidate resumes
│   ├── john_doe.pdf
│   ├── jane_smith.docx
│   └── ...
└── job_descriptions/        # Job postings
    ├── software_engineer.txt
    ├── data_scientist.txt
    └── ...
```

### Supported File Formats
- **Resumes**: PDF, DOCX
- **Job Descriptions**: TXT, PDF, DOCX
- **Database**: SQLite3 (.db)

---

## API Integration Potential

SmartHireX is designed for easy integration with external systems:

- **ATS Integration**: Connect with existing Applicant Tracking Systems
- **Calendar APIs**: Integrate with Google Calendar, Outlook, etc.
- **Email Platforms**: Support for SendGrid, Mailgun, etc.
- **Job Boards**: Sync with LinkedIn, Indeed, and other job platforms
- **HR Systems**: Integration with HRIS and employee management systems

---

## Performance Metrics

The system tracks key hiring metrics:

- **Processing Speed**: Average time to process resumes and job descriptions
- **Match Accuracy**: Quality of candidate-job matches
- **Email Delivery**: Success rate of interview invitation emails
- **Database Performance**: Query execution times and storage efficiency
- **LLM Response Times**: Ollama model performance metrics

---

## Future Enhancements

- **Web Interface**: React-based dashboard for HR teams
- **Real-time Processing**: WebSocket integration for live updates
- **Advanced Analytics**: Hiring pipeline analytics and reporting
- **Multi-language Support**: Resume parsing in multiple languages
- **Video Interview Integration**: Automated video interview scheduling
- **Candidate Feedback**: Automated feedback collection system

---

## Troubleshooting

### Common Issues

1. **Ollama Connection Error**
   - Ensure Ollama is running: `ollama serve`
   - Check model availability: `ollama list`
   - Verify OLLAMA_BASE_URL in config.py

2. **Email Sending Failed**
   - Verify SMTP credentials in `.env` file
   - Check firewall settings for SMTP ports
   - Enable "Less secure app access" for Gmail (or use App Password)

3. **PDF Processing Error**
   - Ensure PyMuPDF is properly installed: `pip install PyMuPDF`
   - Check file permissions for data directories
   - Verify PDF files are not corrupted

4. **Database Lock Error**
   - Close any existing database connections
   - Check if another process is using recruitment.db
   - Restart the application

5. **Module Import Errors**
   - Activate virtual environment: `venv\Scripts\activate`
   - Install missing dependencies: `pip install -r requirements.txt`
   - Check Python path and working directory

### Debug Mode
Add debug logging to any agent:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Add logger.debug() statements in your code
logger.debug("Processing file: {filename}")
```

---

# SmartHireX System Setup & Running Guide

This guide explains how to set up and run the complete SmartHireX recruitment system.

## System Requirements

- Python 3.9+ with pip
- Node.js 16+ with npm
- Ollama (for running LLaMA 3.1 locally)

## 1. Setting up the Backend

### 1.1 Install Python Dependencies

```bash
# Create and activate a virtual environment
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 1.2 Install and Configure Ollama

1. Download and install Ollama from [ollama.ai](https://ollama.ai)
2. Pull the LLaMA 3.1 model:
```bash
ollama pull llama3.1:8b
```

### 1.3 Configure Environment Variables

Create a `.env` file in the project root:

```env
# Email Configuration
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# Optional: Override default settings
OLLAMA_BASE_URL=http://localhost:11434
MATCH_THRESHOLD=0.70
MAX_SHORTLIST_SIZE=10
```

## 2. Running the System

### 2.1 Database Initialization

```bash
# Set up the database
python database_setup.py

# Expected output:
# Database and tables created successfully!
```

### 2.2 Processing Job Descriptions

```bash
# Place job description files in data/job_descriptions/
# Run the JD summarizer
python jd_summarizer.py

# Load jobs into database
python load_jobs.py

# Expected output:
# Job descriptions processed and loaded into database
```

### 2.3 Processing Candidate Resumes

```bash
# Place resume files (PDF/DOCX) in data/cvs/
python process_cvs.py

# Expected output:
# Processing CV: candidate1.pdf
# Candidate data extracted and saved to database
```

### 2.4 Running the Matching Pipeline

```bash
# Match candidates to jobs
python match_candidates.py

# Expected output:
# Matching candidates to jobs...
# Match scores calculated and saved

# Shortlist top candidates
python shortlist_candidates.py

# Expected output:
# Shortlisting candidates with score > 70%
# X candidates shortlisted for Y positions
```

### 2.5 Schedule Interviews

```bash
# Configure email settings in .env file first
python interview_scheduler.py

# Expected output:
# Scheduling interviews for shortlisted candidates...
# Interview emails sent to X candidates
```

### 2.6 Check Database Status

```python
# Python script to check database contents
import sqlite3

conn = sqlite3.connect('recruitment.db')
cursor = conn.cursor()

# Check candidates
cursor.execute("SELECT COUNT(*) FROM candidates")
print(f"Total candidates: {cursor.fetchone()[0]}")

# Check jobs
cursor.execute("SELECT COUNT(*) FROM jobs")
print(f"Total jobs: {cursor.fetchone()[0]}")

# Check shortlisted candidates
cursor.execute("SELECT COUNT(*) FROM shortlisted_candidates")
print(f"Shortlisted candidates: {cursor.fetchone()[0]}")

conn.close()
```

---

## File Organization Guidelines

### Data Directory Structure
```
data/
├── cvs/                     # Candidate resumes
│   ├── john_doe.pdf
│   ├── jane_smith.docx
│   └── ...
└── job_descriptions/        # Job postings
    ├── software_engineer.txt
    ├── data_scientist.txt
    └── ...
```

### Supported File Formats
- **Resumes**: PDF, DOCX
- **Job Descriptions**: TXT, PDF, DOCX
- **Database**: SQLite3 (.db)

---

## API Integration Potential

SmartHireX is designed for easy integration with external systems:

- **ATS Integration**: Connect with existing Applicant Tracking Systems
- **Calendar APIs**: Integrate with Google Calendar, Outlook, etc.
- **Email Platforms**: Support for SendGrid, Mailgun, etc.
- **Job Boards**: Sync with LinkedIn, Indeed, and other job platforms
- **HR Systems**: Integration with HRIS and employee management systems

---

## Performance Metrics

The system tracks key hiring metrics:

- **Processing Speed**: Average time to process resumes and job descriptions
- **Match Accuracy**: Quality of candidate-job matches
- **Email Delivery**: Success rate of interview invitation emails
- **Database Performance**: Query execution times and storage efficiency
- **LLM Response Times**: Ollama model performance metrics

---

## Future Enhancements

- **Web Interface**: React-based dashboard for HR teams
- **Real-time Processing**: WebSocket integration for live updates
- **Advanced Analytics**: Hiring pipeline analytics and reporting
- **Multi-language Support**: Resume parsing in multiple languages
- **Video Interview Integration**: Automated video interview scheduling
- **Candidate Feedback**: Automated feedback collection system

---

## Troubleshooting

### Common Issues

1. **Ollama Connection Error**
   - Ensure Ollama is running: `ollama serve`
   - Check model availability: `ollama list`
   - Verify OLLAMA_BASE_URL in config.py

2. **Email Sending Failed**
   - Verify SMTP credentials in `.env` file
   - Check firewall settings for SMTP ports
   - Enable "Less secure app access" for Gmail (or use App Password)

3. **PDF Processing Error**
   - Ensure PyMuPDF is properly installed: `pip install PyMuPDF`
   - Check file permissions for data directories
   - Verify PDF files are not corrupted

4. **Database Lock Error**
   - Close any existing database connections
   - Check if another process is using recruitment.db
   - Restart the application

5. **Module Import Errors**
   - Activate virtual environment: `venv\Scripts\activate`
   - Install missing dependencies: `pip install -r requirements.txt`
   - Check Python path and working directory

### Debug Mode
Add debug logging to any agent:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Add logger.debug() statements in your code
logger.debug("Processing file: {filename}")
```

---

## License

This project is licensed under the MIT License.

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---


**Built with ❤️ using LLaMA 3.1:8b and modern AI technologies**
