#!/usr/bin/env python3
"""
Test script for the improved date filtering logic.
This validates that the new filtering approach works correctly.
"""

import sys
from datetime import datetime, timedelta, timezone
from services.date_filter_fix import ImprovedDateFiltering, apply_improved_date_filtering

def create_sample_posts():
    """Create sample Reddit posts with different dates for testing."""
    now = datetime.now(timezone.utc)
    
    posts = [
        {
            'reddit_id': 'post1',
            'title': 'Recent post about fastapi',
            'created_utc': now - timedelta(hours=2),  # 2 hours ago
            'score': 100
        },
        {
            'reddit_id': 'post2', 
            'title': 'Yesterday post about fastapi',
            'created_utc': now - timedelta(days=1),  # 1 day ago
            'score': 75
        },
        {
            'reddit_id': 'post3',
            'title': 'Week old post about fastapi', 
            'created_utc': now - timedelta(days=7),  # 7 days ago
            'score': 50
        },
        {
            'reddit_id': 'post4',
            'title': 'Very old post about fastapi',
            'created_utc': now - timedelta(days=10),  # 10 days ago (should be filtered)
            'score': 200
        },
        {
            'reddit_id': 'post5',
            'title': 'Future post about fastapi',
            'created_utc': now + timedelta(hours=1),  # 1 hour in future (edge case)
            'score': 25
        }
    ]
    
    return posts

def test_time_filter_selection():
    """Test the optimal time filter selection logic."""
    print("Testing time filter selection:")
    
    test_cases = [
        (1, "day"),
        (3, "week"), 
        (7, "week"),
        (15, "month"),
        (30, "month"),
        (60, "year"),
        (400, "all")
    ]
    
    for days, expected in test_cases:
        actual = ImprovedDateFiltering.select_optimal_time_filter(days)
        status = "✅" if actual == expected else "❌"
        print(f"  {days} days -> {actual} (expected {expected}) {status}")

def test_date_filtering():
    """Test the improved date filtering logic."""
    print("\nTesting date filtering:")
    
    posts = create_sample_posts()
    print(f"Created {len(posts)} sample posts")
    
    # Test different day ranges
    for days in [3, 7, 14]:
        print(f"\n--- Testing {days}-day filter ---")
        filtered = apply_improved_date_filtering(posts, days=days, debug=True)
        
        print(f"Results: {len(posts)} -> {len(filtered)} posts")
        for post in filtered:
            age_hours = (datetime.now(timezone.utc) - post['created_utc']).total_seconds() / 3600
            print(f"  - {post['reddit_id']}: {age_hours:.1f}h ago, score: {post['score']}")

def test_edge_cases():
    """Test edge cases for date filtering."""
    print("\n--- Testing Edge Cases ---")
    
    # Empty list
    empty_result = apply_improved_date_filtering([], days=7)
    print(f"Empty list test: {len(empty_result)} posts (expected 0)")
    
    # Posts without created_utc
    bad_posts = [
        {'reddit_id': 'bad1', 'title': 'No date'},
        {'reddit_id': 'bad2', 'title': 'Bad date', 'created_utc': 'invalid'},
        {'reddit_id': 'good1', 'title': 'Good post', 'created_utc': datetime.now(timezone.utc)}
    ]
    
    filtered_bad = apply_improved_date_filtering(bad_posts, days=7, debug=True) 
    print(f"Bad data test: {len(bad_posts)} -> {len(filtered_bad)} posts")

def simulate_reddit_collection_scenario():
    """Simulate the actual Reddit collection scenario that was failing."""
    print("\n--- Simulating Reddit Collection Scenario ---")
    
    # Simulate finding 233 posts but filtering them all out
    now = datetime.now(timezone.utc)
    many_posts = []
    
    # Create posts spread over different time periods
    for i in range(233):
        # Most posts are 8-15 days old (outside typical 7-day window)
        age_days = 8 + (i % 7)  # 8-14 days old
        post = {
            'reddit_id': f'post_{i}',
            'title': f'Post {i} about flask',
            'created_utc': now - timedelta(days=age_days),
            'score': 10 + i
        }
        many_posts.append(post)
    
    # Add a few recent posts that should pass
    for i in range(5):
        post = {
            'reddit_id': f'recent_{i}',
            'title': f'Recent post {i} about flask',
            'created_utc': now - timedelta(days=i + 1),  # 1-5 days old
            'score': 100 + i
        }
        many_posts.append(post)
    
    print(f"Simulating collection of {len(many_posts)} posts")
    
    # Test with old restrictive filtering (7 days exact)
    date_from = now - timedelta(days=7)
    date_to = now
    strict_count = sum(1 for post in many_posts 
                      if date_from <= post['created_utc'] <= date_to)
    print(f"Old strict filtering (exactly 7 days): {strict_count} posts would pass")
    
    # Test with improved filtering
    filtered = apply_improved_date_filtering(many_posts, days=7, debug=True)
    print(f"New improved filtering: {len(filtered)} posts pass")
    
    # Show the improvement
    improvement = len(filtered) - strict_count
    print(f"Improvement: +{improvement} posts collected")

if __name__ == "__main__":
    print("🧪 Date Filter Testing Suite")
    print("="*50)
    
    test_time_filter_selection()
    test_date_filtering() 
    test_edge_cases()
    simulate_reddit_collection_scenario()
    
    print("\n✅ All tests completed!")
    print("\nNext steps:")
    print("1. Apply the patch from date_filter_patch.py to data_collector.py")
    print("2. Test with a real collection job")
    print("3. Monitor the logs for improved filtering behavior")