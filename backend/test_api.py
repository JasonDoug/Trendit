#!/usr/bin/env python3
"""
Test script for Trendit API
Validates Reddit integration and basic functionality
"""

import os
import sys
import asyncio
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.reddit_client import RedditClient
from services.data_collector import DataCollector

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_reddit_connection():
    """Test Reddit API connection"""
    logger.info("Testing Reddit API connection...")
    
    try:
        client = RedditClient()
        
        # Test basic subreddit access
        posts = client.get_subreddit_posts("python", limit=5)
        logger.info(f"Successfully retrieved {len(posts)} posts from r/python")
        
        if posts:
            logger.info(f"Sample post: {posts[0]['title'][:50]}...")
        
        return True
        
    except Exception as e:
        logger.error(f"Reddit connection test failed: {e}")
        return False

async def test_scenarios():
    """Test the specific user scenarios"""
    logger.info("Testing user scenarios...")
    
    try:
        collector = DataCollector()
        
        # Test Scenario 1: Search posts by keyword and date
        logger.info("Testing Scenario 1: Keyword search with date range")
        date_from = datetime.utcnow() - timedelta(days=30)
        date_to = datetime.utcnow()
        
        results = await collector.search_subreddit_posts_by_keyword_and_date(
            subreddit="python",
            keywords=["fastapi", "api"],
            date_from=date_from,
            date_to=date_to,
            limit=3
        )
        logger.info(f"Scenario 1: Found {len(results)} posts about FastAPI in r/python")
        
        # Test Scenario 2: Trending posts across multiple subreddits
        logger.info("Testing Scenario 2: Multi-subreddit trending")
        trending = await collector.get_trending_posts_multiple_subreddits(
            subreddits=["python", "programming"],
            timeframe="day",
            final_limit=5
        )
        logger.info(f"Scenario 2: Found {len(trending)} trending posts")
        
        # Test Scenario 3: Top posts from r/all
        logger.info("Testing Scenario 3: Top posts from r/all")
        top_posts = await collector.get_top_posts_all_reddit(
            sort_type="hot",
            time_filter="day",
            limit=3
        )
        logger.info(f"Scenario 3: Found {len(top_posts)} top posts from r/all")
        
        # Test Scenario 4: Most popular post today
        logger.info("Testing Scenario 4: Most popular post today")
        popular = await collector.get_most_popular_post_today(
            subreddit="python",
            metric="score"
        )
        if popular:
            logger.info(f"Scenario 4: Most popular post today: {popular['title'][:50]}...")
        else:
            logger.info("Scenario 4: No posts found for today")
        
        return True
        
    except Exception as e:
        logger.error(f"Scenario testing failed: {e}")
        return False

async def test_comments_and_users():
    """Test comment and user analysis"""
    logger.info("Testing comment and user analysis...")
    
    try:
        collector = DataCollector()
        
        # Test comment analysis
        logger.info("Testing comment analysis")
        comments = await collector.get_top_comments_by_criteria(
            subreddit="python",
            keywords=["django"],
            limit=5
        )
        logger.info(f"Found {len(comments)} comments about Django")
        
        # Test user analysis
        logger.info("Testing user analysis")
        users = await collector.get_top_users_by_activity(
            subreddits=["python"],
            timeframe_days=7,
            limit=5
        )
        logger.info(f"Found {len(users)} active users in r/python")
        
        return True
        
    except Exception as e:
        logger.error(f"Comment/user testing failed: {e}")
        return False

def check_environment():
    """Check if all required environment variables are set"""
    logger.info("Checking environment configuration...")
    
    required_vars = [
        "REDDIT_CLIENT_ID",
        "REDDIT_CLIENT_SECRET"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {missing_vars}")
        logger.error("Please copy .env.example to .env and fill in your Reddit API credentials")
        return False
    
    logger.info("Environment configuration is valid")
    return True

async def main():
    """Main test function"""
    logger.info("Starting Trendit API tests...")
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    # Test Reddit connection
    if not await test_reddit_connection():
        logger.error("Reddit connection failed. Cannot continue tests.")
        sys.exit(1)
    
    # Test scenarios
    if not await test_scenarios():
        logger.error("Scenario tests failed.")
        sys.exit(1)
    
    # Test comments and users
    if not await test_comments_and_users():
        logger.error("Comment/user tests failed.")
        sys.exit(1)
    
    logger.info("All tests completed successfully!")
    logger.info("Trendit API is ready for use!")

if __name__ == "__main__":
    asyncio.run(main())