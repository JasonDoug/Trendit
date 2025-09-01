"""
Patch for data_collector.py to fix date range filtering issues.

This patch addresses the core issue where collection jobs find hundreds of posts
but filter them all out due to overly restrictive date ranges.

Apply this patch to services/data_collector.py
"""

# Step 1: Add this import at the top of data_collector.py
IMPORT_TO_ADD = """
from .date_filter_fix import ImprovedDateFiltering, apply_improved_date_filtering
"""

# Step 2: Replace the search_subreddit_posts_by_keyword_and_date method
IMPROVED_SEARCH_METHOD = '''
async def search_subreddit_posts_by_keyword_and_date(
    self,
    subreddit: str,
    keywords: List[str],
    date_from: datetime,
    date_to: datetime,
    limit: int = 100,
    sort_by: str = "score"
) -> List[Dict[str, Any]]:
    """
    Search posts in a specific subreddit by keywords and date range.
    IMPROVED VERSION with better date filtering logic.
    
    Args:
        subreddit: Subreddit name
        keywords: List of keywords to search for
        date_from: Start date
        date_to: End date
        limit: Number of posts to return
        sort_by: Sort criteria (score, comments, date)
    """
    try:
        logger.info(f"Searching for posts in r/{subreddit} with keywords: {keywords}")
        logger.info(f"Date range: {date_from} to {date_to}")
        
        # Calculate days between dates for optimal Reddit time_filter selection
        days_diff = (date_to - date_from).days
        time_filter = ImprovedDateFiltering.select_optimal_time_filter(days_diff)
        
        logger.info(f"Using Reddit time_filter: {time_filter} for {days_diff} day range")
        
        # Search for posts containing keywords
        search_query = " OR ".join(keywords)
        
        async with self.reddit_client as reddit:
            all_posts = await reddit.search_posts(
                query=search_query,
                subreddit_name=subreddit,
                sort="relevance",  # Use relevance for keyword searches
                time_filter=time_filter,  # Use optimal time_filter
                limit=min(limit * 3, 500)  # Get more posts to account for filtering
            )
        
        logger.info(f"Reddit API returned {len(all_posts)} posts")
        
        if not all_posts:
            logger.info(f"No posts found in r/{subreddit} for query: {search_query}")
            return []
        
        # Apply improved date filtering with diagnostic info
        filtered_posts = apply_improved_date_filtering(
            all_posts, 
            days=days_diff,
            debug=True  # Enable debugging to understand filtering
        )
        
        # Additional keyword filtering (since we're using OR search)
        keyword_filtered_posts = []
        for post in filtered_posts:
            title_text = post.get('title', '').lower()
            content_text = (post.get('selftext', '') or '').lower()
            combined_text = f"{title_text} {content_text}"
            
            # Check if ANY keyword appears (OR logic)
            if any(keyword.lower() in combined_text for keyword in keywords):
                keyword_filtered_posts.append(post)
        
        # Sort by specified criteria
        if sort_by == "score":
            keyword_filtered_posts.sort(key=lambda x: x.get('score', 0), reverse=True)
        elif sort_by == "comments":
            keyword_filtered_posts.sort(key=lambda x: x.get('num_comments', 0), reverse=True)
        elif sort_by == "date":
            keyword_filtered_posts.sort(key=lambda x: x.get('created_utc', 0), reverse=True)
        
        # Limit results
        final_results = keyword_filtered_posts[:limit]
        
        logger.info(f"Final results: {len(final_results)} posts after keyword + date filtering")
        return final_results
        
    except Exception as e:
        logger.error(f"Error searching posts in r/{subreddit}: {e}")
        raise
'''

# Step 3: Improve the collection job date range logic
IMPROVED_COLLECTION_DATE_LOGIC = '''
# In api/collect.py, replace the collection job date range logic:

# OLD CODE (around line 310):
# date_from=job.date_from or (datetime.utcnow() - timedelta(days=7)),
# date_to=job.date_to or datetime.utcnow(),

# NEW CODE:
if job.date_from and job.date_to:
    # Use job-specified dates
    date_from = job.date_from
    date_to = job.date_to
else:
    # Use improved date range with buffer for better collection
    date_from, date_to = ImprovedDateFiltering.create_date_range_with_buffer(
        days=7, buffer_hours=4
    )

logger.info(f"Collection date range: {date_from} to {date_to}")
'''

# Step 4: Add debugging to collection process
COLLECTION_DEBUG_CODE = '''
# Add this debugging code after getting posts_data in collect.py:

if posts_data:
    logger.info(f"Collection debug - posts found: {len(posts_data)}")
    # Show date range of collected posts for debugging
    try:
        post_dates = []
        for post in posts_data:
            created_utc = post.get('created_utc')
            if created_utc and isinstance(created_utc, datetime):
                post_dates.append(created_utc)
        
        if post_dates:
            earliest_post = min(post_dates)
            latest_post = max(post_dates)
            logger.info(f"Collected posts date range: {earliest_post} to {latest_post}")
    except Exception as e:
        logger.warning(f"Error analyzing post dates: {e}")
else:
    logger.warning("No posts collected - this might indicate a date filtering issue")
'''

# Instructions for applying the patch
PATCH_INSTRUCTIONS = """
=== PATCH APPLICATION INSTRUCTIONS ===

1. IMPORTS: Add the import at the top of services/data_collector.py:
   from .date_filter_fix import ImprovedDateFiltering, apply_improved_date_filtering

2. METHOD REPLACEMENT: Replace the entire search_subreddit_posts_by_keyword_and_date method 
   in services/data_collector.py with the IMPROVED_SEARCH_METHOD above

3. COLLECTION LOGIC: Update the date range logic in api/collect.py around line 310
   with the IMPROVED_COLLECTION_DATE_LOGIC

4. ADD DEBUGGING: Add the COLLECTION_DEBUG_CODE to api/collect.py after getting posts_data

5. TEST: Create a collection job and monitor the logs to see:
   - "Using Reddit time_filter: X for Y day range"  
   - "Reddit API returned N posts"
   - "Date filtering: N -> M posts"
   - "Final results: X posts after keyword + date filtering"

This should fix the issue where jobs find hundreds of posts but filter them all out.
"""

if __name__ == "__main__":
    print("Date Filter Patch for Trendit")
    print("="*50)
    print(PATCH_INSTRUCTIONS)