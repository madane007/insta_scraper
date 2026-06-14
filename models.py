"""
Database Models
Defines user accounts and scraping job tracking.
"""

from datetime import datetime
from enum import Enum
from typing import Optional, List
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import logging
import json

logger = logging.getLogger(__name__)

Base = declarative_base()


class JobStatus(Enum):
    """Job status enum"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class User(Base):
    """User account model"""
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    is_active = Column(Boolean, default=True)

    # Relationships
    jobs = relationship('ScrapingJob', back_populates='user', cascade='all, delete-orphan')

    def __repr__(self) -> str:
        return f"<User {self.username}>"

    def to_dict(self) -> dict:
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'is_active': self.is_active,
        }


class ScrapingJob(Base):
    """Scraping job model"""
    __tablename__ = 'scraping_jobs'

    id = Column(Integer, primary_key=True)
    job_uuid = Column(String(36), unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)

    # Job configuration
    hashtags = Column(Text, nullable=False)  # JSON string of hashtag list
    locations = Column(Text)                 # JSON string of location list
    accounts = Column(Text)                  # JSON string of account list
    post_limit = Column(Integer, default=50)
    sort_by = Column(String(20), default='newest')  # "newest" or "oldest"

    # Job status
    status = Column(String(20), default='pending', index=True)
    progress = Column(Float, default=0.0)  # 0-100
    error_message = Column(Text)

    # Results
    posts_count = Column(Integer, default=0)
    csv_filepath = Column(Text)
    csv_filename = Column(String(255))

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)

    # Relationships
    user = relationship('User', back_populates='jobs')

    def __repr__(self) -> str:
        return f"<ScrapingJob {self.job_uuid}>"

    def set_hashtags(self, hashtags: list) -> None:
        self.hashtags = json.dumps(hashtags)

    def get_hashtags(self) -> list:
        return json.loads(self.hashtags) if self.hashtags else []

    def set_locations(self, locations: list) -> None:
        self.locations = json.dumps(locations) if locations else None

    def get_locations(self) -> list:
        return json.loads(self.locations) if self.locations else []

    def set_accounts(self, accounts: list) -> None:
        self.accounts = json.dumps(accounts) if accounts else None

    def get_accounts(self) -> list:
        return json.loads(self.accounts) if self.accounts else []

    def to_dict(self) -> dict:
        """Convert job to dictionary"""
        return {
            'job_uuid': self.job_uuid,
            'status': self.status,
            'progress': self.progress,
            'hashtags': self.get_hashtags(),
            'locations': self.get_locations(),
            'accounts': self.get_accounts(),
            'post_limit': self.post_limit,
            'sort_by': self.sort_by,
            'posts_count': self.posts_count,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'csv_filename': self.csv_filename,
        }


class Database:
    """Database management class"""

    def __init__(self, db_url: str = "sqlite:///instagram_scraper.db"):
        self.engine = create_engine(db_url, echo=False)
        self.Session = sessionmaker(bind=self.engine)
        logger.info(f"Database initialized: {db_url}")

    def create_tables(self) -> None:
        """Create all tables"""
        Base.metadata.create_all(self.engine)
        logger.info("Database tables created")

    def get_session(self):
        """Get new database session"""
        return self.Session()

    def add_user(self, username: str, email: str, password_hash: str) -> User:
        session = self.get_session()
        try:
            user = User(username=username, email=email, password_hash=password_hash)
            session.add(user)
            session.commit()
            session.refresh(user)
            return user
        finally:
            session.close()

    def get_user(self, username: str) -> Optional[User]:
        """
        Get user by username.

        FIX: expunge() detaches the object from the session cleanly so
        attributes remain accessible after session.close().
        """
        session = self.get_session()
        try:
            user = session.query(User).filter_by(username=username).first()
            if user:
                session.expunge(user)
            return user
        finally:
            session.close()

    def create_job(
        self,
        user_id: int,
        job_uuid: str,
        hashtags: list,
        post_limit: int = 50,
        locations: list = None,
        accounts: list = None,
        sort_by: str = "newest"
    ) -> ScrapingJob:
        """Create new scraping job."""
        session = self.get_session()
        try:
            job = ScrapingJob(
                job_uuid=job_uuid,
                user_id=user_id,
                post_limit=post_limit,
                sort_by=sort_by
            )
            job.hashtags = json.dumps(hashtags)
            if locations:
                job.locations = json.dumps(locations)
            if accounts:
                job.accounts = json.dumps(accounts)
            session.add(job)
            session.commit()
            session.refresh(job)
            return job
        finally:
            session.close()

    def get_job(self, job_uuid: str) -> Optional[ScrapingJob]:
        """
        Get job by UUID.

        FIX: expunge() so the returned object is usable after session closes.
        """
        session = self.get_session()
        try:
            job = session.query(ScrapingJob).filter_by(job_uuid=job_uuid).first()
            if job:
                session.expunge(job)
            return job
        finally:
            session.close()

    def update_job_status(
        self,
        job_uuid: str,
        status: str,
        progress: float = None,
        error_message: str = None,
        posts_count: int = None,
        csv_filepath: str = None,
        csv_filename: str = None
    ) -> Optional[ScrapingJob]:
        """Update job status and metadata."""
        session = self.get_session()
        try:
            job = session.query(ScrapingJob).filter_by(job_uuid=job_uuid).first()
            if not job:
                return None

            job.status = status
            if progress is not None:
                job.progress = progress
            if error_message is not None:
                job.error_message = error_message
            if posts_count is not None:
                job.posts_count = posts_count
            if csv_filepath is not None:
                job.csv_filepath = csv_filepath
            if csv_filename is not None:
                job.csv_filename = csv_filename

            if status == 'running' and not job.started_at:
                job.started_at = datetime.utcnow()
            elif status == 'completed' and not job.completed_at:
                job.completed_at = datetime.utcnow()

            session.commit()
            session.refresh(job)
            logger.info(f"Job updated: {job_uuid} -> {status}")
            return job
        finally:
            session.close()

    def get_user_jobs(self, user_id: int) -> List[dict]:
        """
        Get all jobs for a user as a list of dicts.

        FIX: Convert to dicts inside the session so we never return
        detached ORM objects — callers just iterate dicts safely.
        """
        session = self.get_session()
        try:
            jobs = session.query(ScrapingJob).filter_by(user_id=user_id).all()
            return [job.to_dict() for job in jobs]
        finally:
            session.close()


# Example usage
if __name__ == "__main__":
    db = Database()
    db.create_tables()

    user = db.add_user(
        username="testuser",
        email="test@example.com",
        password_hash="hashed_password_here"
    )

    import uuid
    job_uuid = str(uuid.uuid4())
    job = db.create_job(
        user_id=user.id,
        job_uuid=job_uuid,
        hashtags=["python", "coding"],
        post_limit=100
    )

    print(f"User: {user.to_dict()}")
    print(f"Job: {job.to_dict()}")