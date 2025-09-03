# Trendit Frontend API Specification
*Comprehensive Guide for UX/UI AI Code Builder*

## Overview

Trendit is a Reddit data collection and analytics platform that provides comprehensive social media insights. This document outlines all API endpoints needed to build a beautiful, functional frontend with modern UI/UX patterns.

## Base Configuration

```javascript
const API_BASE_URL = "http://localhost:8000"
const API_HEADERS = {
  "Content-Type": "application/json",
  "Authorization": "Bearer {JWT_TOKEN}" // Required for authenticated endpoints
}
```

## Authentication Flow

### 1. User Registration
```http
POST /auth/register
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com", 
  "password": "secure_password123"
}
```

**Response:**
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "is_active": true,
  "subscription_status": "inactive",
  "created_at": "2025-09-02T12:00:00Z"
}
```

### 2. User Login
```http
POST /auth/login
Content-Type: application/json

{
  "username": "john_doe",
  "password": "secure_password123"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "subscription_status": "active"
  }
}
```

### 3. Get Current User Profile
```http
GET /auth/me
Authorization: Bearer {JWT_TOKEN}
```

## API Key Management

### 1. Create API Key
```http
POST /auth/api-keys
Authorization: Bearer {JWT_TOKEN}
Content-Type: application/json

{
  "name": "My Dashboard Key",
  "expires_at": "2025-12-31T23:59:59Z" // Optional
}
```

**Response:**
```json
{
  "id": 1,
  "name": "My Dashboard Key",
  "key": "tk_DJkdLEPxaBDhtGPz5s6RY3vJni-zdIWXJk27QtBlC7k",
  "created_at": "2025-09-02T12:00:00Z",
  "expires_at": "2025-12-31T23:59:59Z"
}
```

### 2. List API Keys
```http
GET /auth/api-keys
Authorization: Bearer {JWT_TOKEN}
```

### 3. Delete API Key
```http
DELETE /auth/api-keys/{key_id}
Authorization: Bearer {JWT_TOKEN}
```

## Subscription & Billing

### 1. Get Current Subscription
```http
GET /billing/subscription
Authorization: Bearer {JWT_TOKEN}
```

**Response:**
```json
{
  "tier": "pro",
  "status": "active",
  "current_period_end": "2025-10-02T12:00:00Z",
  "monthly_api_calls_limit": 10000,
  "monthly_exports_limit": 100,
  "usage": {
    "api_calls_used": 2450,
    "exports_used": 15
  }
}
```

### 2. Create Paddle Subscription
```http
POST /billing/create-subscription
Authorization: Bearer {JWT_TOKEN}
Content-Type: application/json

{
  "tier": "pro", // or "enterprise"
  "billing_cycle": "monthly"
}
```

### 3. Get Billing History
```http
GET /billing/history
Authorization: Bearer {JWT_TOKEN}
```

## Data Collection Scenarios

### 1. Get Available Scenarios
```http
GET /api/scenarios/examples
Authorization: Bearer {JWT_TOKEN}
```

**Response:**
```json
{
  "scenarios": [
    {
      "id": "keyword_search",
      "name": "Keyword Search in Subreddits",
      "description": "Search for posts containing specific keywords within subreddits and date ranges",
      "example_params": {
        "subreddits": ["MachineLearning", "artificial"],
        "keywords": ["GPT", "transformer", "AI"],
        "date_from": "2025-08-01T00:00:00Z",
        "date_to": "2025-09-01T00:00:00Z"
      }
    },
    {
      "id": "trending_analysis",
      "name": "Multi-Subreddit Trending Analysis",
      "description": "Identify trending topics across multiple subreddits",
      "example_params": {
        "subreddits": ["python", "django", "flask"],
        "timeframe": "week"
      }
    }
  ]
}
```

### 2. Execute Scenario
```http
POST /api/scenarios/{scenario_id}/execute
Authorization: Bearer {JWT_TOKEN}
Content-Type: application/json

{
  "subreddits": ["python", "MachineLearning"],
  "keywords": ["AI", "machine learning"],
  "limit": 50,
  "date_from": "2025-08-01T00:00:00Z",
  "date_to": "2025-09-01T00:00:00Z"
}
```

## Collection Jobs

### 1. Create Collection Job
```http
POST /api/collect/jobs
Authorization: Bearer {JWT_TOKEN}
Content-Type: application/json

{
  "subreddits": ["python", "django", "flask"],
  "sort_types": ["hot"],
  "time_filters": ["week"],
  "post_limit": 100,
  "comment_limit": 50,
  "max_comment_depth": 3,
  "keywords": ["API", "framework"],
  "min_score": 10,
  "exclude_nsfw": true,
  "anonymize_users": true
}
```

**Response:**
```json
{
  "id": 123,
  "job_id": "8d4cfc54-3b0f-41ba-90b1-6ee4a36ae2d0",
  "status": "pending",
  "progress": 0,
  "total_expected": 100,
  "collected_posts": 0,
  "collected_comments": 0,
  "created_at": "2025-09-02T12:00:00Z",
  "subreddits": ["python", "django", "flask"],
  "post_limit": 100
}
```

### 2. Get Collection Job Status
```http
GET /api/collect/jobs/{job_id}
Authorization: Bearer {JWT_TOKEN}
```

### 3. List All Collection Jobs
```http
GET /api/collect/jobs?status=completed&page=1&per_page=20
Authorization: Bearer {JWT_TOKEN}
```

### 4. Cancel Collection Job
```http
POST /api/collect/jobs/{job_id}/cancel
Authorization: Bearer {JWT_TOKEN}
```

## Data Querying & Analytics

### 1. Get Data Summary
```http
GET /api/data/summary?job_id={job_id}
Authorization: Bearer {JWT_TOKEN}
```

**Response:**
```json
{
  "total_posts": 150,
  "total_comments": 2500,
  "date_range": {
    "earliest": "2025-08-15T10:30:00Z",
    "latest": "2025-09-02T16:45:00Z"
  },
  "subreddit_breakdown": {
    "python": {"posts": 75, "comments": 1200},
    "django": {"posts": 45, "comments": 800}, 
    "flask": {"posts": 30, "comments": 500}
  },
  "top_keywords": ["API", "tutorial", "beginner", "framework"],
  "average_score": 28.5,
  "engagement_rate": 0.85
}
```

### 2. Get Posts with Filters
```http
GET /api/data/posts?job_id={job_id}&subreddit=python&min_score=50&limit=20&offset=0
Authorization: Bearer {JWT_TOKEN}
```

### 3. Get Comments with Filters  
```http
GET /api/data/comments?job_id={job_id}&min_score=10&limit=50
Authorization: Bearer {JWT_TOKEN}
```

### 4. Get Advanced Analytics
```http
GET /api/data/analytics?job_id={job_id}
Authorization: Bearer {JWT_TOKEN}
```

**Response:**
```json
{
  "sentiment_analysis": {
    "positive": 45.2,
    "neutral": 38.1, 
    "negative": 16.7
  },
  "engagement_trends": [
    {"date": "2025-08-15", "posts": 12, "avg_score": 25.3},
    {"date": "2025-08-16", "posts": 18, "avg_score": 31.2}
  ],
  "top_authors": [
    {"username": "python_expert", "posts": 8, "total_score": 450},
    {"username": "django_dev", "posts": 6, "total_score": 380}
  ],
  "keyword_frequency": {
    "API": 45,
    "tutorial": 32,
    "beginner": 28
  }
}
```

## Data Export

### 1. Get Export Formats
```http
GET /api/export/formats
Authorization: Bearer {JWT_TOKEN}
```

**Response:**
```json
{
  "formats": ["csv", "json", "jsonl", "parquet"],
  "descriptions": {
    "csv": "Comma-separated values for Excel/spreadsheet analysis",
    "json": "JavaScript Object Notation for web applications",
    "jsonl": "JSON Lines format for streaming/big data processing", 
    "parquet": "Columnar format optimized for analytics"
  }
}
```

### 2. Export Posts
```http
POST /api/export/posts/{format}
Authorization: Bearer {JWT_TOKEN}
Content-Type: application/json

{
  "job_id": "8d4cfc54-3b0f-41ba-90b1-6ee4a36ae2d0",
  "filters": {
    "subreddit": "python",
    "min_score": 20,
    "date_from": "2025-08-01T00:00:00Z"
  },
  "fields": ["title", "score", "num_comments", "created_utc", "subreddit"]
}
```

**Response:** File download or download URL

### 3. Export Comments
```http
POST /api/export/comments/{format}
Authorization: Bearer {JWT_TOKEN}
Content-Type: application/json

{
  "job_id": "8d4cfc54-3b0f-41ba-90b1-6ee4a36ae2d0",
  "include_post_context": true
}
```

## Sentiment Analysis

### 1. Get Sentiment Status
```http
GET /api/sentiment/status
Authorization: Bearer {JWT_TOKEN}
```

**Response:**
```json
{
  "service_available": true,
  "model": "llama-3.1-8b-instruct",
  "provider": "OpenRouter",
  "processed_today": 1250,
  "daily_limit": 5000
}
```

### 2. Analyze Custom Text
```http
POST /api/sentiment/analyze
Authorization: Bearer {JWT_TOKEN}
Content-Type: application/json

{
  "texts": [
    "This Python framework is amazing for web development!",
    "I'm frustrated with the documentation quality.",
    "The new features are okay, nothing special."
  ]
}
```

**Response:**
```json
{
  "results": [
    {"text": "This Python framework...", "sentiment": "positive", "score": 0.85, "confidence": 0.92},
    {"text": "I'm frustrated...", "sentiment": "negative", "score": -0.72, "confidence": 0.88},
    {"text": "The new features...", "sentiment": "neutral", "score": 0.15, "confidence": 0.76}
  ]
}
```

## Frontend UI/UX Recommendations

### Dashboard Layout
```javascript
// Suggested dashboard sections
const DASHBOARD_SECTIONS = {
  overview: {
    title: "Analytics Overview",
    widgets: ["total_posts", "sentiment_pie_chart", "engagement_trends", "recent_jobs"]
  },
  collection: {
    title: "Data Collection", 
    widgets: ["create_job_form", "active_jobs_list", "job_progress_bars"]
  },
  analytics: {
    title: "Deep Analytics",
    widgets: ["keyword_cloud", "subreddit_comparison", "temporal_analysis", "top_content"]
  },
  export: {
    title: "Data Export",
    widgets: ["export_builder", "download_history", "format_selector"]
  }
}
```

### Recommended UI Components

1. **Job Progress Component**
   - Real-time progress bars
   - Status badges (pending, running, completed, failed)
   - ETA estimation
   - Cancel/retry buttons

2. **Analytics Visualization**
   - Interactive charts (Chart.js, D3.js, or Recharts)
   - Sentiment analysis pie charts
   - Time-series engagement graphs
   - Word clouds for keywords
   - Heatmaps for subreddit activity

3. **Collection Job Builder**
   - Multi-select subreddit picker
   - Date range selector with presets
   - Keyword input with suggestions
   - Advanced filter toggles
   - Preview mode showing expected results

4. **Data Table Components**
   - Sortable columns
   - Infinite scroll or pagination
   - Search and filter bars
   - Bulk selection for exports
   - Expandable rows for comments

5. **Export Interface**
   - Format selection with previews
   - Filter builder interface
   - Field selection checkboxes
   - Download progress indicators

### Color Scheme & Branding
```css
:root {
  --primary-color: #FF4500; /* Reddit orange */
  --secondary-color: #0079D3; /* Reddit blue */
  --success-color: #46D160;
  --warning-color: #FFB000;
  --error-color: #FF3333;
  --neutral-color: #878A8C;
  
  --background-primary: #FFFFFF;
  --background-secondary: #F6F7F8;
  --text-primary: #1A1A1B;
  --text-secondary: #787C7E;
}
```

### State Management Suggestions
```javascript
// Recommended Redux/Zustand store structure
const STORE_STRUCTURE = {
  auth: {
    user: null,
    token: null,
    isAuthenticated: false
  },
  jobs: {
    active: [],
    completed: [],
    loading: false
  },
  analytics: {
    summary: null,
    charts: {},
    loading: false
  },
  subscription: {
    tier: "free",
    usage: {},
    limits: {}
  }
}
```

### API Integration Patterns
```javascript
// Suggested API service structure
class TrenditAPI {
  constructor(baseURL, authToken) {
    this.baseURL = baseURL;
    this.authToken = authToken;
  }
  
  // Authentication
  async login(credentials) { /* ... */ }
  async register(userData) { /* ... */ }
  
  // Collection Jobs
  async createJob(jobConfig) { /* ... */ }
  async getJobStatus(jobId) { /* ... */ }
  async listJobs(filters) { /* ... */ }
  
  // Analytics
  async getAnalytics(jobId) { /* ... */ }
  async getSentimentAnalysis(jobId) { /* ... */ }
  
  // Export
  async exportData(jobId, format, options) { /* ... */ }
}
```

## Error Handling

All endpoints may return these standard error responses:

```json
{
  "detail": "Error message description",
  "error_code": "INVALID_REQUEST",
  "status_code": 400
}
```

Common status codes:
- 400: Bad Request (validation errors)
- 401: Unauthorized (invalid/missing token)
- 403: Forbidden (subscription limits exceeded)
- 404: Not Found (resource doesn't exist)
- 429: Rate Limited (too many requests)
- 500: Internal Server Error

## WebSocket Real-time Updates (Future Enhancement)

For real-time job progress updates:
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/jobs/{job_id}');
ws.onmessage = (event) => {
  const update = JSON.parse(event.data);
  // Update UI with real-time progress
  updateJobProgress(update.job_id, update.progress, update.status);
};
```

This comprehensive specification provides everything needed to build a modern, beautiful frontend for the Trendit Reddit analytics platform with full CRUD operations, real-time updates, and rich data visualizations.