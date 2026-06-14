"""
CSV Export Module
Handles conversion of scraped Instagram posts to CSV format.
"""

import csv
import os
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from scraper import InstagramPost

logger = logging.getLogger(__name__)


class CSVExporter:
    """Handles exporting InstagramPost objects to CSV format"""
    
    def __init__(self, output_dir: str = "./exports"):
        """
        Initialize CSV exporter.
        
        Args:
            output_dir: Directory to save CSV files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"CSV exporter initialized with output dir: {self.output_dir}")
    
    def _generate_filename(self, hashtag: Optional[str] = None) -> str:
        """
        Generate unique filename for CSV export.
        
        Args:
            hashtag: Optional hashtag name for filename
            
        Returns:
            Filename string
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if hashtag:
            # Remove # and special characters
            safe_hashtag = hashtag.lstrip('#').replace('#', '_')
            filename = f"instagram_{safe_hashtag}_{timestamp}.csv"
        else:
            filename = f"instagram_export_{timestamp}.csv"
        
        return filename
    
    def export(
        self,
        posts: List[InstagramPost],
        hashtag: Optional[str] = None,
        filename: Optional[str] = None
    ) -> str:
        """
        Export posts to CSV file.
        
        Args:
            posts: List of InstagramPost objects to export
            hashtag: Optional hashtag name (used for filename generation)
            filename: Optional custom filename (if not provided, auto-generate)
            
        Returns:
            Full path to created CSV file
            
        Raises:
            ValueError: If posts list is empty
            IOError: If file writing fails
        """
        if not posts:
            raise ValueError("No posts to export")
        
        # Generate or validate filename
        if not filename:
            filename = self._generate_filename(hashtag)
        
        filepath = self.output_dir / filename
        
        try:
            # Define CSV columns in specific order
            fieldnames = [
                'URL',
                'Timestamp',
                'Caption',
                'Likes Count',
                'Comments Count',
                'Post Type'
            ]
            
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                # Write header
                writer.writeheader()
                
                # Write post data
                for post in posts:
                    writer.writerow({
                        'URL': post.url,
                        'Timestamp': post.timestamp,
                        'Caption': post.caption,
                        'Likes Count': post.likes_count,
                        'Comments Count': post.comments_count,
                        'Post Type': post.post_type
                    })
            
            logger.info(f"Exported {len(posts)} posts to {filepath}")
            return str(filepath)
        
        except IOError as e:
            logger.error(f"Failed to write CSV file: {e}")
            raise
    
    def export_multiple_hashtags(
        self,
        hashtag_posts: dict,
        combined_filename: Optional[str] = None
    ) -> str:
        """
        Export posts from multiple hashtags to a single CSV.
        
        Args:
            hashtag_posts: Dictionary of {hashtag: [posts]}
            combined_filename: Optional filename for combined export
            
        Returns:
            Full path to created CSV file
        """
        # Flatten all posts
        all_posts = []
        for hashtag, posts in hashtag_posts.items():
            all_posts.extend(posts)
        
        if not all_posts:
            raise ValueError("No posts to export from any hashtag")
        
        # Sort by timestamp (newest first)
        all_posts.sort(key=lambda p: p.timestamp, reverse=True)
        
        if not combined_filename:
            combined_filename = self._generate_filename(hashtag="combined")
        
        return self.export(all_posts, filename=combined_filename)
    
    def get_export_stats(self, posts: List[InstagramPost]) -> dict:
        """
        Generate statistics about the export.
        
        Args:
            posts: List of InstagramPost objects
            
        Returns:
            Dictionary with statistics
        """
        if not posts:
            return {}
        
        total_likes = sum(p.likes_count for p in posts)
        total_comments = sum(p.comments_count for p in posts)
        avg_likes = total_likes / len(posts) if posts else 0
        avg_comments = total_comments / len(posts) if posts else 0
        
        # Count post types
        post_types = {}
        for post in posts:
            post_types[post.post_type] = post_types.get(post.post_type, 0) + 1
        
        return {
            'total_posts': len(posts),
            'total_likes': total_likes,
            'total_comments': total_comments,
            'avg_likes': round(avg_likes, 2),
            'avg_comments': round(avg_comments, 2),
            'post_type_breakdown': post_types,
            'earliest_post': posts[-1].timestamp if posts else None,
            'latest_post': posts[0].timestamp if posts else None,
        }
    
    def cleanup_old_files(self, days_old: int = 1) -> int:
        """
        Remove CSV files older than specified days.
        
        Args:
            days_old: Remove files older than this many days
            
        Returns:
            Number of files deleted
        """
        from datetime import timedelta, datetime as dt
        
        cutoff_time = dt.now() - timedelta(days=days_old)
        deleted_count = 0
        
        for filepath in self.output_dir.glob('*.csv'):
            if filepath.stat().st_mtime < cutoff_time.timestamp():
                try:
                    filepath.unlink()
                    logger.info(f"Deleted old file: {filepath}")
                    deleted_count += 1
                except OSError as e:
                    logger.warning(f"Could not delete {filepath}: {e}")
        
        return deleted_count


# Example usage
if __name__ == "__main__":
    from scraper import InstagramPost
    
    # Create sample posts for testing
    sample_posts = [
        InstagramPost(
            url="https://www.instagram.com/p/ABC123/",
            timestamp="2024-01-15T10:30:00",
            caption="This is a test post",
            likes_count=150,
            comments_count=12,
            post_type="Photo"
        ),
        InstagramPost(
            url="https://www.instagram.com/p/ABC456/",
            timestamp="2024-01-14T15:45:00",
            caption="Another test post with a longer caption",
            likes_count=320,
            comments_count=25,
            post_type="Reel"
        ),
    ]
    
    exporter = CSVExporter()
    filepath = exporter.export(sample_posts, hashtag="test")
    print(f"Exported to: {filepath}")
    
    stats = exporter.get_export_stats(sample_posts)
    print(f"Export stats: {stats}")
