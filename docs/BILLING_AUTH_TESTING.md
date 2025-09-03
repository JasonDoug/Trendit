# Billing, Authentication & Subscription Gating Testing Guide

This guide provides comprehensive curl examples for testing Trendit's authentication system, subscription gating, and Paddle billing integration.

## Quick Setup

1. **Start the server:**
```bash
cd backend
uvicorn main:app --reload --port 8000
```

2. **Get your Bearer token** (follow the authentication flow below)
3. **Replace `YOUR_TOKEN_HERE`** in all examples with your actual JWT token

---

## 🔐 Authentication System Testing

### 1. User Registration
```bash
# Register a new user account
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com", 
    "password": "securepassword123"
  }' | python -m json.tool
```

Expected response:
```json
{
  "id": 1,
  "email": "test@example.com",
  "username": "testuser",
  "is_active": true,
  "subscription_status": "inactive",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### 2. User Login
```bash
# Login to get JWT Bearer token
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com", 
    "password": "securepassword123"
  }' | python -m json.tool
```

Expected response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}
```

### 3. API Key Management
```bash
# Create an API key (requires JWT token)
curl -X POST "http://localhost:8000/auth/api-keys" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Test API Key"
  }' | python -m json.tool

# List all API keys
curl -X GET "http://localhost:8000/auth/api-keys" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE" | python -m json.tool

# Delete an API key
curl -X DELETE "http://localhost:8000/auth/api-keys/1" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE" | python -m json.tool
```

---

## 💰 Billing System Testing

### 1. Get Subscription Tiers (No Auth Required)
```bash
# View available subscription tiers and pricing
curl -X GET "http://localhost:8000/api/billing/tiers" | python -m json.tool
```

### 2. Get Current Subscription Status
```bash
# Check your subscription status, usage limits, and current consumption
curl -X GET "http://localhost:8000/api/billing/subscription/status" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" | python -m json.tool
```

Expected response:
```json
{
  "tier": "free",
  "status": "inactive",
  "limits": {
    "api_calls_per_month": 100,
    "exports_per_month": 5,
    "sentiment_analysis_per_month": 50,
    "data_retention_days": 30
  },
  "current_usage": {
    "api_call": 0,
    "export": 0,
    "sentiment_analysis": 0
  },
  "usage_percentage": {
    "api_call": 0.0,
    "export": 0.0,
    "sentiment_analysis": 0.0
  }
}
```

### 3. Create Checkout Session for Subscription
```bash
# Create Paddle checkout for Pro tier
curl -X POST "http://localhost:8000/api/billing/checkout/create" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "tier": "pro",
    "trial_days": 14,
    "success_url": "https://example.com/success",
    "cancel_url": "https://example.com/cancel"
  }' | python -m json.tool

# Create Enterprise checkout with no trial
curl -X POST "http://localhost:8000/api/billing/checkout/create" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "tier": "enterprise"
  }' | python -m json.tool
```

### 4. Upgrade/Downgrade Subscription
```bash
# Upgrade to Enterprise tier
curl -X POST "http://localhost:8000/api/billing/subscription/upgrade" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "new_tier": "enterprise"
  }' | python -m json.tool

# Downgrade to Free tier (cancellation)
curl -X POST "http://localhost:8000/api/billing/subscription/upgrade" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "new_tier": "free"
  }' | python -m json.tool
```

### 5. Cancel Subscription
```bash
# Cancel subscription at end of billing period
curl -X POST "http://localhost:8000/api/billing/subscription/cancel" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" | python -m json.tool
```

### 6. Get Usage Analytics
```bash
# Get 30-day usage analytics
curl -X GET "http://localhost:8000/api/billing/usage/analytics" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" | python -m json.tool

# Get 7-day usage analytics
curl -X GET "http://localhost:8000/api/billing/usage/analytics?days=7" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" | python -m json.tool
```

### 7. Billing Health Check
```bash
# Check billing service health
curl -X GET "http://localhost:8000/api/billing/health" | python -m json.tool
```

---

## 🚧 Subscription Gating Testing

### 1. Test API Call Limits
```bash
# This will track usage for "api_calls" type
curl -X POST "http://localhost:8000/api/collect/jobs" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "scenario_id": 1,
    "subreddits": ["python"],
    "keywords": ["fastapi"],
    "post_limit": 10
  }' | python -m json.tool
```

### 2. Test Export Limits
```bash
# This will track usage for "exports" type
curl -X GET "http://localhost:8000/api/export/posts/csv/job123" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"

# You can also test other export formats
curl -X GET "http://localhost:8000/api/export/posts/json/job123" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### 3. Test Sentiment Analysis Limits
```bash
# Single text sentiment analysis - tracks "sentiment_analysis" usage
curl -X POST "http://localhost:8000/api/sentiment/analyze" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "I love this new feature! It works perfectly."
  }' | python -m json.tool

# Batch sentiment analysis - tracks multiple units
curl -X POST "http://localhost:8000/api/sentiment/analyze-batch" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "texts": [
      "This is amazing!",
      "I hate this feature.",
      "It is okay, nothing special."
    ]
  }' | python -m json.tool
```

### 4. Test Usage Limit Enforcement

**For Free Tier users (100 API calls/month):**
```bash
# Make multiple API calls to test rate limiting
for i in {1..5}; do
  echo "API Call #$i"
  curl -X POST "http://localhost:8000/api/collect/jobs" \
    -H "Authorization: Bearer YOUR_TOKEN_HERE" \
    -H "Content-Type: application/json" \
    -d '{
      "scenario_id": 1,
      "subreddits": ["test"],
      "post_limit": 1
    }' | python -m json.tool
  echo "---"
done
```

When you exceed limits, you'll get:
```json
{
  "detail": "Usage limit exceeded. 101/100 api_calls used this month. Upgrade your plan for higher limits."
}
```

---

## 🔍 Testing Usage Tracking Headers

Look for these response headers on gated endpoints:
- `X-RateLimit-Limit`: Your monthly limit
- `X-RateLimit-Remaining`: Remaining usage this month  
- `X-RateLimit-Reset`: Timestamp when limits reset
- `X-User-Tier`: Your current subscription tier

```bash
# View headers with verbose output
curl -v -X POST "http://localhost:8000/api/sentiment/analyze" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"text": "Test message"}' | python -m json.tool
```

---

## 🧪 Complete Test Sequence

Here's a complete test sequence to verify all systems work together:

```bash
# 1. Register and login
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username": "tester", "email": "tester@example.com", "password": "password123"}'

curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "tester@example.com", "password": "password123"}'
# Copy the access_token from response

# 2. Check subscription status (should be free tier)
curl -X GET "http://localhost:8000/api/billing/subscription/status" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"

# 3. Test an API call (should work within free limits)
curl -X POST "http://localhost:8000/api/sentiment/analyze" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"text": "Testing the sentiment analysis"}'

# 4. Check updated usage
curl -X GET "http://localhost:8000/api/billing/subscription/status" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"

# 5. View usage analytics
curl -X GET "http://localhost:8000/api/billing/usage/analytics" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## 📊 Expected Free Tier Limits

- **API Calls**: 100 per month
- **Exports**: 5 per month  
- **Sentiment Analysis**: 50 per month
- **Data Retention**: 30 days

## 🎯 Pro Tier Limits ($29/month)

- **API Calls**: 10,000 per month
- **Exports**: 100 per month
- **Sentiment Analysis**: 2,000 per month  
- **Data Retention**: 1 year

## 🚀 Enterprise Tier Limits ($299/month)

- **API Calls**: 100,000 per month
- **Exports**: 1,000 per month
- **Sentiment Analysis**: 20,000 per month
- **Data Retention**: Unlimited

---

## 🔧 Troubleshooting

### Authentication Errors
- **401 Unauthorized**: Check your Bearer token format and expiration
- **403 Forbidden**: Token is valid but user lacks permission
- **422 Validation Error**: Check request body format

### Rate Limiting Errors  
- **429 Too Many Requests**: You've exceeded your tier limits
- Check `X-RateLimit-*` headers for limit information
- Upgrade your subscription or wait for limit reset

### Billing Errors
- **503 Service Unavailable**: Paddle billing not configured
- **402 Payment Required**: Active subscription required but not found
- **404 Not Found**: No subscription record exists

### Common Issues
- Ensure server is running on port 8000
- Replace `YOUR_TOKEN_HERE` with actual JWT token
- Check Content-Type headers for JSON requests
- Verify environment variables are set (.env file)

---

*This guide covers the complete authentication, billing, and subscription gating system. All endpoints include proper usage tracking and rate limiting according to subscription tiers.*