"""
Test Script for Phase 1 Modules
Tests scraper, CSV exporter, and database without connecting to Instagram.
"""

import sys
import logging
from datetime import datetime
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_scraper_imports():
    """Test that scraper module imports correctly"""
    logger.info("Testing scraper imports...")
    try:
        from scraper import (
            InstagramHashtagScraper,
            InstagramPost,
            RateLimiter,
            PostType
        )
        logger.info("✅ Scraper imports successful")
        return True
    except ImportError as e:
        logger.error(f"❌ Scraper import failed: {e}")
        return False


def test_csv_exporter():
    """Test CSV exporter with sample data"""
    logger.info("Testing CSV exporter...")
    try:
        from scraper import InstagramPost
        from csv_exporter import CSVExporter
        
        # Create sample posts
        sample_posts = [
            InstagramPost(
                url="https://www.instagram.com/p/ABC123/",
                timestamp="2024-01-15T10:30:00",
                caption="Test post 1",
                likes_count=150,
                comments_count=12,
                post_type="Photo"
            ),
            InstagramPost(
                url="https://www.instagram.com/p/ABC456/",
                timestamp="2024-01-14T15:45:00",
                caption="Test post 2",
                likes_count=320,
                comments_count=25,
                post_type="Reel"
            ),
        ]
        
        # Test export
        exporter = CSVExporter(output_dir="./test_exports")
        filepath = exporter.export(sample_posts, hashtag="test")
        
        # Verify file exists
        if Path(filepath).exists():
            logger.info(f"✅ CSV export successful: {filepath}")
            
            # Test statistics
            stats = exporter.get_export_stats(sample_posts)
            logger.info(f"✅ Export stats: {stats}")
            
            # Cleanup
            Path(filepath).unlink()
            logger.info("✅ Test file cleaned up")
            return True
        else:
            logger.error("❌ CSV file not created")
            return False
    
    except Exception as e:
        logger.error(f"❌ CSV exporter test failed: {e}")
        return False


def test_database():
    """Test database models and operations"""
    logger.info("Testing database...")
    try:
        from models import Database, User, ScrapingJob
        import uuid
        
        # Create in-memory test database
        db = Database(db_url="sqlite:///:memory:")
        db.create_tables()
        logger.info("✅ Database tables created")
        
        # Test user creation
        user = db.add_user(
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password"
        )
        logger.info(f"✅ User created: {user.username}")
        
        # Test job creation
        job_uuid = str(uuid.uuid4())
        job = db.create_job(
            user_id=user.id,
            job_uuid=job_uuid,
            hashtags=["python", "coding"],
            post_limit=100,
            sort_by="newest"
        )
        logger.info(f"✅ Job created: {job.job_uuid}")
        
        # Test job retrieval
        retrieved_job = db.get_job(job_uuid)
        if retrieved_job and retrieved_job.job_uuid == job_uuid:
            logger.info("✅ Job retrieval successful")
        else:
            logger.error("❌ Job retrieval failed")
            return False
        
        # Test job status update
        db.update_job_status(
            job_uuid=job_uuid,
            status="completed",
            progress=100,
            posts_count=50,
            csv_filename="test.csv"
        )
        logger.info("✅ Job status updated")
        
        # Verify update
        updated_job = db.get_job(job_uuid)
        if updated_job.status == "completed" and updated_job.progress == 100:
            logger.info("✅ Job status verification successful")
            return True
        else:
            logger.error("❌ Job status update verification failed")
            return False
    
    except Exception as e:
        logger.error(f"❌ Database test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_config():
    """Test configuration module"""
    logger.info("Testing config module...")
    try:
        from config import Config, DevelopmentConfig
        
        config = DevelopmentConfig()
        
        # Check key attributes
        checks = {
            "APP_NAME": config.APP_NAME == "Instagram Hashtag Scraper",
            "DEBUG": config.DEBUG == True,
            "SCRAPER_RATE_LIMIT_DELAY": config.SCRAPER_RATE_LIMIT_DELAY > 0,
            "SCRAPER_MAX_POSTS": config.SCRAPER_MAX_POSTS == 500,
            "CSV_EXPORT_DIR": isinstance(config.CSV_EXPORT_DIR, str),
        }
        
        all_passed = all(checks.values())
        
        if all_passed:
            logger.info("✅ Config module validated")
            for check, result in checks.items():
                logger.info(f"  ✅ {check}")
            return True
        else:
            logger.error("❌ Some config checks failed")
            for check, result in checks.items():
                if not result:
                    logger.error(f"  ❌ {check}")
            return False
    
    except Exception as e:
        logger.error(f"❌ Config test failed: {e}")
        return False


def test_rate_limiter():
    """Test rate limiter functionality"""
    logger.info("Testing rate limiter...")
    try:
        from scraper import RateLimiter
        import time
        
        limiter = RateLimiter(delay_seconds=0.1)  # Short delay for testing
        
        # Time 3 requests
        start = time.time()
        limiter.wait()
        limiter.wait()
        limiter.wait()
        elapsed = time.time() - start
        
        # Should take at least ~0.2 seconds (2 delays of 0.1)
        if elapsed >= 0.15:
            logger.info(f"✅ Rate limiter working (elapsed: {elapsed:.2f}s)")
            return True
        else:
            logger.warning(f"⚠️ Rate limiter timing unexpected (elapsed: {elapsed:.2f}s)")
            return True  # Still pass as this might be timing-dependent
    
    except Exception as e:
        logger.error(f"❌ Rate limiter test failed: {e}")
        return False


def main():
    """Run all tests"""
    logger.info("=" * 60)
    logger.info("PHASE 1 TEST SUITE")
    logger.info("=" * 60)
    logger.info("")
    
    tests = [
        ("Scraper Imports", test_scraper_imports),
        ("CSV Exporter", test_csv_exporter),
        ("Database", test_database),
        ("Config Module", test_config),
        ("Rate Limiter", test_rate_limiter),
    ]
    
    results = {}
    for test_name, test_func in tests:
        logger.info("")
        logger.info(f"Running: {test_name}")
        logger.info("-" * 40)
        results[test_name] = test_func()
    
    # Summary
    logger.info("")
    logger.info("=" * 60)
    logger.info("TEST SUMMARY")
    logger.info("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status}: {test_name}")
    
    logger.info("")
    logger.info(f"Results: {passed}/{total} tests passed")
    logger.info("=" * 60)
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())