# Trendit API Testing Guide

This document provides instructions for testing the Trendit API without Claude Code assistance.

## Prerequisites

### 1. System Requirements
- Python 3.9+
- PostgreSQL database server
- Git (for cloning repository)

### 2. Reddit API Credentials
You need a Reddit application configured at https://www.reddit.com/prefs/apps:
- App type: **"script"** (not web app)
- Name: Your app name (e.g., "Trendit")
- Redirect URI: `http://localhost:8080` (for script apps)

## Setup Instructions

### 1. Clone and Navigate to Project
```bash
git clone <repository-url>
cd Trendit/backend
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy the example environment file and edit it:
```bash
cp .env.example .env
nano .env  # or use your preferred editor
```

Update `.env` with your actual values:
```env
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/database_name

# Reddit API Configuration
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=YourAppName by u/yourusername

# Server Configuration
HOST=localhost
PORT=8000
RELOAD=true

# Logging Configuration
LOG_LEVEL=INFO
```

### 5. Initialize Database
```bash
python init_db.py
```

Expected output:
```
INFO - Starting Trendit database initialization...
INFO - Database connection successful!
INFO - Creating database tables...
INFO - Database tables created successfully!
INFO - Tables created:
  - users
  - collection_jobs
  - reddit_posts
  - reddit_comments
  - reddit_users
  - analytics
INFO - Database initialization completed successfully!
```

## Running Tests

### Test 1: Simple Reddit Connection Test
```bash
python test_reddit_simple.py
```

Expected output:
```
Testing Reddit API connection...
Client ID: your_client_id
User Agent: YourAppName by u/yourusername
Client Secret: ******************************
Read-only mode: True
Subreddit: python
Subscribers: 1385253
Test post: Sunday Daily Thread: What's everyone working on th...
✅ Reddit API connection successful!
```

### Test 2: Comprehensive API Test Suite
```bash
python test_api.py
```

This test runs through all scenarios:
1. Reddit API connection validation
2. Scenario 1: Keyword search with date range
3. Scenario 2: Multi-subreddit trending analysis
4. Scenario 3: Top posts from r/all
5. Scenario 4: Most popular post today
6. Comment and user analysis

Expected final output:
```
INFO - All tests completed successfully!
INFO - Trendit API is ready for use!
```

### Test 3: Start API Server
```bash
uvicorn main:app --reload --port 8000
```

Expected output:
```
INFO - Starting Trendit API server...
INFO - Database tables created/verified
INFO - Uvicorn running on http://127.0.0.1:8000
INFO - Application startup complete.
```

### Test 4: API Endpoint Testing

With the server running, test endpoints in a new terminal:

#### Health Check
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "reddit_api": "configured",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

#### API Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Spec**: http://localhost:8000/openapi.json

#### Test Scenario Endpoints (Quickstarts)
```bash
# Scenario 1: Keyword search
curl "http://localhost:8000/api/scenarios/1/subreddit-keyword-search?subreddit=python&keywords=fastapi&date_from=2024-01-01&date_to=2024-12-31&limit=3"

# Scenario 2: Multi-subreddit trending
curl "http://localhost:8000/api/scenarios/2/trending-multi-subreddits?subreddits=python,programming&timeframe=day&limit=5"

# Scenario 3: Top posts from r/all
curl "http://localhost:8000/api/scenarios/3/top-posts-all?sort_type=hot&time_filter=day&limit=5"

# Scenario 4: Most popular today
curl "http://localhost:8000/api/scenarios/4/most-popular-today?subreddit=python&metric=score"

# Get all scenario examples
curl http://localhost:8000/api/scenarios/examples
```

#### Test Query Endpoints (Advanced)
```bash
# Simple GET query
curl "http://localhost:8000/api/query/posts/simple?subreddits=python&keywords=django&min_score=20&limit=3"

# Multiple subreddits with filtering
curl "http://localhost:8000/api/query/posts/simple?subreddits=python,programming&keywords=async&min_score=50&limit=5"

# Get query examples
curl http://localhost:8000/api/query/examples

# Complex POST query - Advanced filtering
curl -X POST http://localhost:8000/api/query/posts \
  -H "Content-Type: application/json" \
  -d '{
    "subreddits": ["python", "programming"],
    "keywords": ["fastapi", "async"],
    "min_score": 100,
    "min_upvote_ratio": 0.8,
    "exclude_keywords": ["beginner"],
    "sort_type": "top",
    "time_filter": "week",
    "limit": 10
  }'

# User analysis query
curl -X POST http://localhost:8000/api/query/users \
  -H "Content-Type: application/json" \
  -d '{
    "subreddits": ["python"],
    "min_total_karma": 1000,
    "min_account_age_days": 365,
    "limit": 10
  }'

# Comment analysis query
curl -X POST http://localhost:8000/api/query/comments \
  -H "Content-Type: application/json" \
  -d '{
    "subreddits": ["python"],
    "keywords": ["django"],
    "min_score": 10,
    "limit": 15
  }'
```

### Test 5: Query API Test Suite
Run the comprehensive Query API test suite:
```bash
python test_query_api.py
```

Expected output:
```
🔥 Trendit Query API Test Suite
========================================
✅ API healthy!
✅ Simple GET query successful!
✅ Complex query successful!
✅ User query successful!
========================================
Test Results: 4/4 passed
🎉 All Query API tests passed!
```

## Troubleshooting

### Common Issues

#### 1. Database Connection Failed
**Error**: `Database connection failed: could not connect to server`
**Solution**: 
- Ensure PostgreSQL is running
- Verify DATABASE_URL credentials
- Check if database exists

#### 2. Reddit API 401 Unauthorized
**Error**: `received 401 HTTP response`
**Solutions**:
- Verify Reddit app is type "script" not "web app"
- Double-check CLIENT_ID and CLIENT_SECRET
- Ensure USER_AGENT format is correct

#### 3. Import Errors
**Error**: `ImportError: attempted relative import beyond top-level package`
**Solution**: Run commands from the `backend/` directory, not subdirectories

#### 4. Virtual Environment Issues
**Error**: `pip: command not found` or module import errors
**Solution**: 
- Ensure virtual environment is activated: `source venv/bin/activate`
- Reinstall dependencies: `pip install -r requirements.txt`

### Performance Notes

- **PRAW Warnings**: You'll see "asynchronous environment" warnings. These are normal and don't affect functionality.
- **Test Duration**: Comprehensive tests take 2-5 minutes due to Reddit API rate limiting.
- **Rate Limiting**: Reddit API has built-in rate limiting (60 requests/minute typically).

## Test Results Interpretation

### ✅ Success Indicators
- Database tables created successfully
- Reddit API connection successful
- All scenario tests pass
- API server starts without errors
- Health endpoint returns "healthy" status

### ❌ Failure Indicators
- 401 errors (authentication issues)
- Database connection failures
- Import/module errors
- Server startup failures

## Production Considerations

Before deploying to production:

1. **Environment Variables**: Use secure methods to store credentials
2. **Database**: Use production PostgreSQL instance
3. **HTTPS**: Configure SSL/TLS certificates
4. **Rate Limiting**: Implement API rate limiting
5. **Monitoring**: Add logging and monitoring
6. **Async PRAW**: Consider migrating to Async PRAW for better performance

## Support

If tests fail:
1. Check the troubleshooting section above
2. Verify all prerequisites are met
3. Ensure environment variables are correctly set
4. Check Reddit app configuration at https://www.reddit.com/prefs/apps