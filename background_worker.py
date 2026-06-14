"""
Background Worker
Processes scraping jobs in background threads (no Redis/Celery needed).
"""

import threading
import logging
import os
from scraper import InstagramHashtagScraper
from csv_exporter import CSVExporter
from models import Database

logger = logging.getLogger(__name__)


def _get_config():
    """
    FIX: Load config based on FLASK_ENV environment variable at call time,
    not at import time. Previously this was hardcoded to DevelopmentConfig()
    at the module level, which meant production deployments silently used
    dev settings.
    """
    from config import DevelopmentConfig, ProductionConfig
    env = os.getenv('FLASK_ENV', 'development')
    return ProductionConfig() if env == 'production' else DevelopmentConfig()


def run_scraping_job(
    db: Database,
    job_uuid: str,
    hashtags: list,
    post_limit: int,
    sort_by: str = "newest"
):
    """
    Core scraping logic — runs in a background thread.
    Updates job status in DB throughout the process.
    """
    logger.info(f"Starting job {job_uuid}")
    config = _get_config()

    try:
        # Mark job as running
        db.update_job_status(job_uuid=job_uuid, status='running', progress=0)

        scraper = InstagramHashtagScraper(
            rate_limit_delay=config.SCRAPER_RATE_LIMIT_DELAY,
            max_retries=config.SCRAPER_MAX_RETRIES
        )
        exporter = CSVExporter(output_dir=config.CSV_EXPORT_DIR)

        all_posts = []
        posts_per_hashtag = max(1, post_limit // len(hashtags))

        for i, hashtag in enumerate(hashtags):
            try:
                logger.info(f"Scraping #{hashtag} ({i+1}/{len(hashtags)})")

                posts = scraper.scrape_hashtag(
                    hashtag=hashtag,
                    limit=posts_per_hashtag,
                    sort_by=sort_by
                )
                all_posts.extend(posts)

                # Update progress (scraping phase = 0–90%)
                progress = round(((i + 1) / len(hashtags)) * 90)
                db.update_job_status(
                    job_uuid=job_uuid,
                    status='running',
                    progress=progress,
                    posts_count=len(all_posts)
                )

            except Exception as e:
                logger.warning(f"Failed to scrape #{hashtag}: {e}")
                continue

        if not all_posts:
            db.update_job_status(
                job_uuid=job_uuid,
                status='failed',
                progress=0,
                error_message='No posts were collected'
            )
            return

        # Export to CSV (use first 3 hashtags in filename)
        combined_hashtag = "_".join(hashtags[:3])
        csv_filepath = exporter.export(all_posts, hashtag=combined_hashtag)
        csv_filename = os.path.basename(csv_filepath)

        # Mark complete
        db.update_job_status(
            job_uuid=job_uuid,
            status='completed',
            progress=100,
            posts_count=len(all_posts),
            csv_filepath=csv_filepath,
            csv_filename=csv_filename
        )

        logger.info(f"Job {job_uuid} completed: {len(all_posts)} posts → {csv_filename}")

    except Exception as e:
        logger.error(f"Job {job_uuid} failed: {e}")
        db.update_job_status(
            job_uuid=job_uuid,
            status='failed',
            error_message=str(e)
        )


def start_job_thread(
    db: Database,
    job_uuid: str,
    hashtags: list,
    post_limit: int,
    sort_by: str = "newest"
):
    """Launch the scraping job in a background thread"""
    thread = threading.Thread(
        target=run_scraping_job,
        args=(db, job_uuid, hashtags, post_limit, sort_by),
        daemon=True
    )
    thread.start()
    logger.info(f"Background thread started for job {job_uuid}")
    return thread