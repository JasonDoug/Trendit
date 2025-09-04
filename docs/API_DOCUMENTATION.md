# Trendit API Documentation

This directory contains comprehensive API documentation and testing tools for the Trendit Reddit Data Collection and Analysis Platform.

## 📁 Files Overview

| File | Description |
|------|-------------|
| `openapi.json` | OpenAPI 3.0 specification in JSON format |
| `openapi.yaml` | OpenAPI 3.0 specification in YAML format |
| `Trendit_API.postman_collection.json` | Complete Postman collection with all endpoints |
| `Trendit_API.postman_environment.json` | Postman environment variables |
| `TRENDIT_FRONTEND_API_SPECIFICATION.md` | Frontend developer guide |

## 🚀 Getting Started

### Using OpenAPI Specs

#### View Interactive Documentation
1. **Swagger UI**: Navigate to `http://localhost:8000/docs` (when server is running)
2. **ReDoc**: Navigate to `http://localhost:8000/redoc` (alternative documentation)

#### Import into API Tools
- **Postman**: File → Import → Upload `openapi.json` or `openapi.yaml`
- **Insomnia**: Import → From File → Select `openapi.json`
- **VS Code**: Use REST Client extension with OpenAPI specs
- **Code Generation**: Use with Swagger Codegen, OpenAPI Generator, etc.

### Using Postman Collection

#### Import Collection & Environment
1. Open Postman
2. Import `Trendit_API.postman_collection.json`
3. Import `Trendit_API.postman_environment.json`
4. Set environment to "Trendit API Environment"

#### Authentication Flow
1. **Register User** → Creates new account
2. **Login User** → Auto-saves JWT token to environment
3. **Create API Key** → Auto-saves API key to environment
4. All subsequent requests use saved tokens automatically

#### Testing Workflow
```
1. System Health Check ✓
2. Register User ✓
3. Login User ✓ (saves JWT)
4. Create API Key ✓ (saves API key)
5. Create Collection Job ✓ (saves job_id)
6. Monitor Job Progress ✓
7. Query Collected Data ✓
8. Export Data ✓
9. Analyze Sentiment ✓
```

## 🔐 Authentication

The API supports two authentication methods:

### JWT Token Authentication (Recommended)
```bash
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

### API Key Authentication
```bash
Authorization: Bearer tk_DJkdLEPxaBDhtGPz5s6RY3vJni-zdIWXJk27QtBlC7k
```

## 📊 API Endpoints Overview

### Core Categories

#### 🔒 Authentication (`/auth`)
- User registration and login
- JWT token management
- API key creation and management
- User profile access

#### 💰 Billing (`/billing`)
- Subscription management
- Usage tracking
- Paddle payment integration
- Billing history

#### 🔄 Collection Jobs (`/api/collect`)
- Create and manage data collection jobs
- Real-time progress monitoring
- Job cancellation and deletion
- Bulk job operations

#### 📈 Data & Analytics (`/api/data`)
- Query collected posts and comments
- Advanced filtering and sorting
- Statistical summaries
- Analytics generation

#### 📤 Data Export (`/api/export`)
- Multiple format support (CSV, JSON, JSONL, Parquet)
- Custom field selection
- Filtered exports
- Batch processing

#### 🧠 Sentiment Analysis (`/api/sentiment`)
- AI-powered sentiment analysis
- Batch text processing
- Custom text analysis
- Service status monitoring

#### 🎯 Scenarios (`/api/scenarios`)
- Pre-built collection scenarios
- Keyword-based searches
- Trending analysis
- Custom scenario execution

## 💡 Usage Examples

### Quick Start with cURL

```bash
# Health Check
curl http://localhost:8000/health

# Register User
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com", 
    "password": "securepassword123"
  }'

# Login (save the access_token)
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "securepassword123"
  }'

# Create Collection Job (replace YOUR_JWT_TOKEN)
curl -X POST "http://localhost:8000/api/collect/jobs" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "subreddits": ["python"],
    "sort_types": ["hot"],
    "post_limit": 10,
    "comment_limit": 5
  }'
```

### Python SDK Example

```python
import requests

class TrenditAPI:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.token = None
    
    def login(self, username, password):
        response = requests.post(f"{self.base_url}/auth/login", json={
            "username": username,
            "password": password
        })
        self.token = response.json()["access_token"]
        return self.token
    
    def create_job(self, subreddits, **kwargs):
        headers = {"Authorization": f"Bearer {self.token}"}
        data = {"subreddits": subreddits, **kwargs}
        response = requests.post(f"{self.base_url}/api/collect/jobs", 
                               json=data, headers=headers)
        return response.json()

# Usage
api = TrenditAPI()
api.login("testuser", "securepassword123")
job = api.create_job(["python"], post_limit=20, comment_limit=10)
print(f"Created job: {job['job_id']}")
```

### JavaScript/Node.js Example

```javascript
class TrenditAPI {
    constructor(baseURL = 'http://localhost:8000') {
        this.baseURL = baseURL;
        this.token = null;
    }
    
    async login(username, password) {
        const response = await fetch(`${this.baseURL}/auth/login`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({username, password})
        });
        const data = await response.json();
        this.token = data.access_token;
        return this.token;
    }
    
    async createJob(subreddits, options = {}) {
        const response = await fetch(`${this.baseURL}/api/collect/jobs`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${this.token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({subreddits, ...options})
        });
        return response.json();
    }
}

// Usage
const api = new TrenditAPI();
await api.login('testuser', 'securepassword123');
const job = await api.createJob(['python'], {post_limit: 20});
console.log(`Created job: ${job.job_id}`);
```

## 🔧 Development & Testing

### Environment Configuration

| Environment | Base URL |
|-------------|----------|
| Local Development | `http://localhost:8000` |
| Staging | `https://trendit-staging.onrender.com` |
| Production | `https://trendit-api.onrender.com` |

### Testing Checklist

- [ ] Health check passes
- [ ] User registration works
- [ ] Authentication (JWT) works
- [ ] API key creation works
- [ ] Collection job creation works
- [ ] Job progresses and completes
- [ ] Data querying works
- [ ] Export functionality works
- [ ] Sentiment analysis works
- [ ] Error handling is appropriate

### Rate Limits

| Tier | API Calls/Month | Exports/Month | Sentiment Analysis |
|------|-----------------|---------------|-------------------|
| Free | 1,000 | 5 | 100 |
| Pro | 10,000 | 100 | 5,000 |
| Enterprise | Unlimited | Unlimited | Unlimited |

## 🐛 Troubleshooting

### Common Issues

#### 401 Unauthorized
- Check JWT token is valid and not expired
- Ensure Authorization header format: `Bearer {token}`
- Verify user account is active

#### 403 Forbidden
- Check subscription tier limits
- Verify API usage hasn't exceeded monthly limits
- Ensure user has required permissions

#### 429 Rate Limited
- Reduce request frequency
- Implement exponential backoff
- Consider upgrading subscription tier

#### Collection Jobs Stuck
- Check Reddit API credentials
- Verify database connectivity
- Monitor server logs for errors

### Support

- 📧 **Email**: support@trendit.com
- 🐛 **Issues**: GitHub Issues
- 📖 **Documentation**: `/docs` endpoint
- 💬 **Community**: Discord/Slack

## 🚀 Production Deployment

### Environment Variables Required

```bash
# Database
DATABASE_URL=postgresql://user:pass@host:port/dbname

# Reddit API
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=Trendit/1.0 by /u/yourusername

# Security
JWT_SECRET_KEY=your-super-secure-jwt-secret
API_KEY_SALT=your-api-key-salt

# Optional: Billing (Paddle)
PADDLE_API_KEY=your_paddle_api_key
PADDLE_ENVIRONMENT=sandbox|production

# Optional: AI Features
OPENROUTER_API_KEY=your_openrouter_api_key
```

### Deployment Options

1. **Render** (Recommended): Use `deploy-render.sh`
2. **Vercel**: Use `deploy-vercel.sh`
3. **Docker**: Use provided Dockerfile
4. **Manual**: Follow deployment guide

---

## 📝 License

This API documentation is part of the Trendit platform. See the main README for license information.

**Last Updated**: September 2025  
**API Version**: 1.0.0  
**OpenAPI Version**: 3.0.2