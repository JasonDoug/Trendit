# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Development Commands

### Backend (Python/FastAPI)
```bash
# Setup and dependencies
cd backend
pip install -r requirements.txt

# Database initialization
python init_db.py

# Run the FastAPI server
uvicorn main:app --reload --port 8000

# Run tests
python test_api.py

# Test individual scenarios
python -c "import asyncio; from test_api import test_reddit_connection; asyncio.run(test_reddit_connection())"
```

### Frontend (React/Node.js)
```bash
# Setup (when frontend is implemented)
cd frontend
npm install

# Development server
npm run dev

# Build for production
npm run build
```

### Environment Setup
- Copy `.env.example` to `.env` and configure:
  - `DATABASE_URL`: PostgreSQL connection string
  - `REDDIT_CLIENT_ID` and `REDDIT_CLIENT_SECRET`: Reddit API credentials
  - Optional: `OPENAI_API_KEY` for sentiment analysis

## Architecture Overview

### Core System Design
Trendit is a Reddit data collection and analysis platform with a FastAPI backend and planned React frontend. The system follows a service-oriented architecture:

**Backend Services:**
- `RedditClient` (`services/reddit_client.py`): PRAW-based Reddit API interaction
- `DataCollector` (`services/data_collector.py`): High-level data collection scenarios
- `AnalyticsService` (`services/analytics.py`): Data analysis and insights
- API endpoints (`api/scenarios.py`): REST API for frontend communication

**Database Models:**
- `CollectionJob`: Tracks data collection tasks with parameters and status
- `RedditPost`: Stores Reddit posts with metadata and metrics
- `RedditComment`: Stores comment threads with hierarchy
- `RedditUser`: User profiles and karma data
- `Analytics`: Generated insights and summaries

### Key Data Flow
1. User initiates collection via API endpoints (planned frontend UI)
2. `DataCollector` creates `CollectionJob` with specified parameters
3. `RedditClient` interfaces with Reddit API using PRAW
4. Collected data stored in PostgreSQL with full metadata
5. `AnalyticsService` generates insights from collected data
6. Results exported in multiple formats (CSV, JSON, Parquet)

### Scenario-Based Architecture
The system implements specific user scenarios:
- **Scenario 1**: Keyword search within subreddits by date range
- **Scenario 2**: Multi-subreddit trending analysis  
- **Scenario 3**: Top posts from r/all with filters
- **Scenario 4**: Most popular posts by timeframe
- **Advanced**: Comment analysis and user activity tracking

## Important Technical Details

### Database Schema
- Uses SQLAlchemy ORM with PostgreSQL
- Comprehensive indexing for performance (`idx_reddit_posts_subreddit_score`, etc.)
- Enum types for status and filter values (`JobStatus`, `SortType`, `TimeFilter`)
- JSON columns for flexible parameter storage

### Reddit API Integration
- PRAW (Python Reddit API Wrapper) for authentication
- Rate limiting and respectful API usage built-in
- Supports all Reddit sort types (hot, new, top, rising, controversial)
- Time filters (hour, day, week, month, year, all)
- Anonymous data collection with optional PII removal

### Async Architecture
- FastAPI with async/await patterns throughout
- Background job processing for large collections
- Real-time status tracking and progress monitoring

### Data Export Capabilities
- Multiple formats: CSV, JSON, JSONL, Parquet
- Batch processing for large datasets
- GDPR-compliant data export controls

## Key Files and Responsibilities

- `main.py`: FastAPI application setup, CORS, health checks
- `models/models.py`: Complete database schema with relationships
- `services/data_collector.py`: Core collection logic implementing user scenarios
- `services/reddit_client.py`: Reddit API abstraction layer
- `api/scenarios.py`: REST endpoints mapping to collection scenarios
- `test_api.py`: Comprehensive test suite for all functionality

## Testing Strategy

Run `python test_api.py` to validate:
- Reddit API connectivity
- All four main scenarios
- Comment and user analysis features
- Environment configuration

The test suite provides end-to-end validation of the collection pipeline and serves as documentation for expected functionality.