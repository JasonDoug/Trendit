#!/usr/bin/env python3
"""
Test script for Query API endpoints
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_complex_post_query():
    """Test complex POST query with multiple filters"""
    print("Testing complex post query...")
    
    query_data = {
        "subreddits": ["python", "programming"],
        "keywords": ["fastapi", "async"],
        "min_score": 10,
        "min_upvote_ratio": 0.7,
        "exclude_keywords": ["beginner"],
        "sort_type": "top",
        "time_filter": "week",
        "limit": 5,
        "include_self_text": False
    }
    
    response = requests.post(
        f"{BASE_URL}/api/query/posts",
        json=query_data,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Complex query successful!")
        print(f"   Results: {data['count']}")
        print(f"   Execution time: {data['execution_time_ms']:.2f}ms")
        print(f"   Reddit API calls: {data['reddit_api_calls']}")
        print(f"   Filters applied: {data['filters_applied']}")
        
        if data['results']:
            post = data['results'][0]
            print(f"   Sample post: {post['title'][:60]}... (Score: {post['score']})")
        return True
    else:
        print(f"❌ Complex query failed: {response.status_code}")
        print(f"   Error: {response.text}")
        return False

def test_user_query():
    """Test user query"""
    print("\nTesting user query...")
    
    query_data = {
        "usernames": ["spez", "kn0thing"],  # Reddit founders
        "limit": 2
    }
    
    response = requests.post(
        f"{BASE_URL}/api/query/users",
        json=query_data,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ User query successful!")
        print(f"   Results: {data['count']}")
        print(f"   Execution time: {data['execution_time_ms']:.2f}ms")
        
        if data['results']:
            user = data['results'][0]
            print(f"   Sample user: {user['username']} (Karma: {user.get('total_karma', 'N/A')})")
        return True
    else:
        print(f"❌ User query failed: {response.status_code}")
        print(f"   Error: {response.text}")
        return False

def test_simple_get_query():
    """Test simple GET query"""
    print("\nTesting simple GET query...")
    
    response = requests.get(
        f"{BASE_URL}/api/query/posts/simple",
        params={
            "subreddits": "python",
            "keywords": "django",
            "min_score": 20,
            "limit": 3
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Simple GET query successful!")
        print(f"   Results: {data['count']}")
        print(f"   Execution time: {data['execution_time_ms']:.2f}ms")
        return True
    else:
        print(f"❌ Simple GET query failed: {response.status_code}")
        print(f"   Error: {response.text}")
        return False

def test_health_check():
    """Test API health"""
    print("\nTesting API health...")
    
    response = requests.get(f"{BASE_URL}/health")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ API healthy!")
        print(f"   Status: {data['status']}")
        print(f"   Database: {data['database']}")
        print(f"   Reddit API: {data['reddit_api']}")
        return True
    else:
        print(f"❌ API health check failed: {response.status_code}")
        return False

def main():
    """Run all tests"""
    print("🔥 Trendit Query API Test Suite")
    print("=" * 40)
    
    tests = [
        test_health_check,
        test_simple_get_query,
        test_complex_post_query,
        test_user_query
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
            time.sleep(1)  # Rate limiting
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 40)
    print(f"Test Results: {sum(results)}/{len(results)} passed")
    
    if all(results):
        print("🎉 All Query API tests passed!")
    else:
        print("⚠️  Some tests failed")

if __name__ == "__main__":
    main()