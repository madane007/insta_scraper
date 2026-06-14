"""
Instagram Hashtag Scraper Module
Scrapes public Instagram posts by hashtag without authentication.
"""

import time
import logging
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
import random

from instagrapi import Client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# instagrapi media_type integer constants
# (MediaType enum import was removed — use raw ints instead for compatibility)
MEDIA_TYPE_PHOTO = 1
MEDIA_TYPE_VIDEO = 2
MEDIA_TYPE_CAROUSEL = 8


class PostType(Enum):
    """Enum for Instagram post types"""
    PHOTO = "Photo"
    VIDEO = "Reel"
    CAROUSEL = "Carousel"
    STORY = "Story"


@dataclass
class InstagramPost:
    """Data class representing an Instagram post"""
    url: str
    timestamp: str  # ISO format datetime
    caption: str
    likes_count: int
    comments_count: int
    post_type: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for CSV export"""
        return asdict(self)


class RateLimiter:
    """Handles rate limiting with fixed delays between requests"""

    def __init__(self, delay_seconds: float = 3.0, jitter: bool = True):
        """
        Initialize rate limiter.

        Args:
            delay_seconds: Seconds to wait between requests
            jitter: Add random variation (±20%) to delay
        """
        self.delay_seconds = delay_seconds
        self.jitter = jitter
        self.last_request_time = 0

    def wait(self) -> None:
        """Apply rate limiting delay"""
        elapsed = time.time() - self.last_request_time

        delay = self.delay_seconds
        if self.jitter:
            # Add ±20% random variation
            jitter_amount = delay * 0.2
            delay += random.uniform(-jitter_amount, jitter_amount)

        wait_time = max(0, delay - elapsed)
        if wait_time > 0:
            logger.debug(f"Rate limiting: waiting {wait_time:.2f}s")
            time.sleep(wait_time)

        self.last_request_time = time.time()


class InstagramHashtagScraper:
    """Main scraper class for collecting Instagram posts by hashtag"""

    def __init__(
        self,
        rate_limit_delay: float = 3.0,
        max_retries: int = 3,
        timeout: int = 30
    ):
        """
        Initialize scraper.

        Args:
            rate_limit_delay: Seconds between requests
            max_retries: Maximum retry attempts on failure
            timeout: Request timeout in seconds
        """
        self.client = Client()
        self.rate_limiter = RateLimiter(delay_seconds=rate_limit_delay)
        self.max_retries = max_retries
        self.timeout = timeout
        self.posts: List[InstagramPost] = []

    def _get_post_type(self, media: Any) -> str:
        """
        Determine post type from media object.

        Uses raw integer comparisons instead of MediaType enum
        to avoid instagrapi version compatibility issues.

        Args:
            media: Instagram media object from instagrapi

        Returns:
            Post type string
        """
        try:
            if hasattr(media, 'media_type'):
                media_type = media.media_type
                if media_type == MEDIA_TYPE_CAROUSEL:
                    return PostType.CAROUSEL.value
                elif media_type == MEDIA_TYPE_VIDEO:
                    return PostType.VIDEO.value
                elif media_type == MEDIA_TYPE_PHOTO:
                    return PostType.PHOTO.value
            return "Unknown"
        except Exception as e:
            logger.warning(f"Could not determine post type: {e}")
            return "Unknown"

    def _format_timestamp(self, timestamp: datetime) -> str:
        """
        Format timestamp to ISO format string.

        Args:
            timestamp: datetime object

        Returns:
            ISO format string
        """
        if isinstance(timestamp, datetime):
            return timestamp.isoformat()
        return str(timestamp)

    def _extract_post_data(self, media: Any) -> Optional[InstagramPost]:
        """
        Extract relevant data from Instagram media object.

        Args:
            media: Instagram media object from instagrapi

        Returns:
            InstagramPost object or None if extraction fails
        """
        try:
            post_url = f"https://www.instagram.com/p/{media.code}/"
            timestamp = self._format_timestamp(media.taken_at)
            caption = media.caption or ""
            likes_count = media.like_count or 0
            comments_count = media.comments_count or 0
            post_type = self._get_post_type(media)

            return InstagramPost(
                url=post_url,
                timestamp=timestamp,
                caption=caption,
                likes_count=likes_count,
                comments_count=comments_count,
                post_type=post_type
            )
        except Exception as e:
            logger.error(f"Error extracting post data: {e}")
            return None

    def scrape_hashtag(
        self,
        hashtag: str,
        limit: int = 50,
        sort_by: str = "newest"
    ) -> List[InstagramPost]:
        """
        Scrape posts from a specific hashtag.

        Args:
            hashtag: Hashtag to scrape (with or without #)
            limit: Maximum number of posts to retrieve
            sort_by: Sort order - "newest" or "oldest"

        Returns:
            List of InstagramPost objects

        Raises:
            ValueError: If hashtag is invalid or limit exceeds maximum
            Exception: If scraping fails after retries
        """
        if limit > 500:
            raise ValueError("Post limit cannot exceed 500")

        # Clean hashtag
        hashtag = hashtag.lstrip('#').strip()
        if not hashtag:
            raise ValueError("Invalid hashtag provided")

        logger.info(f"Starting scrape for #{hashtag}, limit: {limit}")
        self.posts = []
        retry_count = 0

        while len(self.posts) < limit and retry_count < self.max_retries:
            try:
                # Rate limit between batch API calls (not between individual posts)
                self.rate_limiter.wait()

                logger.info(f"Fetching posts for #{hashtag}...")

                medias = self.client.hashtag_medias_recent(
                    hashtag,
                    amount=limit - len(self.posts)
                )

                if not medias:
                    logger.info(f"No more posts found for #{hashtag}")
                    break  # FIX: break instead of looping forever on empty result

                for media in medias:
                    if len(self.posts) >= limit:
                        break
                    post = self._extract_post_data(media)
                    if post:
                        self.posts.append(post)
                        logger.debug(f"Extracted post: {post.url}")
                    # NOTE: No per-post rate limiting here — only limit between
                    # batch API calls above to avoid 50x slowdown

                logger.info(f"Successfully scraped {len(self.posts)} posts")

                # FIX: Break out of while loop after a successful fetch.
                # instagrapi fetches up to `amount` posts in one call, so
                # looping again would just re-fetch the same posts.
                break

            except Exception as e:
                retry_count += 1
                wait_time = min(60, 10 * retry_count)  # Exponential backoff
                logger.warning(
                    f"Scraping failed (attempt {retry_count}/{self.max_retries}): {e}. "
                    f"Waiting {wait_time}s before retry..."
                )

                if retry_count >= self.max_retries:
                    logger.error(f"Failed to scrape #{hashtag} after {self.max_retries} attempts")
                    raise

                time.sleep(wait_time)

        self._sort_posts(sort_by)
        logger.info(f"Scraping complete: {len(self.posts)} posts collected")
        return self.posts

    def _sort_posts(self, sort_by: str = "newest") -> None:
        """
        Sort posts by timestamp.

        Args:
            sort_by: "newest" or "oldest"
        """
        reverse = (sort_by.lower() == "newest")
        self.posts.sort(key=lambda p: p.timestamp, reverse=reverse)
        logger.info(f"Posts sorted by {sort_by}")

    def get_posts(self) -> List[InstagramPost]:
        """Get current list of scraped posts"""
        return self.posts

    def clear(self) -> None:
        """Clear scraped posts"""
        self.posts = []
        logger.info("Cleared scraped posts")


# Example usage
if __name__ == "__main__":
    scraper = InstagramHashtagScraper(rate_limit_delay=3.0)

    try:
        posts = scraper.scrape_hashtag(hashtag="python", limit=10, sort_by="newest")

        for post in posts:
            print(f"\n{post.url}")
            print(f"  Posted: {post.timestamp}")
            print(f"  Likes: {post.likes_count} | Comments: {post.comments_count}")
            print(f"  Type: {post.post_type}")
            print(f"  Caption: {post.caption[:100]}...")

    except Exception as e:
        logger.error(f"Scraping error: {e}")