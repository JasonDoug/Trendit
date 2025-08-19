from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text, ForeignKey, Index, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base
import enum

class JobStatus(enum.Enum):
    PENDING = "pending"
    RUNNING = "running" 
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class SortType(enum.Enum):
    HOT = "hot"
    NEW = "new"
    TOP = "top"
    RISING = "rising"
    CONTROVERSIAL = "controversial"

class TimeFilter(enum.Enum):
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"
    ALL = "all"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)
    
    # Relationships
    collection_jobs = relationship("CollectionJob", back_populates="user")

class CollectionJob(Base):
    __tablename__ = "collection_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Collection Parameters
    subreddits = Column(JSON)  # List of subreddit names
    sort_types = Column(JSON)  # List of sort types
    time_filters = Column(JSON)  # List of time filters
    post_limit = Column(Integer, default=100)
    comment_limit = Column(Integer, default=50)
    max_comment_depth = Column(Integer, default=3)
    
    # Filters
    keywords = Column(JSON)  # Search keywords
    min_score = Column(Integer, default=0)
    min_upvote_ratio = Column(Float, default=0.0)
    date_from = Column(DateTime(timezone=True), nullable=True)
    date_to = Column(DateTime(timezone=True), nullable=True)
    exclude_nsfw = Column(Boolean, default=True)
    anonymize_users = Column(Boolean, default=True)
    
    # Status and Progress
    status = Column(Enum(JobStatus), default=JobStatus.PENDING)
    progress = Column(Integer, default=0)
    total_expected = Column(Integer, default=0)
    collected_posts = Column(Integer, default=0)
    collected_comments = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="collection_jobs")
    posts = relationship("RedditPost", back_populates="collection_job")
    analytics = relationship("Analytics", back_populates="collection_job")

class RedditPost(Base):
    __tablename__ = "reddit_posts"
    
    id = Column(Integer, primary_key=True, index=True)
    collection_job_id = Column(Integer, ForeignKey("collection_jobs.id"))
    
    # Reddit Data
    reddit_id = Column(String, unique=True, index=True)
    title = Column(Text)
    selftext = Column(Text, nullable=True)
    url = Column(String, nullable=True)
    permalink = Column(String)
    
    # Metadata
    subreddit = Column(String, index=True)
    author = Column(String, nullable=True)  # null if anonymized or deleted
    author_id = Column(String, nullable=True)
    
    # Metrics
    score = Column(Integer, index=True)
    upvote_ratio = Column(Float)
    num_comments = Column(Integer)
    awards_received = Column(Integer, default=0)
    
    # Content Classification
    is_nsfw = Column(Boolean, default=False)
    is_spoiler = Column(Boolean, default=False)
    is_stickied = Column(Boolean, default=False)
    post_hint = Column(String, nullable=True)  # image, video, link, etc.
    
    # Timestamps
    created_utc = Column(DateTime(timezone=True))
    collected_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Analytics
    sentiment_score = Column(Float, nullable=True)
    readability_score = Column(Float, nullable=True)
    
    # Relationships
    collection_job = relationship("CollectionJob", back_populates="posts")
    comments = relationship("RedditComment", back_populates="post")

class RedditComment(Base):
    __tablename__ = "reddit_comments"
    
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("reddit_posts.id"))
    
    # Reddit Data
    reddit_id = Column(String, unique=True, index=True)
    body = Column(Text)
    parent_id = Column(String, nullable=True)  # Parent comment ID
    
    # Metadata
    author = Column(String, nullable=True)  # null if anonymized or deleted
    author_id = Column(String, nullable=True)
    depth = Column(Integer, default=0)  # Comment depth in thread
    
    # Metrics
    score = Column(Integer, index=True)
    awards_received = Column(Integer, default=0)
    
    # Flags
    is_submitter = Column(Boolean, default=False)  # Comment by post author
    is_stickied = Column(Boolean, default=False)
    
    # Timestamps
    created_utc = Column(DateTime(timezone=True))
    collected_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Analytics
    sentiment_score = Column(Float, nullable=True)
    
    # Relationships
    post = relationship("RedditPost", back_populates="comments")

class RedditUser(Base):
    __tablename__ = "reddit_users"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Reddit Data
    username = Column(String, unique=True, index=True)
    user_id = Column(String, unique=True, nullable=True)
    
    # Profile Data
    comment_karma = Column(Integer, default=0)
    link_karma = Column(Integer, default=0)
    total_karma = Column(Integer, default=0)
    account_created = Column(DateTime(timezone=True), nullable=True)
    
    # Flags
    is_employee = Column(Boolean, default=False)
    is_mod = Column(Boolean, default=False)
    is_gold = Column(Boolean, default=False)
    has_verified_email = Column(Boolean, default=False)
    
    # Timestamps
    collected_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Analytics(Base):
    __tablename__ = "analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    collection_job_id = Column(Integer, ForeignKey("collection_jobs.id"))
    
    # Summary Statistics
    total_posts = Column(Integer)
    total_comments = Column(Integer)
    total_users = Column(Integer)
    avg_score = Column(Float)
    avg_comments_per_post = Column(Float)
    avg_upvote_ratio = Column(Float)
    
    # Engagement Metrics
    top_posts = Column(JSON)  # Top posts by score
    most_commented = Column(JSON)  # Most commented posts
    active_users = Column(JSON)  # Most active users
    
    # Content Analysis
    common_keywords = Column(JSON)  # Most common keywords
    sentiment_distribution = Column(JSON)  # Sentiment analysis results
    post_type_distribution = Column(JSON)  # Distribution by post type
    
    # Temporal Analysis
    posting_patterns = Column(JSON)  # Posting frequency over time
    engagement_trends = Column(JSON)  # Engagement trends
    
    # Timestamps
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    collection_job = relationship("CollectionJob", back_populates="analytics")

# Database indexes for better performance
Index('idx_reddit_posts_subreddit_score', RedditPost.subreddit, RedditPost.score)
Index('idx_reddit_posts_created_utc', RedditPost.created_utc)
Index('idx_reddit_comments_score', RedditComment.score)
Index('idx_reddit_comments_created_utc', RedditComment.created_utc)
Index('idx_collection_jobs_status_created', CollectionJob.status, CollectionJob.created_at)