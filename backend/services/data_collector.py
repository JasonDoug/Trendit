import asyncio
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import logging
from sqlalchemy.orm import Session
from .reddit_client import RedditClient
from .analytics import AnalyticsService
from ..models.models import CollectionJob, RedditPost, RedditComment, RedditUser, JobStatus
from ..models.database import get_db

logger = logging.getLogger(__name__)

class DataCollector:
    """
    Advanced Reddit data collection service with comprehensive search and filtering
    """
    
    def __init__(self):
        self.reddit_client = RedditClient()
        self.analytics = AnalyticsService()
    
    # SCENARIO 1: Search posts in specific subreddit with date range and keywords
    async def search_subreddit_posts_by_keyword_and_date(
        self,
        subreddit: str,
        keywords: List[str],
        date_from: datetime,
        date_to: datetime,
        limit: int = 10,
        sort_by: str = "score"  # score, comments, date
    ) -> List[Dict[str, Any]]:
        """
        Scenario 1: Get most popular posts about 'poetry' in r/python from date X to Y
        
        Args:
            subreddit: Subreddit name (e.g., 'python')
            keywords: List of keywords to search for (e.g., ['poetry'])
            date_from: Start date
            date_to: End date
            limit: Number of results (e.g., 10)
            sort_by: How to rank results (score, comments, date)
        """
        try:
            # Search for posts containing keywords
            search_query = " OR ".join(keywords)
            
            # Get posts from the time period (PRAW doesn't filter by date directly)
            all_posts = self.reddit_client.search_posts(
                query=search_query,
                subreddit_name=subreddit,
                sort="top",
                time_filter="all",
                limit=500  # Get more to filter by date
            )
            
            # Filter by date range and keywords
            filtered_posts = []
            for post in all_posts:
                post_date = post['created_utc']
                
                # Check date range
                if date_from <= post_date <= date_to:
                    # Check if any keyword appears in title or content
                    title_text = post['title'].lower()
                    content_text = (post.get('selftext', '') or '').lower()
                    combined_text = f"{title_text} {content_text}"
                    
                    if any(keyword.lower() in combined_text for keyword in keywords):
                        filtered_posts.append(post)
            
            # Sort by specified criteria
            if sort_by == "score":
                filtered_posts.sort(key=lambda x: x['score'], reverse=True)
            elif sort_by == "comments":
                filtered_posts.sort(key=lambda x: x['num_comments'], reverse=True)
            elif sort_by == "date":
                filtered_posts.sort(key=lambda x: x['created_utc'], reverse=True)
            
            result = filtered_posts[:limit]
            logger.info(f"Found {len(result)} posts about {keywords} in r/{subreddit} from {date_from} to {date_to}")
            return result
            
        except Exception as e:
            logger.error(f"Error searching posts: {e}")
            raise
    
    # SCENARIO 2: Trending posts across multiple subreddits for today
    async def get_trending_posts_multiple_subreddits(
        self,
        subreddits: List[str],
        timeframe: str = "day",  # hour, day, week
        limit_per_subreddit: int = 20,
        final_limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Scenario 2: Trending posts in r/claudecode, r/vibecoding, r/aiagent for today
        
        Args:
            subreddits: List of subreddit names
            timeframe: Time filter (hour, day, week)
            limit_per_subreddit: Posts to get from each subreddit
            final_limit: Final number of trending posts to return
        """
        try:
            all_trending_posts = []
            
            # Get hot/rising posts from each subreddit
            for subreddit in subreddits:
                try:
                    # Get hot posts (trending now)
                    hot_posts = self.reddit_client.get_subreddit_posts(
                        subreddit_name=subreddit,
                        sort_type="hot",
                        limit=limit_per_subreddit // 2
                    )
                    
                    # Get rising posts (gaining momentum)
                    rising_posts = self.reddit_client.get_subreddit_posts(
                        subreddit_name=subreddit,
                        sort_type="rising",
                        limit=limit_per_subreddit // 2
                    )
                    
                    # Combine and add trending score
                    subreddit_posts = hot_posts + rising_posts
                    for post in subreddit_posts:
                        # Calculate trending score (combination of score, comments, and recency)
                        hours_old = (datetime.utcnow() - post['created_utc']).total_seconds() / 3600
                        trending_score = (post['score'] + post['num_comments'] * 2) / max(hours_old, 1)
                        post['trending_score'] = trending_score
                        post['source_subreddit'] = subreddit
                    
                    all_trending_posts.extend(subreddit_posts)
                    
                except Exception as e:
                    logger.warning(f"Error getting posts from r/{subreddit}: {e}")
                    continue
            
            # Remove duplicates and sort by trending score
            seen_ids = set()
            unique_posts = []
            for post in all_trending_posts:
                if post['reddit_id'] not in seen_ids:
                    seen_ids.add(post['reddit_id'])
                    unique_posts.append(post)
            
            # Sort by trending score and return top results
            unique_posts.sort(key=lambda x: x['trending_score'], reverse=True)
            result = unique_posts[:final_limit]
            
            logger.info(f"Found {len(result)} trending posts across {len(subreddits)} subreddits")
            return result
            
        except Exception as e:
            logger.error(f"Error getting trending posts: {e}")
            raise
    
    # SCENARIO 3: Top hot posts in r/all for this week
    async def get_top_posts_all_reddit(
        self,
        sort_type: str = "hot",
        time_filter: str = "week",
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Scenario 3: Top 10 hot posts in r/all for this week
        
        Args:
            sort_type: hot, top, new, rising, controversial
            time_filter: hour, day, week, month, year, all
            limit: Number of posts to return
        """
        try:
            # Get posts from r/all
            posts = self.reddit_client.get_subreddit_posts(
                subreddit_name="all",
                sort_type=sort_type,
                time_filter=time_filter,
                limit=limit
            )
            
            logger.info(f"Retrieved top {len(posts)} {sort_type} posts from r/all for {time_filter}")
            return posts
            
        except Exception as e:
            logger.error(f"Error getting top posts from r/all: {e}")
            raise
    
    # SCENARIO 4: Most popular post in specific subreddit today
    async def get_most_popular_post_today(
        self,
        subreddit: str,
        metric: str = "score"  # score, comments, upvote_ratio
    ) -> Optional[Dict[str, Any]]:
        """
        Scenario 4: Most popular post in r/openai today
        
        Args:
            subreddit: Subreddit name
            metric: What defines "most popular" (score, comments, upvote_ratio)
        """
        try:
            # Get today's posts
            today = datetime.utcnow().date()
            yesterday = today - timedelta(days=1)
            
            # Get recent posts and filter for today
            posts = self.reddit_client.get_subreddit_posts(
                subreddit_name=subreddit,
                sort_type="new",
                limit=100
            )
            
            # Filter posts from today only
            today_posts = []
            for post in posts:
                post_date = post['created_utc'].date()
                if post_date == today:
                    today_posts.append(post)
            
            if not today_posts:
                logger.info(f"No posts found in r/{subreddit} for today")
                return None
            
            # Find most popular by specified metric
            if metric == "score":
                most_popular = max(today_posts, key=lambda x: x['score'])
            elif metric == "comments":
                most_popular = max(today_posts, key=lambda x: x['num_comments'])
            elif metric == "upvote_ratio":
                most_popular = max(today_posts, key=lambda x: x['upvote_ratio'])
            else:
                raise ValueError(f"Invalid metric: {metric}")
            
            logger.info(f"Found most popular post in r/{subreddit} today by {metric}")
            return most_popular
            
        except Exception as e:
            logger.error(f"Error finding most popular post in r/{subreddit}: {e}")
            raise
    
    # COMMENT SCENARIOS
    async def get_top_comments_by_criteria(
        self,
        subreddit: str = None,
        post_id: str = None,
        date_from: datetime = None,
        date_to: datetime = None,
        keywords: List[str] = None,
        limit: int = 10,
        sort_by: str = "score"
    ) -> List[Dict[str, Any]]:
        """
        Get top comments based on various criteria
        
        Args:
            subreddit: Specific subreddit to search
            post_id: Specific post to get comments from
            date_from: Start date filter
            date_to: End date filter
            keywords: Keywords to search for in comments
            limit: Number of comments to return
            sort_by: score, date, length
        """
        try:
            all_comments = []
            
            if post_id:
                # Get comments from specific post
                comments = self.reddit_client.get_post_comments(
                    submission_id=post_id,
                    max_comments=200,
                    max_depth=5
                )
                all_comments.extend(comments)
                
            elif subreddit:
                # Get comments from recent posts in subreddit
                posts = self.reddit_client.get_subreddit_posts(
                    subreddit_name=subreddit,
                    sort_type="hot",
                    limit=20
                )
                
                for post in posts:
                    comments = self.reddit_client.get_post_comments(
                        submission_id=post['reddit_id'],
                        max_comments=50,
                        max_depth=3
                    )
                    # Add post context to comments
                    for comment in comments:
                        comment['post_title'] = post['title']
                        comment['post_subreddit'] = post['subreddit']
                    all_comments.extend(comments)
            
            # Apply filters
            filtered_comments = all_comments
            
            # Date filter
            if date_from and date_to:
                filtered_comments = [
                    c for c in filtered_comments 
                    if date_from <= c['created_utc'] <= date_to
                ]
            
            # Keyword filter
            if keywords:
                keyword_filtered = []
                for comment in filtered_comments:
                    comment_text = comment['body'].lower()
                    if any(keyword.lower() in comment_text for keyword in keywords):
                        keyword_filtered.append(comment)
                filtered_comments = keyword_filtered
            
            # Sort comments
            if sort_by == "score":
                filtered_comments.sort(key=lambda x: x['score'], reverse=True)
            elif sort_by == "date":
                filtered_comments.sort(key=lambda x: x['created_utc'], reverse=True)
            elif sort_by == "length":
                filtered_comments.sort(key=lambda x: len(x['body']), reverse=True)
            
            result = filtered_comments[:limit]
            logger.info(f"Found {len(result)} comments matching criteria")
            return result
            
        except Exception as e:
            logger.error(f"Error getting comments: {e}")
            raise
    
    # USER SCENARIOS
    async def get_top_users_by_activity(
        self,
        subreddits: List[str] = None,
        timeframe_days: int = 7,
        limit: int = 10,
        metric: str = "total_score"  # total_score, post_count, comment_count
    ) -> List[Dict[str, Any]]:
        """
        Get most active/popular users based on various metrics
        
        Args:
            subreddits: List of subreddits to analyze (None for all)
            timeframe_days: Days to look back
            limit: Number of users to return
            metric: How to rank users
        """
        try:
            user_stats = {}
            cutoff_date = datetime.utcnow() - timedelta(days=timeframe_days)
            
            # If specific subreddits provided, analyze those
            if subreddits:
                for subreddit in subreddits:
                    posts = self.reddit_client.get_subreddit_posts(
                        subreddit_name=subreddit,
                        sort_type="new",
                        limit=100
                    )
                    
                    for post in posts:
                        if post['created_utc'] >= cutoff_date and post['author']:
                            username = post['author']
                            if username not in user_stats:
                                user_stats[username] = {
                                    'username': username,
                                    'post_count': 0,
                                    'comment_count': 0,
                                    'total_score': 0,
                                    'subreddits': set()
                                }
                            
                            user_stats[username]['post_count'] += 1
                            user_stats[username]['total_score'] += post['score']
                            user_stats[username]['subreddits'].add(post['subreddit'])
                            
                            # Get some comments from this post
                            comments = self.reddit_client.get_post_comments(
                                submission_id=post['reddit_id'],
                                max_comments=20,
                                max_depth=2
                            )
                            
                            for comment in comments:
                                if comment['author'] and comment['created_utc'] >= cutoff_date:
                                    comment_author = comment['author']
                                    if comment_author not in user_stats:
                                        user_stats[comment_author] = {
                                            'username': comment_author,
                                            'post_count': 0,
                                            'comment_count': 0,
                                            'total_score': 0,
                                            'subreddits': set()
                                        }
                                    
                                    user_stats[comment_author]['comment_count'] += 1
                                    user_stats[comment_author]['total_score'] += comment['score']
            
            # Convert to list and sort by metric
            user_list = []
            for username, stats in user_stats.items():
                stats['subreddits'] = list(stats['subreddits'])  # Convert set to list
                user_list.append(stats)
            
            # Sort by specified metric
            if metric == "total_score":
                user_list.sort(key=lambda x: x['total_score'], reverse=True)
            elif metric == "post_count":
                user_list.sort(key=lambda x: x['post_count'], reverse=True)
            elif metric == "comment_count":
                user_list.sort(key=lambda x: x['comment_count'], reverse=True)
            
            result = user_list[:limit]
            logger.info(f"Found top {len(result)} users by {metric}")
            return result
            
        except Exception as e:
            logger.error(f"Error getting top users: {e}")
            raise
    
    # COMPREHENSIVE COLLECTION JOB
    async def start_collection_job(
        self,
        job_config: Dict[str, Any],
        db: Session
    ) -> str:
        """
        Start a comprehensive data collection job
        
        Args:
            job_config: Configuration dictionary with all collection parameters
            db: Database session
        
        Returns:
            Job ID for tracking
        """
        try:
            # Create collection job record
            job = CollectionJob(
                job_id=f"job_{int(datetime.utcnow().timestamp())}",
                subreddits=job_config.get('subreddits', []),
                sort_types=job_config.get('sort_types', ['hot']),
                time_filters=job_config.get('time_filters', ['week']),
                post_limit=job_config.get('post_limit', 100),
                comment_limit=job_config.get('comment_limit', 50),
                max_comment_depth=job_config.get('max_comment_depth', 3),
                keywords=job_config.get('keywords', []),
                min_score=job_config.get('min_score', 0),
                min_upvote_ratio=job_config.get('min_upvote_ratio', 0.0),
                date_from=job_config.get('date_from'),
                date_to=job_config.get('date_to'),
                exclude_nsfw=job_config.get('exclude_nsfw', True),
                anonymize_users=job_config.get('anonymize_users', True),
                status=JobStatus.PENDING
            )
            
            db.add(job)
            db.commit()
            
            # Start collection asynchronously
            asyncio.create_task(self._execute_collection_job(job.job_id, job_config, db))
            
            logger.info(f"Started collection job {job.job_id}")
            return job.job_id
            
        except Exception as e:
            logger.error(f"Error starting collection job: {e}")
            raise
    
    async def _execute_collection_job(
        self,
        job_id: str,
        config: Dict[str, Any],
        db: Session
    ):
        """Execute the actual data collection"""
        # Implementation would go here - this is a comprehensive method
        # that would use all the above methods based on the job configuration
        pass