"""
PROJECT STRUCTURE - Instagram Hashtag Scraper
Complete file organization and module descriptions
"""

PROJECT_STRUCTURE = """
instagram-scraper/
│
├── 📄 README.md                    # Project overview & setup guide
├── 📄 requirements.txt             # Python dependencies
├── 📄 .env.example                 # Environment variables template
├── 📄 .env                         # Environment variables (local - DO NOT commit)
├── 📄 .gitignore                   # Git ignore rules
│
├── 🔧 CORE MODULES (PHASE 1) ✅
│   ├── scraper.py                 # Main scraper logic (instagrapi)
│   │   ├── PostType               # Enum: Photo, Reel, Carousel, Story
│   │   ├── InstagramPost           # Data class for posts
│   │   ├── RateLimiter             # Rate limiting with jitter
│   │   └── InstagramHashtagScraper # Main scraper class
│   │
│   ├── csv_exporter.py            # CSV export functionality
│   │   ├── CSVExporter             # Handles CSV generation
│   │   └── Methods:
│   │       ├── export()            # Export posts to CSV
│   │       ├── export_multiple_hashtags()
│   │       ├── get_export_stats()  # Calculate statistics
│   │       └── cleanup_old_files()
│   │
│   ├── models.py                  # Database models & ORM
│   │   ├── JobStatus              # Enum: pending, running, completed, failed
│   │   ├── User                    # User account model
│   │   ├── ScrapingJob             # Job tracking model
│   │   └── Database                # Database management class
│   │
│   └── config.py                  # Configuration management
│       ├── Config                  # Base config
│       ├── DevelopmentConfig       # Dev settings
│       ├── ProductionConfig        # Prod settings
│       ├── TestingConfig           # Test settings
│       └── setup_logging()
│
├── 📦 API BACKEND (PHASE 2) ⏳
│   ├── app.py                     # Flask application setup
│   ├── auth.py                    # User authentication & JWT
│   ├── routes.py                  # API endpoints
│   └── background_worker.py       # Job processing (Celery/RQ)
│
├── 🎨 FRONTEND (PHASE 3) ⏳
│   ├── frontend/
│   │   ├── src/
│   │   │   ├── App.jsx
│   │   │   ├── pages/
│   │   │   │   ├── Home.jsx       # Main form/dashboard
│   │   │   │   ├── Register.jsx   # User registration
│   │   │   │   ├── Login.jsx      # User login
│   │   │   │   └── Jobs.jsx       # Job history
│   │   │   ├── components/
│   │   │   │   ├── ScraperForm.jsx
│   │   │   │   ├── JobStatus.jsx
│   │   │   │   └── CSVDownload.jsx
│   │   │   └── api/
│   │   │       └── client.js      # API client
│   │   └── package.json
│
├── 🐳 DEPLOYMENT (PHASE 4) ⏳
│   ├── Dockerfile                 # Container configuration
│   ├── docker-compose.yml         # Multi-container setup
│   └── nginx.conf                 # Web server config
│
├── 📊 DATA & LOGS
│   ├── data/
│   │   └── instagram_scraper.db   # SQLite database (generated)
│   ├── logs/
│   │   └── app.log                # Application logs (generated)
│   ├── exports/                   # Generated CSV files (generated)
│   └── test_exports/              # Test CSV files (generated)
│
└── 🧪 TESTING
    ├── test_phase1.py             # Phase 1 test suite
    ├── tests/
    │   ├── test_scraper.py        # Scraper unit tests
    │   ├── test_csv_exporter.py   # CSV exporter tests
    │   ├── test_models.py         # Database model tests
    │   └── test_api.py            # API endpoint tests
    └── conftest.py                # Pytest configuration
"""

PHASE_1_MODULES = """
═════════════════════════════════════════════════════════════════
PHASE 1: CORE SCRAPER MODULE (✅ COMPLETE)
═════════════════════════════════════════════════════════════════

MODULE: scraper.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Purpose: Main Instagram scraping logic
Dependencies: instagrapi, requests, typing, logging
Key Classes:
  - PostType (Enum)
  - InstagramPost (Dataclass)
  - RateLimiter (Rate limiting with jitter)
  - InstagramHashtagScraper (Main class)

Usage:
  scraper = InstagramHashtagScraper(rate_limit_delay=3.0)
  posts = scraper.scrape_hashtag(hashtag="python", limit=50)


MODULE: csv_exporter.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Purpose: Convert posts to CSV format
Dependencies: csv, pathlib, logging
Key Classes:
  - CSVExporter (Main class)

Methods:
  - export(posts, hashtag, filename) → filepath
  - export_multiple_hashtags(hashtag_posts) → filepath
  - get_export_stats(posts) → dict
  - cleanup_old_files(days_old) → int

Usage:
  exporter = CSVExporter(output_dir="./exports")
  filepath = exporter.export(posts, hashtag="python")


MODULE: models.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Purpose: Database models and ORM
Dependencies: sqlalchemy, json, datetime, logging
Key Classes:
  - JobStatus (Enum)
  - User (SQLAlchemy model)
  - ScrapingJob (SQLAlchemy model)
  - Database (Management class)

Methods:
  - create_tables() → None
  - add_user(username, email, password_hash) → User
  - get_user(username) → User or None
  - create_job(...) → ScrapingJob
  - get_job(job_uuid) → ScrapingJob or None
  - update_job_status(...) → ScrapingJob or None
  - get_user_jobs(user_id) → list

Usage:
  db = Database()
  user = db.add_user("john", "john@example.com", "hashed_password")
  job = db.create_job(user.id, job_uuid, ["python"])


MODULE: config.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Purpose: Centralized configuration management
Dependencies: python-dotenv, pathlib, logging
Key Classes:
  - Config (Base configuration)
  - DevelopmentConfig (Development settings)
  - ProductionConfig (Production settings)
  - TestingConfig (Testing settings)

Key Settings:
  - Database: SQLALCHEMY_DATABASE_URI
  - Scraper: SCRAPER_RATE_LIMIT_DELAY, SCRAPER_MAX_POSTS
  - API: API_HOST, API_PORT, API_SECRET_KEY
  - Logging: LOG_LEVEL, LOG_FILE
  - Storage: CSV_EXPORT_DIR, EXPORTS_DIR

Usage:
  from config import config
  print(config.SCRAPER_MAX_POSTS)  # 500
"""

DEPENDENCIES = """
═════════════════════════════════════════════════════════════════
DEPENDENCIES BREAKDOWN
═════════════════════════════════════════════════════════════════

CORE SCRAPING:
  ✅ instagrapi==2.0.0        # Instagram scraper (no auth required)
  ✅ requests==2.31.0         # HTTP library
  ✅ urllib3==2.1.0           # HTTP client

WEB FRAMEWORK & API:
  ⏳ flask==3.0.0             # (Phase 2) Web framework
  ⏳ flask-cors==4.0.0        # (Phase 2) CORS support
  ⏳ flask-sqlalchemy==3.1.1  # (Phase 2) ORM integration

DATABASE:
  ✅ sqlalchemy==2.0.23       # ORM
  ✅ python-dotenv==1.0.0     # Environment variables

AUTHENTICATION:
  ⏳ werkzeug==3.0.1          # (Phase 2) Password hashing
  ⏳ pyjwt==2.8.1             # (Phase 2) JWT tokens
  ⏳ bcrypt==4.1.0            # (Phase 2) Password encryption

DATA PROCESSING:
  ✅ pandas==2.1.3            # Data analysis
  ✅ python-dateutil==2.8.2   # Date utilities

BACKGROUND JOBS:
  ⏳ celery==5.3.4            # (Phase 4) Task queue
  ⏳ redis==5.0.1             # (Phase 4) Message broker

UTILITIES:
  ✅ python-uuid==0.2.0       # UUID generation
  ✅ pydantic==2.5.0          # Data validation

LOGGING & MONITORING:
  ✅ python-json-logger==2.0.7 # JSON logging

TESTING:
  ✅ pytest==7.4.3            # Testing framework
  ✅ pytest-cov==4.1.0        # Coverage reports

DEVELOPMENT:
  ✅ black==23.12.0           # Code formatter
  ✅ flake8==6.1.0            # Linter
  ✅ mypy==1.7.1              # Type checker
"""

WORKFLOW = """
═════════════════════════════════════════════════════════════════
USER WORKFLOW (FULL PIPELINE)
═════════════════════════════════════════════════════════════════

1. USER REGISTRATION/LOGIN
   Website Login Form
   ↓
   API: POST /auth/register or /auth/login
   ↓
   Database: Create User or Verify Credentials
   ↓
   JWT Token Generated
   ↓
   User Authenticated ✅

2. SCRAPING REQUEST
   Website Form (filled with criteria)
   ↓
   Hashtags: #python, #coding, #webdev
   Limit: 150 posts
   Sort: Newest first
   ↓
   API: POST /jobs
   ↓
   Database: Create ScrapingJob (pending)
   ↓
   Background Worker: Receive job

3. SCRAPING EXECUTION
   Background Worker (Celery/RQ)
   ↓
   Initialize: InstagramHashtagScraper
   ↓
   For each hashtag:
     - Apply rate limiting (3s delay)
     - Scrape posts via instagrapi
     - Extract: URL, timestamp, caption, likes, comments
     - Handle errors with exponential backoff
   ↓
   Database: Update job progress (0% → 100%)
   ↓
   All posts collected ✅

4. DATA EXPORT
   CSV Exporter
   ↓
   Sort by timestamp (newest first)
   ↓
   Format: URL | Timestamp | Caption | Likes | Comments | Type
   ↓
   Write to CSV file
   ↓
   Database: Update job (status=completed, csv_filename=...)

5. DOWNLOAD
   Website: Show "Download CSV" button
   ↓
   User clicks button
   ↓
   API: GET /jobs/<id>/download
   ↓
   Serve CSV file with headers
   ↓
   User downloads file ✅

6. CLEANUP
   Scheduled task (cron/APScheduler)
   ↓
   Delete old CSV files (older than 1 day)
   ↓
   Delete old job records (older than 7 days)
"""

NEXT_STEPS = """
═════════════════════════════════════════════════════════════════
NEXT STEPS - BUILD PHASE 2 (BACKEND API)
═════════════════════════════════════════════════════════════════

When you're ready, we'll create:

1. ✨ app.py - Flask application setup
   - Initialize Flask app
   - Configure SQLAlchemy
   - Setup CORS
   - Error handling

2. 🔐 auth.py - User authentication
   - User registration endpoint
   - User login endpoint
   - Password hashing (bcrypt)
   - JWT token generation & validation

3. 🛣️ routes.py - API endpoints
   - POST /api/auth/register
   - POST /api/auth/login
   - POST /api/jobs (create scraping job)
   - GET /api/jobs/<job_id> (check status)
   - GET /api/jobs/<job_id>/download (download CSV)
   - GET /api/jobs (list user's jobs)
   - DELETE /api/jobs/<job_id>

4. 🔄 background_worker.py - Job processing
   - Celery task for scraping
   - Job status updates
   - Error handling & retries
   - CSV generation

5. 📚 API Documentation
   - OpenAPI/Swagger specs
   - Endpoint descriptions
   - Request/response examples

Then Phase 3: Frontend (React form + dashboard)
Then Phase 4: Deployment (Docker + DigitalOcean)
"""

if __name__ == "__main__":
    print(PROJECT_STRUCTURE)
    print("\n")
    print(PHASE_1_MODULES)
    print("\n")
    print(DEPENDENCIES)
    print("\n")
    print(WORKFLOW)
    print("\n")
    print(NEXT_STEPS)
