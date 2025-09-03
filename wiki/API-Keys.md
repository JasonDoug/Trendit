# API Keys in Trendit

API keys are a fundamental authentication mechanism in Trendit's SaaS platform, enabling secure programmatic access to all data collection and analysis services.

## 🔑 What are API Keys?

API keys in Trendit are long-lived authentication tokens that allow applications, scripts, and automated systems to access the platform without requiring interactive user login. Each API key is:

- **User-specific**: Tied to a specific user account and inherits their subscription permissions
- **Named**: Each key has a descriptive name for easy identification
- **Trackable**: Usage is monitored with last-used timestamps
- **Revocable**: Can be individually deleted without affecting other keys
- **Secure**: Stored as hashed values in the database (similar to passwords)

## 🎯 Primary Use Cases

### 1. **Automated Data Collection**
Perfect for scheduled jobs that collect Reddit data at regular intervals:

```bash
#!/bin/bash
# Daily data collection script
curl -X POST "https://api.trendit.com/api/collect/jobs" \
  -H "Authorization: Bearer tk_your_api_key_here" \
  -H "Content-Type: application/json" \
  -d '{
    "subreddits": ["technology", "programming"],
    "sort_types": ["hot", "top"],
    "post_limit": 100,
    "keywords": ["AI", "machine learning"]
  }'
```

### 2. **Third-Party Integrations**
Enable other applications to access your Trendit data:

```python
# Python application using Trendit API
import requests

API_KEY = "tk_your_api_key_here"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

# Export data to external system
response = requests.post(
    "https://api.trendit.com/api/export/posts/json",
    headers=HEADERS,
    json={"subreddits": ["datascience"], "min_score": 50}
)
```

### 3. **Development & Testing Environments**
Separate API keys for different environments:

- **Production**: `tk_prod_abc123...` - Live data collection
- **Staging**: `tk_staging_def456...` - Testing new features
- **Development**: `tk_dev_ghi789...` - Local development work

### 4. **CI/CD Pipeline Integration**
Automated testing and deployment workflows:

```yaml
# GitHub Actions example
name: Data Quality Check
on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours
  
jobs:
  test-data-quality:
    runs-on: ubuntu-latest
    steps:
      - name: Test Sentiment Analysis
        run: |
          curl -X POST "https://api.trendit.com/api/sentiment/analyze" \
            -H "Authorization: Bearer ${{ secrets.TRENDIT_API_KEY }}" \
            -H "Content-Type: application/json" \
            -d '{"text": "Test sentiment analysis functionality"}'
```

## 🆚 JWT Tokens vs API Keys

Understanding when to use each authentication method:

| Aspect | JWT Tokens | API Keys |
|--------|------------|----------|
| **Lifespan** | Short (30 minutes) | Long (until revoked) |
| **Use Case** | Interactive user sessions | Automated/programmatic access |
| **Security Model** | Session-based | Application-based |
| **Renewal Required** | Yes, frequent | No |
| **Best For** | Web apps, mobile apps | Scripts, integrations, servers |

### Example: Web App Login Flow
```bash
# 1. User logs in via web interface
curl -X POST "https://api.trendit.com/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@company.com", "password": "password123"}'

# 2. Receives JWT token for web session
# 3. Uses JWT to create API key for automated systems
curl -X POST "https://api.trendit.com/auth/api-keys" \
  -H "Authorization: Bearer jwt_token_here" \
  -d '{"name": "Company Data Collector"}'

# 4. Application uses API key for long-term access
```

## 🔧 Managing API Keys

### Creating API Keys

1. **Authenticate with JWT token** (from login)
2. **Create named API key**:

```bash
curl -X POST "https://api.trendit.com/auth/api-keys" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Production Data Pipeline"
  }' | python -m json.tool
```

3. **Response includes the key** (⚠️ **shown only once**):
```json
{
  "id": 1,
  "name": "Production Data Pipeline",
  "key": "tk_abc123def456ghi789...",
  "created_at": "2024-01-01T12:00:00Z",
  "expires_at": null
}
```

### Listing Your API Keys

```bash
curl -X GET "https://api.trendit.com/auth/api-keys" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" | python -m json.tool
```

Response shows **all keys except the actual key values**:
```json
[
  {
    "id": 1,
    "name": "Production Data Pipeline",
    "is_active": true,
    "created_at": "2024-01-01T12:00:00Z",
    "last_used_at": "2024-01-01T14:30:00Z"
  },
  {
    "id": 2,
    "name": "Development Testing",
    "is_active": true,
    "created_at": "2024-01-01T13:00:00Z",
    "last_used_at": null
  }
]
```

### Revoking API Keys

```bash
curl -X DELETE "https://api.trendit.com/auth/api-keys/1" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## 🔒 Security Best Practices

### 1. **Key Storage**
```bash
# ❌ DON'T: Store in code or version control
API_KEY = "tk_abc123def456..."

# ✅ DO: Use environment variables
API_KEY = os.getenv("TRENDIT_API_KEY")

# ✅ DO: Use secrets management
API_KEY = get_secret("trendit/api-key")
```

### 2. **Key Rotation**
- **Regular rotation**: Create new keys periodically
- **Immediate revocation**: Remove compromised keys instantly
- **Monitoring**: Check "last used" timestamps for unusual activity

### 3. **Principle of Least Privilege**
- **Environment-specific keys**: Separate keys for prod/staging/dev
- **Application-specific keys**: Different keys for different services
- **Team-specific keys**: Individual keys for different team members

### 4. **Monitoring & Auditing**
```bash
# Check your current usage and key activity
curl -X GET "https://api.trendit.com/api/billing/usage/analytics" \
  -H "Authorization: Bearer tk_your_api_key" | python -m json.tool
```

## 🏢 Enterprise Features

### Subscription Integration
API keys automatically inherit your subscription tier limits:

- **Free Tier**: 100 API calls/month per key
- **Pro Tier**: 10,000 API calls/month per key  
- **Enterprise Tier**: 100,000 API calls/month per key

### Usage Tracking
Every API call is tracked for:
- **Billing accuracy**: Correct usage attribution
- **Rate limiting**: Tier-based enforcement
- **Analytics**: Usage patterns and trends
- **Security**: Anomaly detection

### Team Management
- **Multiple keys per user**: Organize by project/environment
- **Usage attribution**: All usage tied to the key owner's subscription
- **Centralized billing**: Single subscription covers all user's API keys

## 📊 Real-World Examples

### Data Science Pipeline
```python
import requests
import pandas as pd
from datetime import datetime, timedelta

class TrenditCollector:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.trendit.com"
        self.headers = {"Authorization": f"Bearer {api_key}"}
    
    def collect_daily_data(self, subreddits):
        """Collect daily Reddit data for analysis"""
        job_data = {
            "subreddits": subreddits,
            "sort_types": ["hot", "top"],
            "time_filters": ["day"],
            "post_limit": 100,
            "comment_limit": 50
        }
        
        response = requests.post(
            f"{self.base_url}/api/collect/jobs",
            headers=self.headers,
            json=job_data
        )
        return response.json()
    
    def export_sentiment_analysis(self, job_id):
        """Export collected data with sentiment scores"""
        response = requests.get(
            f"{self.base_url}/api/export/job/{job_id}/json",
            headers=self.headers
        )
        return response.json()

# Usage
collector = TrenditCollector(os.getenv("TRENDIT_API_KEY"))
job = collector.collect_daily_data(["MachineLearning", "datascience"])
data = collector.export_sentiment_analysis(job["job_id"])
```

### Monitoring Dashboard
```bash
#!/bin/bash
# Check API usage and limits
echo "=== Trendit API Usage Report ==="
echo "Generated: $(date)"
echo

# Get subscription status
curl -s -X GET "https://api.trendit.com/api/billing/subscription/status" \
  -H "Authorization: Bearer $TRENDIT_API_KEY" | \
  jq -r '"Tier: " + .tier + " | Status: " + .status'

# Get usage analytics
curl -s -X GET "https://api.trendit.com/api/billing/usage/analytics?days=7" \
  -H "Authorization: Bearer $TRENDIT_API_KEY" | \
  jq '.total_usage_this_period'

echo "=== End Report ==="
```

## 🚨 Troubleshooting

### Common Issues

**❌ 401 Unauthorized**
```bash
# Check API key format - should start with 'tk_'
echo $TRENDIT_API_KEY | grep "^tk_"

# Verify key is still active
curl -X GET "https://api.trendit.com/auth/api-keys" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**❌ 429 Too Many Requests**
```bash
# Check your usage limits
curl -X GET "https://api.trendit.com/api/billing/subscription/status" \
  -H "Authorization: Bearer tk_your_api_key"
```

**❌ Key Not Found**
- Key may have been revoked
- Check if user account is still active
- Verify the key was copied correctly (no extra spaces/characters)

### Best Practices Summary

1. **🔐 Never commit API keys to version control**
2. **🔄 Rotate keys regularly (quarterly recommended)**
3. **📊 Monitor usage patterns for anomalies**
4. **🏷️ Use descriptive names for easy identification**
5. **🗑️ Revoke unused keys immediately**
6. **🚨 Set up alerts for unusual usage patterns**
7. **📝 Document which keys are used where**
8. **🔒 Store keys in secure secrets management systems**

## 📚 Related Documentation

- [Authentication Overview](Authentication-Overview.md)
- [Subscription Management](Subscription-Management.md)
- [Rate Limiting & Usage Tracking](Rate-Limiting.md)
- [Security Best Practices](Security-Best-Practices.md)
- [Billing Integration](Billing-Integration.md)

---

*API keys are the backbone of programmatic access to Trendit. Following these guidelines ensures secure, reliable, and efficient integration with your data collection workflows.*