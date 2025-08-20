# Trendit API - cURL Examples

Complete collection of cURL examples for all Trendit API endpoints.

## Core Endpoints

### Health Check
```bash
# Basic health check
curl -X GET "http://localhost:8000/health"

# Health check with formatted output
curl -s "http://localhost:8000/health" | python -m json.tool
```

### API Information
```bash
# Get API info and features
curl -X GET "http://localhost:8000/"

# Get just the scenarios list
curl -s "http://localhost:8000/" | python -c "import sys,json; data=json.load(sys.stdin); print(json.dumps(data['scenarios'], indent=2))"
```

## Scenarios API - Quickstart Examples

### Scenario 1: Subreddit Keyword Search
```bash
# Basic keyword search
curl -X GET "http://localhost:8000/api/scenarios/1/subreddit-keyword-search?subreddit=python&keywords=fastapi&date_from=2024-01-01&date_to=2024-12-31&limit=5"

# Multiple keywords
curl -X GET "http://localhost:8000/api/scenarios/1/subreddit-keyword-search?subreddit=programming&keywords=python,django,flask&date_from=2024-06-01&date_to=2024-12-31&limit=10&sort_by=score"

# Search in different subreddit with date range
curl -X GET "http://localhost:8000/api/scenarios/1/subreddit-keyword-search?subreddit=MachineLearning&keywords=pytorch,tensorflow&date_from=2024-01-01&date_to=2024-06-30&limit=15"

# Search for async programming posts
curl -X GET "http://localhost:8000/api/scenarios/1/subreddit-keyword-search?subreddit=python&keywords=async,await,asyncio&date_from=2024-01-01&date_to=2024-12-31&limit=20&sort_by=comments"
```

### Scenario 2: Multi-Subreddit Trending
```bash
# Trending in programming subreddits today
curl -X GET "http://localhost:8000/api/scenarios/2/trending-multi-subreddits?subreddits=python,programming,coding&timeframe=day&limit=10"

# Trending this week in AI subreddits
curl -X GET "http://localhost:8000/api/scenarios/2/trending-multi-subreddits?subreddits=MachineLearning,artificial,OpenAI&timeframe=week&limit=15"

# Trending web development topics
curl -X GET "http://localhost:8000/api/scenarios/2/trending-multi-subreddits?subreddits=webdev,javascript,reactjs,node&timeframe=day&limit=20"

# Trending in data science communities
curl -X GET "http://localhost:8000/api/scenarios/2/trending-multi-subreddits?subreddits=datascience,analytics,statistics&timeframe=week&limit=12"
```

### Scenario 3: Top Posts from r/all
```bash
# Hot posts from r/all today
curl -X GET "http://localhost:8000/api/scenarios/3/top-posts-all?sort_type=hot&time_filter=day&limit=10"

# Top posts this week
curl -X GET "http://localhost:8000/api/scenarios/3/top-posts-all?sort_type=top&time_filter=week&limit=25&exclude_nsfw=true"

# Rising posts from r/all
curl -X GET "http://localhost:8000/api/scenarios/3/top-posts-all?sort_type=rising&time_filter=hour&limit=15"

# Controversial posts this month
curl -X GET "http://localhost:8000/api/scenarios/3/top-posts-all?sort_type=controversial&time_filter=month&limit=20"
```

### Scenario 4: Most Popular Posts Today
```bash
# Most popular post in r/python by score
curl -X GET "http://localhost:8000/api/scenarios/4/most-popular-today?subreddit=python&metric=score"

# Most commented post in r/programming
curl -X GET "http://localhost:8000/api/scenarios/4/most-popular-today?subreddit=programming&metric=comments"

# Highest upvote ratio in r/MachineLearning
curl -X GET "http://localhost:8000/api/scenarios/4/most-popular-today?subreddit=MachineLearning&metric=upvote_ratio"

# Most popular in different subreddits
curl -X GET "http://localhost:8000/api/scenarios/4/most-popular-today?subreddit=webdev&metric=score"
curl -X GET "http://localhost:8000/api/scenarios/4/most-popular-today?subreddit=datascience&metric=comments"
```

### Scenario Comments: Advanced Comment Analysis
```bash
# Top comments about Django
curl -X GET "http://localhost:8000/api/scenarios/comments/top-by-criteria?subreddit=python&keywords=django&limit=10"

# High-scoring comments in programming
curl -X GET "http://localhost:8000/api/scenarios/comments/top-by-criteria?subreddit=programming&min_score=50&limit=15"

# Comments about machine learning
curl -X GET "http://localhost:8000/api/scenarios/comments/top-by-criteria?subreddit=MachineLearning&keywords=neural,networks&limit=20"

# Recent quality comments
curl -X GET "http://localhost:8000/api/scenarios/comments/top-by-criteria?subreddit=python&min_score=25&limit=12"
```

### Scenario Users: User Activity Analysis
```bash
# Top users by post count in r/python
curl -X GET "http://localhost:8000/api/scenarios/users/top-by-activity?subreddits=python&metric=post_count&limit=10"

# Active users across multiple subreddits
curl -X GET "http://localhost:8000/api/scenarios/users/top-by-activity?subreddits=python,programming,webdev&metric=total_score&limit=15"

# Most active commenters
curl -X GET "http://localhost:8000/api/scenarios/users/top-by-activity?subreddits=MachineLearning&metric=comment_count&limit=20"

# Top contributors in data science
curl -X GET "http://localhost:8000/api/scenarios/users/top-by-activity?subreddits=datascience,statistics&metric=total_score&limit=12"
```

### Scenario Examples
```bash
# Get all scenario examples and usage
curl -X GET "http://localhost:8000/api/scenarios/examples"

# Pretty print scenarios
curl -s "http://localhost:8000/api/scenarios/examples" | python -m json.tool
```

## Query API - Advanced Flexible Queries

### Simple GET Queries
```bash
# Basic simple query
curl -X GET "http://localhost:8000/api/query/posts/simple?subreddits=python&keywords=fastapi&limit=5"

# Multiple subreddits with score filter
curl -X GET "http://localhost:8000/api/query/posts/simple?subreddits=python,programming&keywords=django&min_score=50&limit=10"

# Search for machine learning posts
curl -X GET "http://localhost:8000/api/query/posts/simple?subreddits=MachineLearning,artificial&keywords=neural,deep&min_score=100&limit=8"

# Web development queries
curl -X GET "http://localhost:8000/api/query/posts/simple?subreddits=webdev,javascript&keywords=react,vue&min_score=25&limit=12"
```

### Advanced POST Queries

#### Complex Post Filtering
```bash
# High-quality Python posts with multiple filters
curl -X POST "http://localhost:8000/api/query/posts" \
  -H "Content-Type: application/json" \
  -d '{
    "subreddits": ["python", "programming"],
    "keywords": ["async", "performance", "optimization"],
    "min_score": 100,
    "min_upvote_ratio": 0.85,
    "exclude_keywords": ["beginner", "help", "question"],
    "sort_type": "top",
    "time_filter": "week",
    "limit": 15
  }'

# Machine Learning research posts
curl -X POST "http://localhost:8000/api/query/posts" \
  -H "Content-Type: application/json" \
  -d '{
    "subreddits": ["MachineLearning", "artificial"],
    "keywords": ["transformer", "neural", "model"],
    "min_score": 200,
    "min_comments": 20,
    "exclude_nsfw": true,
    "exclude_stickied": true,
    "sort_type": "top",
    "time_filter": "month",
    "limit": 20
  }'

# Web development framework comparison
curl -X POST "http://localhost:8000/api/query/posts" \
  -H "Content-Type: application/json" \
  -d '{
    "subreddits": ["webdev", "javascript", "reactjs"],
    "keywords": ["framework", "comparison", "vs"],
    "min_score": 50,
    "min_upvote_ratio": 0.8,
    "max_comments": 200,
    "sort_type": "hot",
    "limit": 12
  }'

# Data science tutorials and guides
curl -X POST "http://localhost:8000/api/query/posts" \
  -H "Content-Type: application/json" \
  -d '{
    "subreddits": ["datascience", "analytics", "statistics"],
    "keywords": ["tutorial", "guide", "how-to"],
    "min_score": 75,
    "exclude_keywords": ["basic", "beginner"],
    "content_types": ["text", "link"],
    "sort_type": "top",
    "time_filter": "month",
    "limit": 10
  }'

# Author-specific filtering
curl -X POST "http://localhost:8000/api/query/posts" \
  -H "Content-Type: application/json" \
  -d '{
    "subreddits": ["python"],
    "exclude_authors": ["AutoModerator", "bot"],
    "min_score": 30,
    "exclude_deleted": true,
    "exclude_removed": true,
    "sort_type": "new",
    "limit": 20
  }'
```

#### Comment Analysis Queries
```bash
# High-quality technical discussions
curl -X POST "http://localhost:8000/api/query/comments" \
  -H "Content-Type: application/json" \
  -d '{
    "subreddits": ["python", "programming"],
    "keywords": ["architecture", "design", "pattern"],
    "min_score": 15,
    "max_depth": 3,
    "exclude_deleted": true,
    "sort_type": "top",
    "limit": 25
  }'

# Comments from specific posts
curl -X POST "http://localhost:8000/api/query/comments" \
  -H "Content-Type: application/json" \
  -d '{
    "post_ids": ["abc123", "def456"],
    "min_score": 10,
    "max_depth": 2,
    "exclude_deleted": true,
    "limit": 50
  }'

# Long-form technical comments
curl -X POST "http://localhost:8000/api/query/comments" \
  -H "Content-Type: application/json" \
  -d '{
    "subreddits": ["MachineLearning"],
    "min_score": 20,
    "keywords": ["explanation", "detailed", "analysis"],
    "exclude_authors": ["AutoModerator"],
    "sort_type": "best",
    "limit": 15
  }'

# Discussion thread analysis
curl -X POST "http://localhost:8000/api/query/comments" \
  -H "Content-Type: application/json" \
  -d '{
    "subreddits": ["webdev", "javascript"],
    "keywords": ["debate", "discussion", "opinion"],
    "min_score": 5,
    "min_depth": 1,
    "max_depth": 4,
    "limit": 30
  }'
```

#### User Analysis Queries
```bash
# Experienced developers analysis
curl -X POST "http://localhost:8000/api/query/users" \
  -H "Content-Type: application/json" \
  -d '{
    "subreddits": ["python", "programming"],
    "min_total_karma": 5000,
    "min_account_age_days": 730,
    "limit": 20
  }'

# High-karma machine learning contributors
curl -X POST "http://localhost:8000/api/query/users" \
  -H "Content-Type: application/json" \
  -d '{
    "subreddits": ["MachineLearning", "artificial"],
    "min_comment_karma": 2000,
    "min_link_karma": 1000,
    "min_account_age_days": 365,
    "limit": 15
  }'

# Active recent contributors
curl -X POST "http://localhost:8000/api/query/users" \
  -H "Content-Type: application/json" \
  -d '{
    "subreddits": ["webdev", "javascript"],
    "min_post_count": 5,
    "min_comment_count": 20,
    "timeframe_days": 30,
    "exclude_suspended": true,
    "limit": 25
  }'

# Specific user profiles
curl -X POST "http://localhost:8000/api/query/users" \
  -H "Content-Type: application/json" \
  -d '{
    "usernames": ["spez", "kn0thing", "reddit"],
    "limit": 3
  }'

# Premium/verified users
curl -X POST "http://localhost:8000/api/query/users" \
  -H "Content-Type: application/json" \
  -d '{
    "subreddits": ["python"],
    "include_verified_only": true,
    "min_total_karma": 1000,
    "limit": 10
  }'
```

### Query Examples
```bash
# Get all query examples and documentation
curl -X GET "http://localhost:8000/api/query/examples"

# Pretty print query examples
curl -s "http://localhost:8000/api/query/examples" | python -m json.tool
```

## Documentation Endpoints

```bash
# OpenAPI specification
curl -X GET "http://localhost:8000/openapi.json"

# Get just the paths
curl -s "http://localhost:8000/openapi.json" | python -c "import sys,json; data=json.load(sys.stdin); [print(f'{method.upper()} {path}') for path, methods in data['paths'].items() for method in methods.keys()]"

# Count endpoints by tag
curl -s "http://localhost:8000/openapi.json" | python -c "
import sys,json
data=json.load(sys.stdin)
tags = {}
for path, methods in data['paths'].items():
    for method, details in methods.items():
        tag = details.get('tags', ['Untagged'])[0]
        tags[tag] = tags.get(tag, 0) + 1
for tag, count in tags.items():
    print(f'{tag}: {count} endpoints')
"
```

## Batch Testing Examples

```bash
# Test all core endpoints
echo "Testing core endpoints..."
curl -s "http://localhost:8000/" > /dev/null && echo "✅ Root endpoint"
curl -s "http://localhost:8000/health" > /dev/null && echo "✅ Health endpoint"

# Test scenario endpoints
echo "Testing scenario endpoints..."
curl -s "http://localhost:8000/api/scenarios/examples" > /dev/null && echo "✅ Scenarios examples"
curl -s "http://localhost:8000/api/scenarios/1/subreddit-keyword-search?subreddit=python&keywords=test&date_from=2024-01-01&date_to=2024-12-31&limit=1" > /dev/null && echo "✅ Scenario 1"

# Test query endpoints
echo "Testing query endpoints..."
curl -s "http://localhost:8000/api/query/examples" > /dev/null && echo "✅ Query examples"
curl -s "http://localhost:8000/api/query/posts/simple?subreddits=python&limit=1" > /dev/null && echo "✅ Simple query"

# Performance test
echo "Performance testing..."
time curl -s "http://localhost:8000/api/query/posts/simple?subreddits=python&keywords=fastapi&limit=5" > /dev/null
```

## Response Processing Examples

```bash
# Extract just titles from posts
curl -s "http://localhost:8000/api/query/posts/simple?subreddits=python&keywords=fastapi&limit=5" | \
  python -c "import sys,json; data=json.load(sys.stdin); [print(f'• {post[\"title\"]}') for post in data['results']]"

# Get execution time and count
curl -s "http://localhost:8000/api/query/posts/simple?subreddits=python&limit=3" | \
  python -c "import sys,json; data=json.load(sys.stdin); print(f'Results: {data[\"count\"]}, Time: {data[\"execution_time_ms\"]:.2f}ms')"

# Extract user karma information
curl -s -X POST "http://localhost:8000/api/query/users" \
  -H "Content-Type: application/json" \
  -d '{"usernames": ["spez"], "limit": 1}' | \
  python -c "import sys,json; data=json.load(sys.stdin); user=data['results'][0]; print(f'{user[\"username\"]}: {user[\"total_karma\"]} karma')"

# Count posts by subreddit
curl -s "http://localhost:8000/api/query/posts/simple?subreddits=python,programming&limit=20" | \
  python -c "
import sys,json
data=json.load(sys.stdin)
subreddits = {}
for post in data['results']:
    sub = post['subreddit']
    subreddits[sub] = subreddits.get(sub, 0) + 1
for sub, count in subreddits.items():
    print(f'{sub}: {count} posts')
"
```

## Error Testing

```bash
# Test invalid subreddit
curl -X GET "http://localhost:8000/api/scenarios/1/subreddit-keyword-search?subreddit=invalidsubreddit&keywords=test&date_from=2024-01-01&date_to=2024-12-31"

# Test malformed JSON
curl -X POST "http://localhost:8000/api/query/posts" \
  -H "Content-Type: application/json" \
  -d '{"invalid": json}'

# Test missing required parameters
curl -X GET "http://localhost:8000/api/scenarios/1/subreddit-keyword-search?subreddit=python"

# Test invalid date range
curl -X GET "http://localhost:8000/api/scenarios/1/subreddit-keyword-search?subreddit=python&keywords=test&date_from=2024-12-31&date_to=2024-01-01"
```