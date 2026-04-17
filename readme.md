JOB APPLICATION COPILOT
Complete Production-Grade System Documentation
Architecture • Implementation • AI Prompts • APIs • Deployment
WHAT THIS DOCUMENT COVERS
System Architecture • Tech Stack • Database Schema • API Design
AI Prompt Engineering • Folder Structure • Deployment • 7-Day MVP Plan

Version 1.0 | Personal Use / Local-First Build | Zero-Cost Stack

 
SECTION 1: VISION & SYSTEM OVERVIEW
1.1 What Is the Job Application Copilot?
The Job Application Copilot is a fully local, AI-powered system that acts as your personal career assistant. It scrapes job listings from public job boards (without using paid APIs), parses them against your master resume, generates tailored ATS-optimised resumes and cover letters using a local LLM (Ollama + Mistral/LLaMA), scores each application, and maintains a live tracking dashboard — all running on your own machine for free.

Core Philosophy
This is NOT an auto-apply bot. It maximises your INTERVIEW RATE by ensuring every application you manually submit is perfectly tailored. The system does the heavy lifting; you do the final click.

1.2 High-Level Capability Map
Input Layer Your master resume (PDF/DOCX), LinkedIn export, GitHub profile URL
Job Discovery Automated scraping of LinkedIn, Naukri, Indeed, Wellfound (ethical, rate-limited)
AI Engine Local Ollama LLM (free) + sentence-transformers for embeddings — no API cost
Resume Generation Per-job tailored resume in PDF + DOCX with ATS score 0-100
Tracking System SQLite database + auto-exported Excel/Google Sheets dashboard
Frontend React dashboard (Vite) running on localhost:3000
Backend Python FastAPI running on localhost:8000
Scheduler APScheduler (Python) — nightly cron at 2 AM
Storage Local filesystem (optionally sync to Google Drive or S3)
Extra Features Cover letter, skill gap report, referral email templates, Chrome extension

1.3 What Makes This Different From Generic Advice
• Uses LOCAL LLMs (Ollama) — zero API cost, works fully offline
• Semantic job matching with sentence-transformers cosine similarity
• ATS scoring algorithm mirrors real ATS systems (keyword density + section analysis)
• Generates versioned resumes — never overwrites, full history per job
• Semi-automated pipeline with human-in-the-loop for final apply decision
• Scrapers use respectful delays + user-agent rotation to stay under radar

 
SECTION 2: COMPLETE SYSTEM ARCHITECTURE
2.1 Architecture Diagram (Textual)

┌─────────────────────────────────────────────────────────────────────┐
│ JOB APPLICATION COPILOT │
│ LOCAL-FIRST SYSTEM │
└─────────────────────────────────────────────────────────────────────┘

┌───────────────────┐ ┌──────────────────────────────────────┐
│ INPUT SOURCES │ │ REACT DASHBOARD │
│ │ │ localhost:3000 │
│ • Master Resume │ │ │
│ (PDF/DOCX) │ │ ┌──────────┐ ┌──────────────────┐ │
│ • LinkedIn CSV │ │ │ Job List │ │ ATS Score Gauges │ │
│ • GitHub URL │ │ └──────────┘ └──────────────────┘ │
│ • Manual JD │ │ ┌──────────┐ ┌──────────────────┐ │
└────────┬──────────┘ │ │ Resume │ │ Status Tracker │ │
│ │ │ Preview │ │ Filters & Search │ │
▼ │ └──────────┘ └──────────────────┘ │
┌───────────────────┐ └──────────────┬───────────────────────┘
│ PYTHON FASTAPI │◄─────────────────────┘ REST API calls
│ localhost:8000 │
│ │
│ ┌─────────────┐ │ ┌──────────────────────────────────────┐
│ │ /parse │ │ │ LOCAL AI STACK (FREE) │
│ │ /analyze │ │◄────►│ │
│ │ /generate │ │ │ Ollama Runtime │
│ │ /score │ │ │ └── mistral:7b (resume gen) │
│ │ /track │ │ │ └── llama3.2:3b (fast ATS score) │
│ │ /scrape │ │ │ │
│ └─────────────┘ │ │ sentence-transformers │
│ │ │ └── all-MiniLM-L6-v2 (embeddings) │
│ APScheduler │ └──────────────────────────────────────┘
│ (Nightly 2 AM) │
└────────┬──────────┘
│
┌──────▼──────────────────────────────────────────┐
│ DATA LAYER │
│ │
│ SQLite DB Local Filesystem │
│ └── jobs └── /resumes/ │
│ └── applications └── {company}/ │
│ └── user_profile └── v1_resume.pdf │
│ └── skills_cache └── v1_resume.docx│
│ └── /exports/ │
│ └── tracker.xlsx │
└─────────────────────────────────────────────────┘

    ┌──────────────────────────────────────────────────┐
    │           WEB SCRAPERS (ETHICAL)                 │
    │                                                  │
    │  LinkedIn Jobs   (Playwright headless)            │
    │  Naukri.com      (requests + BeautifulSoup)       │
    │  Indeed India    (requests + BeautifulSoup)       │
    │  Wellfound       (requests + BeautifulSoup)       │
    │  Remotive.io     (Official free API - no scrape) │
    │  JobsPikr        (Free tier 100 jobs/month)       │
    └──────────────────────────────────────────────────┘

    ┌──────────────────────────────────────────────────┐
    │         CHROME EXTENSION (Optional)              │
    │  1-Click capture of any job page               │
    │  Sends JD to localhost:8000/api/capture-jd      │
    └──────────────────────────────────────────────────┘

2.2 Data Flow — Complete Request Lifecycle
USER ACTION: "Scrape new jobs"

1. Scheduler / Manual trigger
   └── scraper_service.py
   └── LinkedIn/Naukri/Indeed scrapers
   └── raw_jobs[] (title, company, url, jd_text)

2. Filter Service
   └── embed(user_profile) vs embed(job_jd)
   └── cosine_similarity > 0.65 → keep
   └── filtered_jobs[] saved to SQLite

3. Resume Generation (per job)
   └── jd_analyzer.py → keywords[], required_skills[], exp_years
   └── resume_generator.py → Ollama prompt → tailored_resume_text
   └── ats_scorer.py → score 0-100
   └── file_builder.py → PDF + DOCX saved to /resumes/{company}/

4. Tracking Update
   └── tracker_service.py → SQLite row inserted
   └── Excel export → /exports/tracker_YYYYMMDD.xlsx

5. Dashboard Update
   └── React polls /api/jobs every 30s
   └── New jobs appear in Job List with ATS scores

 
SECTION 3: TECH STACK — FULL JUSTIFICATION
3.1 Complete Technology Decisions

Technology Role Why Chosen
Ollama + Mistral 7B LLM for resume & cover letter 100% free, offline, no API limits, runs on 8GB RAM laptop
sentence-transformers Job-profile semantic matching Free, fast, local embeddings, best-in-class for English NLP
Python FastAPI Backend framework Async, auto-docs at /docs, type hints, fastest Python web framework
SQLite Primary database Zero setup, file-based, perfect for single-user local system
React + Vite Frontend dashboard Fast HMR, no config hell, easiest React setup for solo devs
Playwright LinkedIn scraper Handles JS-rendered pages, mimics real browser, free
BeautifulSoup4 Static site scrapers Lightweight, easy to parse HTML, no JS needed for Naukri/Indeed
APScheduler Nightly cron jobs Pure Python scheduler, no external service needed
python-docx DOCX generation Official MS Word format writer, free, no LibreOffice dependency
WeasyPrint PDF generation HTML-to-PDF, allows beautiful CSS-styled resumes
openpyxl Excel export Free, creates .xlsx without MS Office, perfect for trackers
PyMuPDF (fitz) PDF resume parsing Fastest PDF text extractor, handles complex layouts
Remotive.io API Remote job source Free public API, no auth needed, 1000+ jobs
Tailwind CSS Dashboard styling No design system needed, utility-first, fast to build
Axios HTTP client (React) Promise-based, automatic JSON parsing, industry standard
Recharts ATS score charts React-native, zero config, beautiful gauges and bar charts
ChromaDB Vector store (optional) Free local vector database for embedding-based search

3.2 Why NOT These Common Choices
Avoided Tech Reason
OpenAI / Claude API Costs money per call. With 100 resumes/month = $10-50. Use Ollama instead.
MongoDB Overkill for single-user local system. SQLite is 10x simpler and zero setup.
Redis Not needed. APScheduler handles job queuing. Adds unnecessary complexity.
Docker Adds complexity for personal use. Run services directly. Add Docker later for production.
Puppeteer (JS) Python ecosystem is better for this project. Playwright Python is identical in power.
AWS S3 (required) Store files locally first. Add S3 sync optionally. Keeps it free.
Next.js Overkill for local dashboard. Vite + React is faster to set up and run.

 
SECTION 4: COMPLETE FOLDER STRUCTURE
4.1 Root Project Structure
job-copilot/
├── backend/ # Python FastAPI backend
├── frontend/ # React + Vite dashboard
├── chrome-extension/ # Browser extension
├── data/ # All generated data
│ ├── resumes/ # Generated resumes per job
│ ├── exports/ # Daily Excel exports
│ ├── uploads/ # User uploaded master resume
│ └── db/ # SQLite database files
├── scripts/ # Utility scripts
├── docs/ # This documentation
├── .env # Environment variables
├── .gitignore
├── README.md
└── start.sh # One-command startup script

4.2 Backend Folder Structure (Python FastAPI)
backend/
├── main.py # FastAPI app entry point, router registration
├── config.py # All settings from .env
├── database.py # SQLAlchemy setup, DB connection, migrations
├── models/ # SQLAlchemy ORM models
│ ├── **init**.py
│ ├── job.py # Job model
│ ├── application.py # Application/tracking model
│ └── user_profile.py # User profile + skills model
├── routers/ # FastAPI route handlers
│ ├── **init**.py
│ ├── jobs.py # GET/POST /api/jobs
│ ├── resume.py # POST /api/resume/generate
│ ├── analyze.py # POST /api/analyze/jd
│ ├── score.py # POST /api/score/ats
│ ├── tracker.py # GET/PATCH /api/tracker
│ ├── scraper.py # POST /api/scrape/run
│ ├── profile.py # GET/POST /api/profile
│ └── export.py # GET /api/export/excel
├── services/ # Core business logic
│ ├── **init**.py
│ ├── llm_service.py # Ollama client wrapper
│ ├── embedding_service.py # sentence-transformers wrapper
│ ├── resume_parser.py # PDF/DOCX master resume parser
│ ├── jd_analyzer.py # Job description analyzer
│ ├── resume_generator.py # LLM-based resume tailoring
│ ├── ats_scorer.py # ATS score algorithm (0-100)
│ ├── file_builder.py # PDF + DOCX builder
│ ├── tracker_service.py # Job tracking operations
│ ├── excel_exporter.py # openpyxl Excel generation
│ └── cover_letter_service.py # Cover letter generator
├── scrapers/ # Job scrapers
│ ├── **init**.py
│ ├── base_scraper.py # Abstract base class
│ ├── linkedin_scraper.py # Playwright-based
│ ├── naukri_scraper.py # requests + BS4
│ ├── indeed_scraper.py # requests + BS4
│ ├── remotive_scraper.py # Free API — no scraping
│ └── wellfound_scraper.py # requests + BS4
├── scheduler/ # APScheduler nightly pipeline
│ ├── **init**.py
│ └── pipeline.py # Nightly job + resume pipeline
├── utils/ # Shared utilities
│ ├── **init**.py
│ ├── text_utils.py # Text cleaning helpers
│ └── file_utils.py # File path helpers
├── templates/ # Resume HTML templates (for PDF)
│ ├── resume_modern.html
│ ├── resume_classic.html
│ └── resume_minimal.html
└── requirements.txt

4.3 Frontend Folder Structure (React + Vite)
frontend/
├── index.html
├── vite.config.js
├── package.json
├── tailwind.config.js
├── postcss.config.js
├── src/
│ ├── main.jsx # React entry point
│ ├── App.jsx # Root component, router setup
│ ├── api/ # Axios API layer
│ │ ├── index.js # Axios instance with baseURL
│ │ ├── jobs.js # Job-related API calls
│ │ ├── resume.js # Resume API calls
│ │ └── tracker.js # Tracker API calls
│ ├── components/ # Reusable UI components
│ │ ├── Layout.jsx # Sidebar + topbar wrapper
│ │ ├── Sidebar.jsx # Navigation sidebar
│ │ ├── JobCard.jsx # Single job card widget
│ │ ├── ATSGauge.jsx # Circular score gauge (Recharts)
│ │ ├── StatusBadge.jsx # Coloured status pill
│ │ ├── ResumePreview.jsx # PDF iframe preview
│ │ ├── FilterBar.jsx # Role/score/status filters
│ │ └── SkillGapCard.jsx # Missing skills display
│ ├── pages/ # Route-level pages
│ │ ├── Dashboard.jsx # Home — stats overview
│ │ ├── JobsList.jsx # All scraped jobs table
│ │ ├── ApplicationTracker.jsx # Kanban + table view
│ │ ├── ResumeStudio.jsx # Generate + preview resumes
│ │ ├── Profile.jsx # Upload master resume + skills
│ │ ├── Settings.jsx # Ollama model, schedule config
│ │ └── SkillGap.jsx # Skill gap + learning plan
│ ├── hooks/ # Custom React hooks
│ │ ├── useJobs.js
│ │ ├── useATSScore.js
│ │ └── usePolling.js # Auto-refresh every 30s
│ ├── store/ # Zustand global state
│ │ └── useStore.js
│ └── utils/ # Frontend utilities
│ ├── formatters.js # Date, score formatters
│ └── constants.js # Status enums etc.
└── public/
└── favicon.ico

 
SECTION 5: DATABASE SCHEMA DESIGN
5.1 Schema Overview (SQLite via SQLAlchemy)
All data is stored in a single SQLite file at data/db/copilot.db. SQLAlchemy ORM handles all operations. Alembic handles migrations.

5.2 Table: user_profile
CREATE TABLE user_profile (
id INTEGER PRIMARY KEY AUTOINCREMENT,
full_name TEXT NOT NULL,
email TEXT,
phone TEXT,
location TEXT,
linkedin_url TEXT,
github_url TEXT,
target_roles TEXT, -- JSON: ["Software Engineer", "Backend Dev"]
target_locations TEXT, -- JSON: ["Bangalore", "Remote", "Lucknow"]
skills TEXT, -- JSON: ["Python", "React", "SQL", ...]
years_exp REAL,
resume_path TEXT, -- Path to master resume PDF
resume_text TEXT, -- Extracted plain text of master resume
resume_embedding TEXT, -- JSON: [0.12, -0.34, ...] 384-dim vector
created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

5.3 Table: jobs
CREATE TABLE jobs (
id INTEGER PRIMARY KEY AUTOINCREMENT,
title TEXT NOT NULL,
company TEXT NOT NULL,
location TEXT,
job_type TEXT, -- "full-time", "contract", "remote"
source TEXT, -- "linkedin", "naukri", "indeed", "manual"
job_url TEXT UNIQUE,
jd_text TEXT, -- Full job description raw text
jd_embedding TEXT, -- JSON: 384-dim vector for matching
keywords TEXT, -- JSON: extracted keywords
required_skills TEXT, -- JSON: ["Python", "AWS", "Docker"]
nice_to_have TEXT, -- JSON: optional skills
min_exp_years REAL,
max_exp_years REAL,
salary_range TEXT,
match_score REAL, -- 0.0-1.0 cosine similarity with user profile
scraped_at DATETIME DEFAULT CURRENT_TIMESTAMP,
is_active BOOLEAN DEFAULT 1
);

5.4 Table: applications (Job Tracker)
CREATE TABLE applications (
id INTEGER PRIMARY KEY AUTOINCREMENT,
job_id INTEGER REFERENCES jobs(id),
status TEXT DEFAULT "not_applied",
-- Status values: not_applied | applied | interview_r1 |
-- interview_r2 | offer | rejected | withdrawn
ats_score INTEGER, -- 0-100
resume_pdf_path TEXT, -- data/resumes/{company}/v{N}\_resume.pdf
resume_docx_path TEXT, -- data/resumes/{company}/v{N}\_resume.docx
cover_letter_path TEXT,
resume_version INTEGER DEFAULT 1,
tailored_skills TEXT, -- JSON: skills highlighted for this job
missing_skills TEXT, -- JSON: skills gap
notes TEXT, -- User notes
applied_date DATE,
interview_date DATETIME,
recruiter_name TEXT,
recruiter_email TEXT,
referral_email_path TEXT,
date_added DATETIME DEFAULT CURRENT_TIMESTAMP,
updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

5.5 Table: skills_library
CREATE TABLE skills_library (
id INTEGER PRIMARY KEY AUTOINCREMENT,
skill_name TEXT UNIQUE NOT NULL,
category TEXT, -- "language", "framework", "cloud", "database", "tool"
frequency INTEGER DEFAULT 0, -- How many JDs mention this skill
user_has BOOLEAN DEFAULT 0 -- Does user have this skill?
);

5.6 Table: scrape_runs (Audit Log)
CREATE TABLE scrape_runs (
id INTEGER PRIMARY KEY AUTOINCREMENT,
source TEXT, -- "linkedin" | "naukri" | "scheduler"
jobs_found INTEGER,
jobs_added INTEGER,
status TEXT, -- "success" | "failed" | "partial"
error_msg TEXT,
started_at DATETIME,
ended_at DATETIME
);

 
SECTION 6: COMPLETE API DESIGN
6.1 Base URL & Headers
Base URL: http://localhost:8000/api
All requests: Content-Type: application/json
Auto-generated interactive docs: http://localhost:8000/docs (Swagger UI)

6.2 Profile Endpoints
POST /api/profile/upload-resume
Upload master resume PDF or DOCX.
// Request: multipart/form-data
file: <binary PDF or DOCX>

// Response 200
{
"success": true,
"extracted_text": "John Doe\nSoftware Engineer...",
"skills_detected": ["Python", "React", "PostgreSQL"],
"years_experience": 2.5,
"resume_path": "data/uploads/master_resume.pdf"
}

GET /api/profile
// Response 200
{
"full_name": "John Doe",
"email": "john@example.com",
"skills": ["Python", "React", "FastAPI"],
"target_roles": ["Software Engineer", "Backend Developer"],
"years_exp": 2.5,
"resume_path": "data/uploads/master_resume.pdf"
}

6.3 Job Endpoints
GET /api/jobs
// Query params (all optional)
?status=not_applied // Filter by application status
?min_score=70 // Minimum ATS score
?source=linkedin // Filter by scrape source
?search=python // Full-text search in title/company
?limit=20&offset=0 // Pagination

// Response 200
{
"total": 142,
"jobs": [
{
"id": 1,
"title": "Software Engineer",
"company": "Razorpay",
"location": "Bangalore, Remote",
"source": "linkedin",
"job_url": "https://linkedin.com/jobs/...",
"match_score": 0.87,
"ats_score": 82,
"status": "not_applied",
"required_skills": ["Python", "Django", "AWS"],
"scraped_at": "2025-01-15T02:00:00"
}
]
}

POST /api/jobs/manual
// Request: Paste a job description manually
{
"title": "Backend Engineer",
"company": "Zepto",
"job_url": "https://zepto.com/careers/123",
"jd_text": "We are looking for a backend engineer..."
}

// Response 201
{
"job_id": 47,
"match_score": 0.79,
"keywords": ["Python", "FastAPI", "Redis", "Microservices"],
"message": "Job added. Ready to generate resume."
}

6.4 Scraper Endpoints
POST /api/scrape/run
// Request
{
"sources": ["linkedin", "naukri", "remotive"],
"keywords": ["software engineer", "python developer"],
"location": "Bangalore",
"max_per_source": 25
}

// Response 202 (async task)
{
"task_id": "scrape_20250115_141023",
"status": "started",
"message": "Scrape running in background. Check /api/scrape/status/{task_id}"
}

GET /api/scrape/status/{task_id}
// Response 200
{
"task_id": "scrape_20250115_141023",
"status": "completed",
"jobs_found": 67,
"jobs_added": 43,
"jobs_duplicate": 24,
"sources_completed": ["linkedin", "naukri", "remotive"],
"duration_seconds": 127
}

6.5 Resume Generation Endpoints
POST /api/resume/generate
// Request
{
"job_id": 47,
"template": "modern", // "modern" | "classic" | "minimal"
"include_cover_letter": true
}

// Response 200
{
"success": true,
"ats_score": 84,
"resume_pdf_url": "/api/files/resumes/zepto/v1_resume.pdf",
"resume_docx_url": "/api/files/resumes/zepto/v1_resume.docx",
"cover_letter_url": "/api/files/resumes/zepto/v1_cover_letter.pdf",
"missing_skills": ["Redis", "Kubernetes"],
"tailored_summary": "Results-driven backend engineer with 2.5 years...",
"keywords_added": ["FastAPI", "microservices", "REST API", "Python 3.11"]
}

GET /api/resume/score/{job_id}
// Response 200
{
"ats_score": 84,
"breakdown": {
"keyword_match": 32, // out of 40
"skills_coverage": 28, // out of 35
"format_compliance": 14, // out of 15
"experience_match": 10 // out of 10
},
"matched_keywords": ["Python", "FastAPI", "REST API", "PostgreSQL"],
"missing_keywords": ["Redis", "Kubernetes", "gRPC"],
"recommendations": [
"Add Redis experience from your internship project",
"Mention Docker/containerization skills",
"Add quantified metrics to your work experience bullets"
]
}

6.6 Tracker Endpoints
GET /api/tracker
// Response 200
{
"summary": {
"total": 58, "applied": 23, "interview": 4, "offer": 1, "rejected": 8
},
"applications": [
{
"id": 1, "company": "Razorpay", "role": "Software Engineer",
"ats_score": 82, "status": "interview_r1",
"applied_date": "2025-01-10", "interview_date": "2025-01-20",
"job_url": "https://...", "resume_pdf_url": "/api/files/...",
"notes": "HR call done. Tech round scheduled."
}
]
}

PATCH /api/tracker/{application_id}
// Request: Update status, add notes, record interview date
{
"status": "interview_r1",
"interview_date": "2025-01-20T10:00:00",
"notes": "HR call done. Tech round scheduled with team lead."
}

// Response 200
{
"success": true,
"application_id": 1,
"updated_fields": ["status", "interview_date", "notes"]
}

GET /api/export/excel
// Downloads tracker as Excel file
// Response: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
// Filename: job_tracker_2025-01-15.xlsx

// Excel columns:
// A: Company | B: Role | C: Location | D: Source | E: Job URL
// F: Resume Link | G: ATS Score | H: Status | I: Applied Date
// J: Interview Date | K: Notes | L: Match Score | M: Missing Skills

 
SECTION 7: AI PROMPT ENGINEERING
Model Used
All prompts use Ollama running mistral:7b or llama3.2:3b locally. No API key required. Install: ollama pull mistral

7.1 Master Prompt — Resume Tailoring
File: backend/services/resume_generator.py — The core prompt that generates the tailored resume content.

SYSTEM PROMPT:
"""
You are an expert resume writer and ATS optimization specialist with 10 years
of experience helping candidates get past Applicant Tracking Systems and land
interviews at top tech companies.

Your task is to rewrite a candidate's resume to be perfectly optimised for a
specific job description. Follow these STRICT rules:

RULES:

1. NEVER invent or fabricate experience, skills, or achievements the candidate
   does not have. Only reframe and highlight existing experience.
2. Mirror the exact keywords and phrases from the job description wherever true.
3. Quantify every achievement with numbers: "Improved performance by 40%",
   "Reduced load time by 2.3s", "Managed 5-person team".
4. Use strong action verbs: Architected, Engineered, Optimised, Deployed,
   Reduced, Increased, Built, Led, Delivered.
5. Keep bullet points to 1-2 lines. No paragraphs in experience section.
6. Summary must contain the exact job title the candidate is applying for.
7. Skills section must list ALL matching skills from JD first.
8. ATS-friendly: No tables, no graphics descriptions, no columns in text.
9. Output in the EXACT JSON structure provided. No extra text.
   """

USER PROMPT TEMPLATE:
"""
JOB DESCRIPTION:

---

## {job_description}

## CANDIDATE'S MASTER RESUME:

## {master_resume_text}

TARGET ROLE: {job_title} at {company_name}
REQUIRED SKILLS FROM JD: {required_skills_list}
KEYWORDS TO INCLUDE: {keywords_list}

Generate a tailored resume in this EXACT JSON format:
{
"summary": "3-4 sentence professional summary targeting this exact role",
"skills": {
"languages": ["Python", "JavaScript"],
"frameworks": ["FastAPI", "React"],
"databases": ["PostgreSQL", "Redis"],
"tools": ["Docker", "Git", "AWS"],
"other": ["REST APIs", "Agile", "CI/CD"]
},
"experience": [
{
"company": "Company Name",
"role": "Your Role",
"duration": "Jan 2023 - Present",
"bullets": [
"Action verb + what you did + measurable impact",
"Action verb + technology used + business result"
]
}
],
"projects": [
{
"name": "Project Name",
"tech_stack": "Python, FastAPI, PostgreSQL",
"description": "2-3 bullets highlighting relevance to this JD",
"bullets": ["Built X using Y, resulting in Z"]
}
],
"education": [
{
"degree": "B.Tech Computer Science",
"institution": "XYZ University",
"year": "2025",
"cgpa": "8.5/10",
"relevant_coursework": ["Data Structures", "DBMS", "OS"]
}
],
"certifications": ["AWS Cloud Practitioner", "Meta React Developer"],
"keywords_used": ["list", "of", "JD", "keywords", "added"]
}
"""

7.2 ATS Scoring Prompt
File: backend/services/ats_scorer.py — This prompt evaluates how well a resume matches a job description.

SYSTEM PROMPT:
"""
You are an ATS (Applicant Tracking System) scoring engine. Evaluate resumes
exactly as enterprise ATS software would: Workday, Greenhouse, Lever, iCIMS.
"""

USER PROMPT TEMPLATE:
"""
Score this resume against the job description. Return ONLY valid JSON.

JOB DESCRIPTION:
{job_description}

RESUME TEXT:
{resume_text}

Score on these 4 dimensions. Be strict and accurate:

1. KEYWORD_MATCH (0-40 points):
   Count exact keyword matches between JD and resume.
   Partial credit for synonyms. 40 = 90%+ keywords matched.

2. SKILLS_COVERAGE (0-35 points):
   How many required skills from JD appear in resume skills section?
   35 = all required skills present.

3. FORMAT_COMPLIANCE (0-15 points):
   ATS-parseable format: no tables, no images, standard section headings,
   proper dates, contact info present, summary/objective present.

4. EXPERIENCE_MATCH (0-10 points):
   Does years of experience and seniority level match JD requirements?
   10 = perfect match.

Return ONLY this JSON:
{
"total_score": 84,
"keyword_match": 32,
"skills_coverage": 28,
"format_compliance": 14,
"experience_match": 10,
"matched_keywords": ["Python", "FastAPI", "PostgreSQL", "REST"],
"missing_keywords": ["Redis", "Kubernetes", "gRPC"],
"matched_skills": ["Python", "React", "SQL"],
"missing_skills": ["Redis", "Docker", "CI/CD"],
"format_issues": [],
"recommendations": [
"Add Redis/caching experience to skills section",
"Mention containerization/Docker usage from projects",
"Add 2-3 quantified metrics to experience bullets"
]
}
"""

7.3 JD Analysis Prompt
USER PROMPT:
"""
Analyze this job description and extract structured information.
Return ONLY valid JSON. No preamble.

JOB DESCRIPTION:
{job_description}

{
"required_skills": ["Python", "Django", "PostgreSQL"],
"nice_to_have_skills": ["Redis", "Kubernetes"],
"min_exp_years": 2,
"max_exp_years": 5,
"seniority": "mid", // "intern" | "junior" | "mid" | "senior" | "lead"
"job_type": "full-time", // "full-time" | "contract" | "internship"
"work_mode": "hybrid", // "remote" | "onsite" | "hybrid"
"top_keywords": ["software engineer", "backend", "API", "scalable"],
"responsibilities": [
"Design and implement RESTful APIs",
"Collaborate with frontend team"
],
"company_culture_hints": ["fast-paced", "startup", "agile team"],
"salary_mentioned": "18-24 LPA",
"education_required": "B.Tech/B.E. in CS or related field"
}
"""

7.4 Cover Letter Prompt
SYSTEM: You are a professional cover letter writer who writes concise,
compelling, and personalised letters that get hiring managers to respond.

USER PROMPT:
"""
Write a cover letter for this candidate applying to this role.

Candidate Name: {full_name}
Target Role: {job_title} at {company_name}
Candidate's Top Skills: {top_5_matching_skills}
Candidate's Strongest Achievement: {top_achievement}

Job Description Summary: {jd_summary}

RULES:

- Maximum 3 paragraphs, under 250 words
- Paragraph 1: Why THIS company + role specifically (research-based)
- Paragraph 2: Your most relevant achievement + how it maps to their need
- Paragraph 3: Confident close with specific call to action
- Never start with "I am writing to..."
- Do NOT use generic phrases: "team player", "passionate", "hardworking"
- Use the company name exactly as provided

Return plain text only, no JSON, no markdown.
"""

7.5 Skill Gap Analysis Prompt
USER PROMPT:
"""
Compare this candidate profile against the top job requirements in their
target industry and identify skill gaps with a learning plan.

Candidate Skills: {user_skills_list}
Target Roles: {target_roles}
Top 20 most-required skills in these roles: {market_skills_from_db}

Return JSON:
{
"critical_gaps": [
{
"skill": "Docker",
"demand_percentage": 73,
"learning_resource": "Docker official docs + TechWorld with Nana YouTube",
"estimated_hours": 20,
"priority": "high"
}
],
"optional_gaps": [...],
"strengths": ["Python", "React", "SQL"],
"30_day_plan": [
"Week 1: Docker fundamentals (dockerize your projects)",
"Week 2: Kubernetes basics (minikube locally)",
"Week 3: CI/CD with GitHub Actions",
"Week 4: Add all to resume + 1 demo project"
]
}
"""

 
SECTION 8: KEY IMPLEMENTATION CODE
8.1 Backend Entry Point — main.py

# backend/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from database import init_db
from scheduler.pipeline import start_scheduler
from routers import jobs, resume, analyze, score, tracker, scraper, profile, export_router

@asynccontextmanager
async def lifespan(app: FastAPI):
init_db() # Create tables if not exist
start_scheduler() # Start nightly cron
yield # cleanup on shutdown

app = FastAPI(
title="Job Application Copilot API",
version="1.0.0",
lifespan=lifespan
)

app.add_middleware(CORSMiddleware,
allow_origins=["http://localhost:3000"],
allow_methods=["*"], allow_headers=["*"]
)

# Serve generated files

app.mount("/api/files", StaticFiles(directory="../data"), name="data")

# Register routers

app.include_router(profile.router, prefix="/api/profile", tags=["Profile"])
app.include_router(jobs.router, prefix="/api/jobs", tags=["Jobs"])
app.include_router(scraper.router, prefix="/api/scrape", tags=["Scraper"])
app.include_router(resume.router, prefix="/api/resume", tags=["Resume"])
app.include_router(score.router, prefix="/api/score", tags=["ATS Score"])
app.include_router(tracker.router, prefix="/api/tracker", tags=["Tracker"])
app.include_router(export_router.router, prefix="/api/export", tags=["Export"])

8.2 LLM Service — llm_service.py

# backend/services/llm_service.py

import httpx, json
from config import settings

class OllamaService:
def **init**(self):
self.base_url = settings.OLLAMA_URL # http://localhost:11434
self.model = settings.LLM_MODEL # mistral:7b

    async def generate(self, system_prompt: str, user_prompt: str,
                        max_tokens: int = 4096) -> str:
        """Single generation call to Ollama"""
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user",   "content": user_prompt}
                    ],
                    "stream": False,
                    "options": {"num_predict": max_tokens, "temperature": 0.3}
                }
            )
        return response.json()["message"]["content"]

    async def generate_json(self, system_prompt: str,
                             user_prompt: str) -> dict:
        """Generate and auto-parse JSON response"""
        raw = await self.generate(system_prompt, user_prompt)
        # Strip markdown code fences if present
        clean = raw.strip().strip("```json").strip("```").strip()
        return json.loads(clean)

llm = OllamaService()

8.3 Embedding & Matching Service

# backend/services/embedding_service.py

from sentence_transformers import SentenceTransformer
import numpy as np

class EmbeddingService:
def **init**(self): # Downloads ~90MB once, then cached locally
self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def embed(self, text: str) -> list[float]:
        """Convert text to 384-dim embedding vector"""
        return self.model.encode(text, normalize_embeddings=True).tolist()

    def cosine_similarity(self, vec1: list, vec2: list) -> float:
        """Calculate similarity between two embeddings (0.0 - 1.0)"""
        a = np.array(vec1)
        b = np.array(vec2)
        return float(np.dot(a, b))  # Already normalised, dot = cosine

    def match_score(self, user_profile_text: str, job_jd_text: str) -> float:
        """One-call match scoring for a job vs user profile"""
        user_vec = self.embed(user_profile_text)
        job_vec = self.embed(job_jd_text)
        return self.cosine_similarity(user_vec, job_vec)

embedder = EmbeddingService()

8.4 ATS Scorer — ats_scorer.py

# backend/services/ats_scorer.py

# Hybrid scorer: algorithmic (fast) + LLM (detailed recommendations)

import re
from services.llm_service import llm

class ATSScorer:
def algorithmic_score(self, resume_text: str,
keywords: list, required_skills: list) -> dict:
"""Fast deterministic score — no LLM call"""
resume_lower = resume_text.lower()

        # 1. Keyword match (0-40)
        matched_kw = [k for k in keywords if k.lower() in resume_lower]
        kw_score = min(40, int((len(matched_kw)/max(len(keywords),1)) * 40))

        # 2. Skills coverage (0-35)
        matched_sk = [s for s in required_skills if s.lower() in resume_lower]
        sk_score = min(35, int((len(matched_sk)/max(len(required_skills),1)) * 35))

        # 3. Format compliance (0-15)
        sections = ["experience", "education", "skills", "projects"]
        found_sections = sum(1 for s in sections if s in resume_lower)
        has_email = bool(re.search(r"[w.-]+@[w.-]+.w+", resume_text))
        has_phone = bool(re.search(r"[+d][ds-()]{8,}", resume_text))
        fmt_score = (found_sections * 3) + (has_email * 2) + (has_phone * 1)
        fmt_score = min(15, fmt_score)

        # 4. Experience match — basic check (0-10)
        exp_score = 8  # Default, LLM call gives precise score

        total = kw_score + sk_score + fmt_score + exp_score
        return {
            "total_score": total,
            "keyword_match": kw_score,
            "skills_coverage": sk_score,
            "format_compliance": fmt_score,
            "experience_match": exp_score,
            "matched_keywords": matched_kw,
            "missing_keywords": [k for k in keywords if k not in matched_kw],
            "matched_skills": matched_sk,
            "missing_skills": [s for s in required_skills if s not in matched_sk]
        }

    async def llm_score(self, resume_text: str, jd_text: str) -> dict:
        """Slower but precise — includes recommendations"""
        from services.prompt_templates import ATS_SCORE_SYSTEM, ats_score_user
        return await llm.generate_json(
            ATS_SCORE_SYSTEM,
            ats_score_user(jd_text, resume_text)
        )

ats_scorer = ATSScorer()

8.5 Naukri Scraper (Free, No Login Required)

# backend/scrapers/naukri_scraper.py

import requests, time, random
from bs4 import BeautifulSoup
from scrapers.base_scraper import BaseScraper

class NaukriScraper(BaseScraper):
BASE_URL = "https://www.naukri.com/{role}-jobs-in-{location}"
HEADERS = {
"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
"AppleWebKit/537.36 (KHTML, like Gecko) "
"Chrome/120.0.0.0 Safari/537.36",
"Accept-Language": "en-IN,en;q=0.9",
}

    def scrape(self, role: str, location: str = "india",
               max_jobs: int = 25) -> list[dict]:
        url = self.BASE_URL.format(
            role=role.lower().replace(" ", "-"),
            location=location.lower().replace(" ", "-")
        )
        jobs = []
        try:
            time.sleep(random.uniform(2, 4))  # Respectful delay
            resp = requests.get(url, headers=self.HEADERS, timeout=15)
            soup = BeautifulSoup(resp.text, "html.parser")
            cards = soup.select("article.jobTuple")[:max_jobs]
            for card in cards:
                title = card.select_one(".title")?.get_text(strip=True)
                company = card.select_one(".subTitle")?.get_text(strip=True)
                link_tag = card.select_one("a.title")
                job_url = link_tag["href"] if link_tag else ""
                location_el = card.select_one(".location")
                loc = location_el.get_text(strip=True) if location_el else ""
                exp_el = card.select_one(".experience")
                exp = exp_el.get_text(strip=True) if exp_el else ""
                if title and company:
                    jobs.append({
                        "title": title, "company": company,
                        "location": loc, "job_url": job_url,
                        "experience": exp, "source": "naukri"
                    })
                time.sleep(random.uniform(0.5, 1.5))
        except Exception as e:
            print(f"Naukri scrape error: {e}")
        return jobs

8.6 Remotive Free API (No Scraping Needed)

# backend/scrapers/remotive_scraper.py

# Remotive.io has a FREE public API — no auth, no rate limits listed

import httpx

class RemotiveScraper:
API_URL = "https://remotive.com/api/remote-jobs"

    async def scrape(self, role: str, max_jobs: int = 25) -> list[dict]:
        async with httpx.AsyncClient() as client:
            resp = await client.get(self.API_URL, params={
                "search": role, "limit": max_jobs
            })
        data = resp.json()
        jobs = []
        for j in data.get("jobs", [])[:max_jobs]:
            jobs.append({
                "title": j["title"],
                "company": j["company_name"],
                "location": j.get("candidate_required_location", "Remote"),
                "job_url": j["url"],
                "jd_text": j.get("description", ""),
                "job_type": j.get("job_type", "full_time"),
                "source": "remotive"
            })
        return jobs

8.7 Nightly Scheduler — pipeline.py

# backend/scheduler/pipeline.py

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from services.llm_service import llm
from services.embedding_service import embedder
from services.ats_scorer import ats_scorer
from services.resume_generator import resume_generator
from services.tracker_service import tracker_service
from services.excel_exporter import excel_exporter
from scrapers.naukri_scraper import NaukriScraper
from scrapers.remotive_scraper import RemotiveScraper
from database import get_db
import logging

logger = logging.getLogger(**name**)

async def nightly_pipeline():
"""Full pipeline: scrape → filter → generate resumes → export"""
logger.info("=== NIGHTLY PIPELINE STARTED ===")
db = next(get_db())
user = db.query(UserProfile).first()
if not user: return

    # 1. Scrape new jobs
    scrapers = [NaukriScraper(), RemotiveScraper()]
    all_jobs = []
    for scraper in scrapers:
        jobs = await scraper.scrape(role="software engineer")
        all_jobs.extend(jobs)
    logger.info(f"Scraped {len(all_jobs)} raw jobs")

    # 2. Filter by semantic match score
    user_profile_text = f"{user.skills} {user.target_roles} {user.resume_text}"
    new_jobs = []
    for job_data in all_jobs:
        jd_text = job_data.get("jd_text", job_data.get("title",""))
        match = embedder.match_score(user_profile_text, jd_text)
        if match >= 0.62:  # Threshold: adjust based on quality
            job_data["match_score"] = match
            new_jobs.append(job_data)
    logger.info(f"Filtered to {len(new_jobs)} relevant jobs")

    # 3. Save to DB + generate resumes for top matches
    for job_data in new_jobs:
        job = save_job_to_db(db, job_data)
        if job_data["match_score"] >= 0.75:  # Auto-generate for top matches
            await resume_generator.generate(job.id, user)

    # 4. Export Excel tracker
    excel_exporter.export(db)
    logger.info("=== NIGHTLY PIPELINE COMPLETE ===")

def start_scheduler():
scheduler = AsyncIOScheduler()
scheduler.add_job(
nightly_pipeline,
CronTrigger(hour=2, minute=0), # 2:00 AM every night
id="nightly_pipeline",
replace_existing=True
)
scheduler.start()
logger.info("Scheduler started — nightly job at 2:00 AM")

 
SECTION 9: COMPLETE SETUP GUIDE (ZERO TO RUNNING)
9.1 Prerequisites
Requirement How to Install
Python 3.11+ sudo apt install python3.11 OR brew install python@3.11
Node.js 20+ Download from nodejs.org OR brew install node
Ollama curl -fsSL https://ollama.com/install.sh | sh
Git sudo apt install git OR brew install git
4GB+ RAM free Mistral 7B needs ~4GB RAM while running
10GB+ disk space For models, generated files, and dependencies

9.2 Step-by-Step Installation
Step 1 — Clone & Setup

# Create project

mkdir job-copilot && cd job-copilot
git init

# Create folder structure

mkdir -p backend frontend chrome-extension
mkdir -p data/resumes data/exports data/uploads data/db

Step 2 — Install Ollama & Pull Models

# Install Ollama (Linux/Mac)

curl -fsSL https://ollama.com/install.sh | sh

# Pull the models (one-time, ~4GB total)

ollama pull mistral # Main model for resume generation
ollama pull llama3.2:3b # Faster model for quick ATS scoring

# Verify Ollama is running

ollama list

# Should show: mistral:latest, llama3.2:3b

# Test it works

ollama run mistral "Say hello in one sentence"

Step 3 — Backend Setup
cd backend

# Create virtual environment

python -m venv venv
source venv/bin/activate # Linux/Mac

# venv\Scripts\activate # Windows

# Install all dependencies

pip install fastapi uvicorn[standard] sqlalchemy aiosqlite
pip install sentence-transformers httpx python-multipart
pip install beautifulsoup4 requests playwright
pip install python-docx weasyprint openpyxl
pip install pymupdf apscheduler python-dotenv

# Install Playwright browsers

playwright install chromium

# Create .env file

cat > ../.env << EOF
OLLAMA_URL=http://localhost:11434
LLM_MODEL=mistral
FAST_MODEL=llama3.2:3b
DB_PATH=../data/db/copilot.db
DATA_DIR=../data
SCRAPE_DELAY_MIN=2
SCRAPE_DELAY_MAX=5
MIN_MATCH_SCORE=0.62
EOF

# Start the backend

uvicorn main:app --reload --port 8000

# Visit: http://localhost:8000/docs

Step 4 — Frontend Setup
cd ../frontend

# Create Vite + React project

npm create vite@latest . -- --template react
npm install

# Install dependencies

npm install axios recharts react-router-dom
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p

# Configure Vite proxy (add to vite.config.js)

server: {
proxy: {
'/api': 'http://localhost:8000'
}
}

# Start frontend

npm run dev

# Visit: http://localhost:3000

Step 5 — One-Command Startup Script

# Create start.sh in project root

cat > start.sh << EOF
#!/bin/bash
echo "Starting Job Application Copilot..."

# Start Ollama in background

ollama serve &
sleep 2

# Start backend

cd backend && source venv/bin/activate
uvicorn main:app --reload --port 8000 &
cd ..

# Start frontend

cd frontend && npm run dev &
cd ..

echo "All services started!"
echo "Dashboard: http://localhost:3000"
echo "API Docs: http://localhost:8000/docs"
wait
EOF

chmod +x start.sh
./start.sh

 
SECTION 10: IMPLEMENTATION TIMELINE
10.1 7-Day MVP Plan — Ship Something That Works

Day Focus Deliverable
Day 1 Foundation Setup Python env, FastAPI skeleton, SQLite schema, Ollama installed. Test LLM works. GOAL: "Hello World" API running.
Day 2 Resume Parser + Profile Build resume_parser.py to extract text from PDF/DOCX. Build /api/profile endpoints. Upload master resume via UI. GOAL: Profile page working.
Day 3 JD Analysis + ATS Score Build jd_analyzer.py + ats_scorer.py. Test prompts with Ollama. Build /api/score endpoint. GOAL: Paste a JD and get a score.
Day 4 Resume Generator Build resume_generator.py with tailoring prompt. Build file_builder.py for DOCX/PDF output. GOAL: Generate tailored resume from JD.
Day 5 Scrapers (Remotive + Naukri) Build Remotive API scraper (easiest — free API). Build Naukri BS4 scraper. Build /api/scrape endpoints. GOAL: 20+ jobs auto-scraped.
Day 6 Tracker + Excel Export Build tracker_service.py + excel_exporter.py. Build /api/tracker endpoints. GOAL: Download working Excel tracker.
Day 7 React Dashboard Build minimal React UI: Job list, ATS gauges, Resume download, Status update. GOAL: Full working dashboard at localhost:3000.

10.2 30-Day Production Roadmap
Phase Theme Work Done
Week 1 (Days 1-7) MVP Working local system per 7-day plan above
Week 2 (Days 8-14) Quality LinkedIn scraper (Playwright), cover letter generator, skill gap analyzer, resume template improvements, error handling & logging
Week 3 (Days 15-21) Polish Chrome extension for 1-click JD capture, referral email generator, resume versioning UI, APScheduler nightly pipeline, dashboard charts & filters
Week 4 (Days 22-30) Scale Multiple resume templates, batch score recalculation, Google Drive sync (optional), performance optimisation, comprehensive README

 
SECTION 11: CHROME EXTENSION
11.1 Extension Structure
chrome-extension/
├── manifest.json
├── popup.html
├── popup.js
├── content.js # Injected into job pages to extract JD
├── background.js # Service worker
└── icon.png

11.2 manifest.json
{
"manifest_version": 3,
"name": "Job Copilot - Capture JD",
"version": "1.0",
"description": "1-click job description capture to your local copilot",
"permissions": ["activeTab", "scripting"],
"host_permissions": ["http://localhost:8000/*"],
"action": { "default_popup": "popup.html" },
"content_scripts": [{
"matches": ["*://www.linkedin.com/jobs/*",
"*://www.naukri.com/*",
"*://in.indeed.com/*"],
"js": ["content.js"]
}]
}

11.3 content.js — JD Extractor
// content.js — Extracts job description from current page
function extractJobData() {
const hostname = window.location.hostname;

if (hostname.includes("linkedin")) {
return {
title: document.querySelector(".job-details-jobs-unified-top-card**job-title")?.innerText,
company: document.querySelector(".job-details-jobs-unified-top-card**company-name")?.innerText,
jd_text: document.querySelector(".jobs-description\_\_content")?.innerText,
job_url: window.location.href,
source: "linkedin"
};
}

if (hostname.includes("naukri")) {
return {
title: document.querySelector(".jd-header-title")?.innerText,
company: document.querySelector(".jd-header-comp-name")?.innerText,
jd_text: document.querySelector(".job-desc")?.innerText,
job_url: window.location.href,
source: "naukri"
};
}

// Fallback: grab all visible text
return {
title: document.title,
company: "",
jd_text: document.body.innerText.substring(0, 5000),
job_url: window.location.href,
source: "manual"
};
}

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
if (msg.action === "extractJD") {
sendResponse(extractJobData());
}
});

11.4 popup.js — Send to API
// popup.js
document.getElementById("captureBtn").addEventListener("click", async () => {
const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

const jobData = await chrome.scripting.executeScript({
target: { tabId: tab.id },
func: () => window.extractJobData?.() || { error: "No extractor found" }
});

const data = jobData[0].result;
const statusEl = document.getElementById("status");

try {
const response = await fetch("http://localhost:8000/api/jobs/manual", {
method: "POST",
headers: { "Content-Type": "application/json" },
body: JSON.stringify(data)
});
const result = await response.json();
statusEl.textContent = `Captured! Match: ${(result.match_score*100).toFixed(0)}%`;
statusEl.style.color = "green";
} catch (e) {
statusEl.textContent = "Error: Is the copilot running?";
statusEl.style.color = "red";
}
});

11.5 Installing the Extension

1. Open Chrome → chrome://extensions
2. Enable "Developer mode" (top right toggle)
3. Click "Load unpacked"
4. Select the chrome-extension/ folder
5. Extension icon appears in toolbar
6. Navigate to any job page → click icon → click "Capture This Job"

 
SECTION 12: ETHICAL SCRAPING & ANTI-BAN STRATEGY
12.1 Legal & Ethical Guidelines
IMPORTANT LEGAL NOTE
Only scrape publicly visible job listings. Never scrape behind login. Never store personal data of recruiters/candidates. Always respect robots.txt. This system is for personal job searching only — not commercial reselling of data.

12.2 Anti-Ban Techniques Implemented
Technique Implementation
Randomised delays 2-5 second random sleep between each request — mimics human browsing speed
User-agent rotation Rotate through 5 real Chrome/Firefox user-agent strings
Rate limiting Max 25 jobs per scrape run per source — never bulk-crawl
Session reuse Single Playwright browser session per run — not a new browser per page
Robots.txt check base_scraper.py reads robots.txt before scraping any domain
No login scraping All scrapers only access public-facing job listings (no session cookies)
Priority: APIs first Use Remotive free API, JobsPikr free tier — zero scraping needed
Off-peak scheduling Nightly pipeline runs at 2 AM — lowest traffic period
Error backoff On 429/503, wait 30+ minutes before retry — never hammer blocked endpoint

12.3 Free Data Sources (No Scraping Required)
Source Details
Remotive.io API https://remotive.com/api/remote-jobs — No auth, free, 1000+ remote jobs
Adzuna API Free tier: 250 calls/month — India jobs available, no scraping
The Muse API Free public API — tech & startup jobs, global
GitHub Jobs (archived) GitHub Jobs JSON file still exists and is public
LinkedIn RSS (unofficial) linkedin.com/jobs/search/?keywords=...&format=json — limited
Naukri public pages Public search results — scrape respectfully
Indeed India public pages in.indeed.com/jobs — public, scrape with delays

 
SECTION 13: DEPENDENCY FILES
13.1 backend/requirements.txt

# Web Framework

fastapi==0.115.0
uvicorn[standard]==0.30.0

# Database

sqlalchemy==2.0.35
aiosqlite==0.20.0
alembic==1.13.0

# AI / ML

sentence-transformers==3.0.0
httpx==0.27.0

# File Parsing

pymupdf==1.24.0 # PDF parsing (import as fitz)
python-docx==1.1.0 # DOCX parsing + creation
weasyprint==62.0 # HTML to PDF generation

# Scraping

requests==2.32.0
beautifulsoup4==4.12.0
playwright==1.45.0
lxml==5.2.0

# Excel Export

openpyxl==3.1.5

# Scheduler

apscheduler==3.10.4

# Utilities

python-multipart==0.0.9 # File upload in FastAPI
python-dotenv==1.0.0
pydantic==2.7.0
pydantic-settings==2.3.0
aiofiles==23.2.1

13.2 frontend/package.json (key dependencies)
{
"name": "job-copilot-frontend",
"version": "1.0.0",
"dependencies": {
"react": "^18.3.0",
"react-dom": "^18.3.0",
"react-router-dom": "^6.26.0",
"axios": "^1.7.0",
"recharts": "^2.12.0",
"zustand": "^4.5.0",
"@heroicons/react": "^2.1.0",
"react-hot-toast": "^2.4.0",
"react-pdf": "^8.0.0",
"date-fns": "^3.6.0"
},
"devDependencies": {
"@vitejs/plugin-react": "^4.3.0",
"vite": "^5.3.0",
"tailwindcss": "^3.4.0",
"autoprefixer": "^10.4.0",
"postcss": "^8.4.0"
}
}

 
SECTION 14: CHALLENGES & SOLUTIONS
Challenge Solution
Ollama too slow on laptop Use llama3.2:3b for ATS scoring (fast). Use mistral only for resume generation. Enable GPU in Ollama if available. Process resumes in background, not blocking UI.
LinkedIn blocks scraping Use Playwright with human-like delays. Alternatively: use the Chrome extension to manually capture JDs — MORE reliable, zero ban risk. Use Remotive API for remote jobs.
LLM hallucinates fake skills Validate LLM output: check that all skills in generated resume exist in master resume. Add validation function that compares generated skills against known user skills.
ATS score not accurate Use hybrid scoring: algorithmic score (fast, deterministic) + LLM recommendations (slow, qualitative). Real ATS systems use keyword density, not AI — algorithmic is closer to reality.
PDF resume formatting issues Use HTML templates with WeasyPrint. Test rendered PDF in 3 ATS systems (Greenhouse test, Lever test). Use single-column layout — multi-column breaks most ATS parsers.
SQLite concurrent writes FastAPI async + aiosqlite handles concurrency safely for single user. If multiple users needed: upgrade to PostgreSQL. For personal use: SQLite is perfectly fine.
Duplicate job detection Use job_url as UNIQUE constraint in DB. Before inserting, check if URL exists. For jobs without stable URLs: hash(company+title+location) as dedup key.
Generated resume too long Add token limit in LLM prompt: "Resume must fit 1 page. Maximum 550 words total." Add word count validation and trim bullet points if over limit.
Naukri/Indeed change HTML Add scraper health check: if scraped_jobs == 0 for 3 runs, email/notify user. Scrapers need periodic maintenance — plan 1 hour/month for scraper upkeep.
User has no measurable achievements Add a "Achievement Builder" prompt: "Given this project/internship: {description}, suggest 3 quantified bullet points using estimated realistic metrics." Educate user.

 
SECTION 15: DEPLOYMENT OPTIONS
15.1 Local Only (Recommended for Students)
Run everything on your own laptop. Zero cost. Full control. All data stays local.

# Single command to start everything

./start.sh

# Access from other devices on same network (mobile)

uvicorn main:app --host 0.0.0.0 --port 8000 # Backend
npm run dev -- --host # Frontend

# Your IP: find with "ip addr" or "ifconfig"

# Access: http://192.168.1.X:3000

15.2 Optional Cloud Deployment (If Needed)
Component Option
Frontend → Vercel Push frontend/ to GitHub. Connect to Vercel. Auto-deploys on push. Free tier. URL: job-copilot.vercel.app
Backend → Railway.app Free $5/month credit. Deploy FastAPI with Dockerfile. Persistent storage for SQLite. Easy PostgreSQL upgrade.
Backend → Render.com Free tier available. Auto-sleep after 15min (bad for scheduler). Upgrade to $7/month to keep awake for cron jobs.
Ollama → Not cloud Ollama cannot run on free cloud tiers (needs GPU/RAM). Keep LLM local OR use Groq free API (llama3-70b, free tier, fast).
Files → Supabase Storage Free 1GB storage. SDK available for Python. Easy to swap local file paths to Supabase URLs.
DB → Supabase PostgreSQL Free tier: 500MB. Change SQLAlchemy URL from sqlite to postgresql+psycopg2.

15.3 If You Want Cloud LLM (Groq — Free)

# Groq API is FREE with generous limits

# Models: llama3-70b-8192, mixtral-8x7b, gemma2-9b

# Limits: 14,400 requests/day, 500,000 tokens/minute

# In .env:

LLM_PROVIDER=groq
GROQ_API_KEY=gsk_your_key_here # Get free at console.groq.com

# In llm_service.py, add Groq client:

from groq import AsyncGroq
client = AsyncGroq(api_key=settings.GROQ_API_KEY)

async def generate_groq(self, system: str, user: str) -> str:
completion = await client.chat.completions.create(
model="llama3-70b-8192",
messages=[{"role":"system","content":system},
{"role":"user","content":user}],
temperature=0.3, max_tokens=4096
)
return completion.choices[0].message.content

 
SECTION 16: EXCEL TRACKER & EXTRA FEATURES
16.1 Excel Tracker Column Design
Column Type Example
A: Company TEXT Razorpay, Google, Zepto
B: Role TEXT Software Engineer, Backend Dev
C: Location TEXT Bangalore / Remote / Hybrid
D: Source TEXT linkedin, naukri, remotive, manual
E: Job URL HYPERLINK Direct link to job posting
F: Resume Link HYPERLINK Link to generated PDF resume
G: ATS Score INTEGER (0-100) Coloured: Green 80+, Yellow 60-79, Red <60
H: Match Score PERCENTAGE Semantic similarity: 87%, 65%
I: Status DROPDOWN Not Applied / Applied / Interview R1 / Offer
J: Date Added DATE Auto-filled by system
K: Applied Date DATE Manually updated
L: Interview Date DATE HR round date
M: Missing Skills TEXT Redis, Docker, K8s
N: Notes TEXT Free text notes per application
O: Referral Status TEXT Not sent / Sent to {name}

16.2 Referral Email Template Generator

# backend/services/referral_email_service.py

# Prompt to generate personalised referral outreach

REFERRAL_PROMPT = """
Write a short, professional LinkedIn message or email to request a referral.

Sender: {my_name} ({my_role}, {my_college}, graduating {my_year})
Target: Employee at {company_name} in {their_department}
Role I'm applying for: {target_role}
Connection context: {how_we_are_connected}

RULES:

- Maximum 150 words
- Do NOT ask directly for a referral in the first message
- Show genuine interest in their work/company first
- Mention 1 specific thing about the company you admire
- End with a soft ask: "Would love to learn about your experience there"
- Output: Subject line + Email body as plain text
  """

  16.3 Skill Gap Analyzer — Learning Plan
  The skill gap analyzer compares your skills against the top 50 most-demanded skills in your target roles (aggregated from all scraped JDs in your database).
  • Query DB: SELECT skill_name, COUNT(\*) FROM skills_library WHERE user_has=0 GROUP BY skill_name ORDER BY frequency DESC LIMIT 20
  • Send top gaps to LLM with learning resource prompt
  • Generate 30-day personalised learning plan with free resources
  • Display on /skill-gap page with priority ranking and estimated hours

 
SECTION 17: SUCCESS CHECKLIST & METRICS
17.1 "Is My System Working?" Checklist
• Ollama running: curl http://localhost:11434/api/tags returns model list
• Backend running: http://localhost:8000/docs shows Swagger UI
• Frontend running: http://localhost:3000 shows dashboard
• Profile uploaded: Master resume parsed, skills detected
• First scrape done: 10+ jobs appear in job list
• Resume generated: Click "Generate Resume" → PDF downloads
• ATS score shown: Score visible in job list
• Excel exported: /api/export/excel downloads .xlsx file
• Tracker updated: Change status on a job → persists after refresh
• Nightly scheduler: Check logs at 2 AM — jobs scraped automatically

17.2 Target Metrics for Success
Metric Target & Notes
ATS Score Target Aim for 75+ on every application you submit. Below 65 = do not apply yet.
Jobs Scraped/Week 50-100 relevant jobs per week across all sources
Applications/Week 10-15 high-quality tailored applications (not 100 generic ones)
Interview Rate Target 5-10% of applications → interview call (industry average is 2-3%)
Match Score Filter Only apply to jobs with semantic match score > 0.65
Resume Generation Time Should take 30-90 seconds per resume with Mistral 7B
Scrape Duration Full nightly scrape (all sources) should complete in under 10 minutes

17.3 Quick Reference: Key URLs & Commands
Item Value
Dashboard http://localhost:3000
API Swagger Docs http://localhost:8000/docs
Ollama API http://localhost:11434
Start everything ./start.sh
Manual scrape POST http://localhost:8000/api/scrape/run
Download Excel GET http://localhost:8000/api/export/excel
Test LLM ollama run mistral "Hello"
View DB sqlite3 data/db/copilot.db ".tables"
View logs tail -f backend/app.log

FINAL ADVICE FROM THE ARCHITECT
The system is only as good as your master resume. Before running the pipeline, spend 2 hours perfecting your master resume — quantified achievements, strong action verbs, and honest skills. The AI can tailor, but it cannot create achievements that don't exist. Quality over quantity: 15 tailored 80+ ATS-score applications will get you more interviews than 200 generic ones.

END OF DOCUMENTATION
