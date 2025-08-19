# Trendit 🔥

A comprehensive Reddit data collection and analysis platform built with PRAW (Python Reddit API Wrapper).

## Features

### 🎯 **Comprehensive Data Collection**
- **Multiple Subreddits**: Collect from multiple subreddits simultaneously
- **All Sort Types**: Hot, New, Top, Rising, Controversial posts
- **Time Filters**: Hour, Day, Week, Month, Year, All Time
- **User Profiles**: Collect user data and post history
- **Comments**: Deep comment tree collection with threading
- **Real-time Metrics**: Live score tracking and temporal analysis

### 📊 **Advanced Search & Filtering**
- **Keyword Search**: Search across titles, content, and comments
- **Score Thresholds**: Filter by upvotes, downvote ratio
- **Date Ranges**: Collect posts from specific time periods
- **Author Filtering**: Include/exclude specific users
- **Content Type**: Text posts, links, images, videos
- **NSFW Filtering**: Control adult content collection

### 🔒 **Privacy & Ethics**
- **User Anonymization**: Optional PII removal
- **Rate Limiting**: Respectful API usage
- **Terms Compliance**: Reddit API terms adherence
- **Data Export Controls**: GDPR-compliant exports

### 📈 **Analytics & Insights**
- **Trend Analysis**: Track post performance over time
- **Sentiment Analysis**: Comment sentiment tracking
- **Network Analysis**: User interaction patterns
- **Statistical Reports**: Comprehensive data summaries

### 💾 **Data Management**
- **Multiple Export Formats**: CSV, JSON, JSONL, Parquet
- **Database Storage**: PostgreSQL integration
- **Batch Processing**: Handle large datasets efficiently
- **Data Deduplication**: Prevent duplicate entries

## Quick Start

### Prerequisites
- Python 3.9+
- PostgreSQL
- Reddit API credentials ([Get them here](https://www.reddit.com/prefs/apps))

### Installation

```bash
git clone https://github.com/yourusername/Trendit.git
cd Trendit

# Backend setup
cd backend
pip install -r requirements.txt

# Frontend setup
cd ../frontend
npm install

# Environment configuration
cp .env.example .env
# Edit .env with your Reddit API credentials and database URL
```

### Configuration

Create a `.env` file with:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/trendit

# Reddit API
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USER_AGENT=Trendit/1.0 by YourUsername

# Optional: Advanced Features
OPENAI_API_KEY=your_openai_key  # For sentiment analysis
RATE_LIMIT_REQUESTS=60  # Requests per minute
```

### Database Setup

```bash
cd backend
python init_db.py
```

### Running the Application

```bash
# Terminal 1: Backend
cd backend
uvicorn main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend
npm run dev
```

Open http://localhost:3000 to start collecting Reddit data!

## Architecture

```
Trendit/
├── backend/                 # FastAPI backend
│   ├── main.py             # FastAPI app
│   ├── models/             # Database models
│   ├── services/           # Reddit collection services
│   │   ├── reddit_client.py
│   │   ├── data_collector.py
│   │   └── analytics.py
│   ├── api/                # API endpoints
│   └── utils/              # Utility functions
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API services
│   │   └── utils/          # Frontend utilities
└── docs/                   # Documentation
```

## API Capabilities

### Data Collection Endpoints
- `POST /api/collect/subreddit` - Collect from subreddit(s)
- `POST /api/collect/user` - Collect user data
- `POST /api/collect/search` - Search-based collection
- `GET /api/collect/status/{job_id}` - Job status tracking

### Data Retrieval Endpoints
- `GET /api/data/posts` - Retrieve collected posts
- `GET /api/data/comments` - Retrieve comments
- `GET /api/data/users` - Retrieve user data
- `GET /api/data/analytics` - Get analytics data

### Export Endpoints
- `GET /api/export/{job_id}` - Export collected data
- `GET /api/export/analytics/{job_id}` - Export analytics

## Advanced Features

### Batch Collection
```python
# Collect from multiple subreddits with different parameters
collection_config = {
    "subreddits": ["python", "MachineLearning", "datascience"],
    "sort_types": ["hot", "top"],
    "time_filters": ["week", "month"],
    "post_limit": 100,
    "include_comments": True,
    "max_comment_depth": 3
}
```

### Real-time Monitoring
- Live job progress tracking
- Real-time statistics
- Error monitoring and alerts

### Data Analytics
- Trend analysis over time
- User engagement metrics
- Content performance insights
- Cross-subreddit comparisons

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This tool is for research and educational purposes. Please respect Reddit's API terms of service and the privacy of Reddit users. Always obtain necessary permissions for data collection and analysis.

## Support

- 📖 [Documentation](docs/)
- 🐛 [Issue Tracker](https://github.com/yourusername/Trendit/issues)
- 💬 [Discussions](https://github.com/yourusername/Trendit/discussions)

---

Built with ❤️ by the Trendit team