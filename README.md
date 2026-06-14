# Instagram Hashtag Scraper

A full-stack web application for scraping Instagram posts by hashtags, locations, or accounts, with CSV export functionality.

## 📋 Project Overview

**Goal**: Build a user-friendly website where users can specify scraping criteria (hashtags, locations, accounts), and receive a CSV file with post URLs sorted by timestamp.

### Key Features
- ✅ **Hashtag-based scraping** (primary)
- ✅ **Location & account scraping** (extensible)
- ✅ **CSV export** with columns: URL, Timestamp, Caption, Likes, Comments, Post Type
- ✅ **User authentication** (simple account system)
- ✅ **Job tracking** (monitor scraping progress)
- ✅ **Rate limiting** (3-5 second delays, respectful to Instagram)
- ✅ **Error handling & retry logic** (exponential backoff)
- ✅ **Logging** (comprehensive debugging)

### Architecture

```
┌─────────────────────────────────────────┐
│          FRONTEND (React/Vue)           │
│     User Input Form + Job Dashboard     │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│    BACKEND API (Flask/FastAPI)          │
│  • User auth                            │
│  • Job creation & status                │
│  • CSV download                         │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│    BACKGROUND WORKER (Celery/RQ)       │
│  • Scraper logic (instagrapi)           │
│  • Rate limiting & retries              │
│  • CSV export                           │
└──────────────────────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│      DATABASE (SQLite/PostgreSQL)       │
│  • User accounts                        │
│  • Job history & status                 │
└──────────────────────────────────────────┘
```

## 🏗️ Project Phases

### Phase 1: Core Scraper Module ✅ (Current)
- [x] `scraper.py` - Main scraper using instagrapi
- [x] `csv_exporter.py` - CSV generation
- [x] `models.py` - Database models
- [x] `config.py` - Configuration management
- [ ] Unit tests for scraper

### Phase 2: Backend API
- [ ] `app.py` - Flask application setup
- [ ] `auth.py` - User authentication (JWT)
- [ ] `routes.py` - API endpoints
- [ ] `background_worker.py` - Job processing
- [ ] API documentation

### Phase 3: Frontend Website
- [ ] React/Vue form component
- [ ] Job status dashboard
- [ ] CSV download interface
- [ ] User account management

### Phase 4: Deployment
- [ ] Docker & Docker Compose
- [ ] Deployment guide (DigitalOcean/AWS)
- [ ] Production checklist

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- pip or conda

### Installation

1. **Clone/Setup Project**
```bash
cd instagram-scraper
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

3. **Setup Environment**
```bash
cp .env.example .env
# Edit .env with your settings (defaults are fine for development)
```

4. **Create Database**
```bash
python -c "from models import Database; db = Database(); db.create_tables()"
```

### Testing the Scraper (Phase 1)

```python
from scraper import InstagramHashtagScraper
from csv_exporter import CSVExporter

# Initialize scraper
scraper = InstagramHashtagScraper(rate_limit_delay=3.0)

# Scrape hashtag
posts = scraper.scrape_hashtag(
    hashtag="python",
    limit=50,
    sort_by="newest"
)

# Export to CSV
exporter = CSVExporter()
filepath = exporter.export(posts, hashtag="python")
print(f"Exported to: {filepath}")

# Get statistics
stats = exporter.get_export_stats(posts)
print(f"Stats: {stats}")
```

---

## 📚 Module Documentation

### `scraper.py`
Main scraper module with Instagram post collection logic.

**Classes:**
- `PostType` - Enum for post types (Photo, Reel, Carousel, Story)
- `InstagramPost` - Dataclass for post metadata
- `RateLimiter` - Implements rate limiting with optional jitter
- `InstagramHashtagScraper` - Main scraper class

**Key Methods:**
```python
scraper = InstagramHashtagScraper(rate_limit_delay=3.0)
posts = scraper.scrape_hashtag(hashtag="python", limit=50, sort_by="newest")
```

### `csv_exporter.py`
Exports scraped posts to CSV format.

**Classes:**
- `CSVExporter` - Handles CSV generation and export

**Key Methods:**
```python
exporter = CSVExporter(output_dir="./exports")
filepath = exporter.export(posts, hashtag="python")
stats = exporter.get_export_stats(posts)
```

### `models.py`
Database models for user accounts and job tracking.

**Classes:**
- `User` - User account model
- `ScrapingJob` - Job tracking model
- `Database` - Database management

**Key Methods:**
```python
db = Database()
user = db.add_user(username="john", email="john@example.com", password_hash="...")
job = db.create_job(user_id=1, job_uuid="...", hashtags=["python"])
```

### `config.py`
Centralized configuration management.

**Classes:**
- `Config` - Base configuration
- `DevelopmentConfig` - Development settings
- `ProductionConfig` - Production settings
- `TestingConfig` - Testing settings

---

## ⚙️ Rate Limiting Strategy

**Current: Fixed Delay (3 seconds)**
- Simple and reliable
- Respects Instagram's rate limits
- Safe for scraping up to 500 posts

**Future: Adaptive Backoff**
- Detects 429 errors (rate limit exceeded)
- Automatically increases delays
- Recovers when rates normalize

```
Normal: 3s delay between requests
429 Error: Wait 30s, retry
Continued Error: Wait 60s, retry
Escalation: Max wait 300s (5 minutes)
```

---

## 🔐 Instagram ToS Compliance

✅ **Allowed:**
- Collect publicly available data
- Use for research/analysis
- Respect rate limits
- Identify as a bot in user-agent

❌ **Not Allowed:**
- Collect private/personal data
- Aggressive scraping (too many requests)
- Bypass authentication or security
- Resell scraped data

**Current Implementation:**
- Only scrapes public hashtags
- 3-second minimum delays
- Proper error handling & backoff
- No login/private data access

---

## 📊 CSV Export Format

| URL | Timestamp | Caption | Likes Count | Comments Count | Post Type |
|-----|-----------|---------|------------|----------------|-----------|
| https://www.instagram.com/p/ABC123/ | 2024-01-15T10:30:00 | Test caption | 150 | 12 | Photo |
| https://www.instagram.com/p/ABC456/ | 2024-01-14T15:45:00 | Another post | 320 | 25 | Reel |

**Sorted by:** Timestamp (newest first, configurable)

---

## 🛠️ Troubleshooting

### "No posts found"
- Check hashtag spelling and popularity
- Instagram may be rate-limiting - increase delay
- Try different hashtag

### "Connection timeout"
- Network issue or Instagram blocking requests
- Check delay settings in config
- Verify internet connection

### "Authentication error"
- Not applicable for basic (no-login) scraper
- Will be relevant in Phase 2 with account support

### "CSV export failed"
- Check disk space
- Verify `exports/` directory exists and is writable
- Check file permissions

---

## 📝 Logging

Logs are written to:
- **Console:** Real-time output
- **File:** `logs/app.log` (rotated daily)

**Log Levels:**
- `DEBUG` - Detailed development info
- `INFO` - General info (default)
- `WARNING` - Warning messages
- `ERROR` - Error messages

**Change log level:**
```bash
LOG_LEVEL=DEBUG python scraper.py
```

---

## 🔄 Next Steps (Phase 2)

When ready to build the backend API:

1. Create `app.py` with Flask setup
2. Implement authentication (`auth.py`)
3. Create API routes (`routes.py`)
4. Setup background jobs (`background_worker.py`)
5. Write API documentation

```
POST /api/auth/register
POST /api/auth/login

POST /api/jobs
GET /api/jobs/<job_id>
GET /api/jobs/<job_id>/download

GET /api/users/me
```

---

## 📦 Deployment

### Local Development
```bash
FLASK_ENV=development python app.py
```

### Docker Deployment (Phase 4)
```bash
docker-compose up
```

### Cloud Deployment
- **DigitalOcean App Platform:** $5-12/month
- **Heroku:** Free tier or paid dyno
- **AWS:** Pay-as-you-go (usually $5-20/month for small app)

---

## 📄 License

MIT License - Feel free to use, modify, and distribute.

---

## 🤝 Contributing

Issues and improvements welcome! Please:
1. Test locally before submitting changes
2. Follow Python PEP 8 style guidelines
3. Add docstrings to all functions
4. Update README with significant changes

---

## 📞 Support

For issues or questions:
1. Check troubleshooting section
2. Review logs in `logs/app.log`
3. Test with simple hashtag first
4. Verify network connectivity

---

**Status:** Phase 1 (Core Scraper) - ✅ Complete  
**Last Updated:** 2024  
**Version:** 0.1.0
