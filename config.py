"""
Configuration Module
Centralized configuration for the scraper application.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Project directories
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / 'data'
LOGS_DIR = BASE_DIR / 'logs'
EXPORTS_DIR = BASE_DIR / 'exports'

# Create directories if they don't exist
for directory in [DATA_DIR, LOGS_DIR, EXPORTS_DIR]:
    directory.mkdir(exist_ok=True)


class Config:
    """Base configuration"""
    
    # App settings
    APP_NAME = "Instagram Hashtag Scraper"
    VERSION = "0.1.0"
    DEBUG = False
    TESTING = False
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        f'sqlite:///{DATA_DIR}/instagram_scraper.db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Scraper settings
    SCRAPER_RATE_LIMIT_DELAY = float(os.getenv('SCRAPER_RATE_LIMIT_DELAY', '3.0'))
    SCRAPER_MAX_RETRIES = int(os.getenv('SCRAPER_MAX_RETRIES', '3'))
    SCRAPER_TIMEOUT = int(os.getenv('SCRAPER_TIMEOUT', '30'))
    SCRAPER_MAX_POSTS = int(os.getenv('SCRAPER_MAX_POSTS', '500'))
    
    # Job settings
    JOB_TIMEOUT = int(os.getenv('JOB_TIMEOUT', '3600'))  # 1 hour
    JOB_CLEANUP_DAYS = int(os.getenv('JOB_CLEANUP_DAYS', '7'))
    CSV_CLEANUP_DAYS = int(os.getenv('CSV_CLEANUP_DAYS', '1'))
    
    # File storage
    CSV_EXPORT_DIR = str(EXPORTS_DIR)
    MAX_CSV_SIZE_MB = 100
    
    # API settings
    API_HOST = os.getenv('API_HOST', '0.0.0.0')
    API_PORT = int(os.getenv('API_PORT', '5000'))
    API_SECRET_KEY = os.getenv('API_SECRET_KEY', 'dev-secret-key-change-in-production')
    API_CORS_ORIGINS = os.getenv('API_CORS_ORIGINS', '*').split(',')
    
    # JWT settings
    JWT_ALGORITHM = 'HS256'
    JWT_EXPIRATION_HOURS = int(os.getenv('JWT_EXPIRATION_HOURS', '24'))
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = LOGS_DIR / 'app.log'
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Instagram settings
    INSTAGRAM_USER_AGENT = (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
        '(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    )


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_ECHO = True
    LOG_LEVEL = 'DEBUG'


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    API_SECRET_KEY = os.getenv('API_SECRET_KEY', 'dev-secret-key-change-in-production')

    
class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    LOG_LEVEL = 'DEBUG'


# Select configuration based on environment
ENV = os.getenv('FLASK_ENV', 'development')

if ENV == 'production':
    config = ProductionConfig()
elif ENV == 'testing':
    config = TestingConfig()
else:
    config = DevelopmentConfig()


# Logging configuration
import logging
import logging.handlers

def setup_logging():
    """Configure application logging"""
    logger = logging.getLogger()
    logger.setLevel(config.LOG_LEVEL)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(config.LOG_LEVEL)
    console_formatter = logging.Formatter(config.LOG_FORMAT)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler
    file_handler = logging.handlers.RotatingFileHandler(
        config.LOG_FILE,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(config.LOG_LEVEL)
    file_formatter = logging.Formatter(config.LOG_FORMAT)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    return logger


# Example .env file content
ENV_EXAMPLE = """
# Environment (development, production, testing)
FLASK_ENV=development

# Database
DATABASE_URL=sqlite:///data/instagram_scraper.db

# Scraper settings
SCRAPER_RATE_LIMIT_DELAY=3.0
SCRAPER_MAX_RETRIES=3
SCRAPER_TIMEOUT=30
SCRAPER_MAX_POSTS=500

# Job settings
JOB_TIMEOUT=3600
JOB_CLEANUP_DAYS=7
CSV_CLEANUP_DAYS=1

# API settings
API_HOST=0.0.0.0
API_PORT=5000
API_SECRET_KEY=your-secret-key-here-change-in-production
API_CORS_ORIGINS=*

# JWT settings
JWT_EXPIRATION_HOURS=24

# Logging
LOG_LEVEL=INFO
"""
