# Comprehensive SaaS Endpoint Gating Strategy

## Current Problem: Value Leakage

**Only 1 out of 32 valuable endpoints is currently gated!** This means users can:
- ❌ Export data for free (`/api/export/*`)
- ❌ Query stored data for free (`/api/data/*`)  
- ❌ Run analytics for free (`/api/data/analytics/*`)
- ❌ Use scenarios for free (`/api/scenarios/*`)
- ❌ Access sentiment analysis for free (`/api/sentiment/*`)
- ❌ Manage collection jobs for free (`/api/collect/jobs/{id}`)

**Result:** Users can get full value without paying!

## Comprehensive Gating Plan

### Tier 1: Free (Public Access)
**Business Purpose:** Lead generation, account creation, API exploration

```
✅ /health                    # System health check
✅ /                          # API information  
✅ /docs                      # API documentation
✅ /redoc                     # Alternative docs
✅ /auth/register             # Account creation
✅ /auth/login                # Authentication
```

### Tier 2: Authenticated Required
**Business Purpose:** Account management, non-premium features

```
🔑 /auth/api-keys/*           # API key management (requires JWT)
```

### Tier 3: Active Subscription Required (Premium)
**Business Purpose:** Core paid features - ALL VALUE-GENERATING ENDPOINTS

#### Data Collection & Management
```
💰 POST /api/collect/jobs                    # Create collection job
💰 GET  /api/collect/jobs                    # List user's jobs  
💰 GET  /api/collect/jobs/{id}               # Get job details
💰 GET  /api/collect/jobs/{id}/status        # Get job status
💰 POST /api/collect/jobs/{id}/cancel        # Cancel job
💰 DELETE /api/collect/jobs/{id}             # Delete job
```

#### Data Querying & Access  
```
💰 POST /api/data/posts                      # Query stored posts
💰 POST /api/data/comments                   # Query stored comments
💰 GET  /api/data/analytics/{job_id}         # Get analytics
💰 GET  /api/data/summary                    # Data summary
💰 GET  /api/data/posts/recent               # Recent posts
💰 GET  /api/data/posts/top                  # Top posts
```

#### Data Export (High Value!)
```
💰 POST /api/export/posts/{format}          # Export posts
💰 POST /api/export/comments/{format}       # Export comments  
💰 GET  /api/export/job/{job_id}/{format}   # Export job results
💰 GET  /api/export/formats                 # Available formats
```

#### Reddit Scenarios (Live API Access)
```
💰 GET /api/scenarios/1/subreddit-keyword-search
💰 GET /api/scenarios/2/trending-multi-subreddits  
💰 GET /api/scenarios/3/top-posts-all
💰 GET /api/scenarios/4/most-popular-today
💰 GET /api/scenarios/comments/top-by-criteria
💰 GET /api/scenarios/users/top-by-activity
💰 GET /api/scenarios/examples
```

#### Query API (Live Reddit Access)
```
💰 POST /api/query/posts                    # Live Reddit post queries
💰 POST /api/query/comments                 # Live Reddit comment queries
💰 POST /api/query/users                    # Live Reddit user queries
💰 GET  /api/query/posts/simple             # Simple post queries
💰 GET  /api/query/examples                 # Query examples
```

#### AI-Powered Sentiment Analysis
```
💰 GET  /api/sentiment/status               # Sentiment service status
💰 POST /api/sentiment/analyze              # Analyze single text
💰 POST /api/sentiment/analyze-batch        # Batch analysis
💰 GET  /api/sentiment/test                 # Test sentiment analysis
```

## Implementation Strategy

### Phase 1: Immediate Gating (High Priority)
Gate the highest-value endpoints first:

1. **Export endpoints** - Users getting data for free
2. **Data query endpoints** - Accessing stored data for free
3. **Scenarios endpoints** - Live Reddit API access for free

### Phase 2: Complete Coverage
Gate remaining endpoints:

4. **Collection management endpoints** - Job management
5. **Sentiment analysis endpoints** - AI features
6. **Query API endpoints** - Live Reddit queries

### Implementation Method

#### Add Subscription Gate to Each Endpoint
```python
# BEFORE (vulnerable to free access)
@router.post("/posts/{format}")
async def export_posts(
    format: str,
    request: ExportPostsRequest,
    db: Session = Depends(get_db)
):

# AFTER (subscription protected) 
@router.post("/posts/{format}")
async def export_posts(
    format: str,
    request: ExportPostsRequest, 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_active_subscription)  # 🔒 GATE
):
```

#### Bulk Gating Script
```python
# Apply to multiple endpoints efficiently
SUBSCRIPTION_PROTECTED_ENDPOINTS = [
    # Export API
    "export.py:export_posts",
    "export.py:export_comments", 
    "export.py:export_job_results",
    "export.py:get_export_formats",
    
    # Data API  
    "data.py:query_posts",
    "data.py:query_comments",
    "data.py:get_analytics",
    "data.py:get_data_summary",
    "data.py:get_recent_posts",
    "data.py:get_top_posts",
    
    # Scenarios API
    "scenarios.py:*",  # All scenario endpoints
    
    # Query API
    "query.py:*",  # All query endpoints
    
    # Sentiment API
    "sentiment.py:*",  # All sentiment endpoints
    
    # Collection Management
    "collect.py:get_collection_job",
    "collect.py:get_job_status", 
    "collect.py:list_jobs",
    "collect.py:cancel_job",
    "collect.py:delete_job"
]
```

## Business Impact Analysis

### Current Revenue Leakage
```
User Journey WITHOUT Proper Gating:
1. Register free account ✅
2. Create API key ✅  
3. Run scenarios to get Reddit data ❌ (Should be paid)
4. Export data in multiple formats ❌ (Should be paid)
5. Use sentiment analysis ❌ (Should be paid)
6. Query and analyze data ❌ (Should be paid)

Result: User gets full value for $0
```

### After Comprehensive Gating  
```
User Journey WITH Proper Gating:
1. Register free account ✅
2. Try to access valuable endpoints → 402 Payment Required 
3. Subscribe to access premium features 💰
4. Get API key and access full functionality ✅

Result: User must pay for value
```

### Revenue Protection

#### Monthly Subscription Scenarios
- **Basic Plan ($29/month)** - Limited API calls, basic export
- **Pro Plan ($99/month)** - Higher limits, all export formats  
- **Enterprise ($299/month)** - Unlimited usage, priority support

#### Usage-Based Pricing
- **Collection Jobs:** $0.10 per job
- **Data Export:** $0.001 per post exported
- **Sentiment Analysis:** $0.01 per text analyzed
- **Live API Queries:** $0.001 per query

## Free Tier Strategy

### What Remains Free (Lead Generation)
```
✅ Account creation and management
✅ API documentation and exploration  
✅ Basic health checks and system info
✅ Sample data preview (first 10 results)
```

### Free Tier Limits (Freemium Model)
```python
# Alternative: Limited free usage
async def require_subscription_or_free_limit(
    user: User = Depends(get_current_user_from_api_key),
    db: Session = Depends(get_db)
) -> User:
    """Allow limited free usage or require subscription"""
    
    if user.subscription_status == SubscriptionStatus.ACTIVE:
        return user  # Unlimited access
    
    # Check free tier limits
    monthly_usage = get_user_monthly_usage(user.id, db)
    
    if monthly_usage.api_calls >= FREE_TIER_LIMIT:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f"Free tier limit exceeded ({FREE_TIER_LIMIT} calls/month). Upgrade to continue."
        )
    
    # Increment usage counter
    increment_user_usage(user.id, db)
    return user
```

## Implementation Priority

### Immediate (This Sprint)
1. **Export endpoints** - Highest value leakage
2. **Data query endpoints** - Core stored data access
3. **Scenarios endpoints** - Live Reddit API access

### Next Sprint  
4. **Collection management endpoints**
5. **Sentiment analysis endpoints** 
6. **Query API endpoints**

### Error Messages for Gated Endpoints
```python
# Consistent error messaging
SUBSCRIPTION_REQUIRED_MESSAGE = {
    "error": "subscription_required",
    "message": "This feature requires an active subscription",
    "upgrade_url": "https://trendit.com/pricing",
    "contact": "support@trendit.com"
}
```

## Testing Strategy

### Verify All Endpoints Gated
```bash
# Test script to verify gating
for endpoint in $PREMIUM_ENDPOINTS; do
    response=$(curl -s -o /dev/null -w "%{http_code}" \
        -H "Authorization: Bearer $INACTIVE_API_KEY" \
        "$endpoint")
    
    if [ "$response" != "402" ]; then
        echo "❌ LEAK: $endpoint returned $response (should be 402)"
    else
        echo "✅ GATED: $endpoint properly protected"
    fi
done
```

## Documentation Updates Needed

### Update API Documentation
```yaml
# All premium endpoints need this note:
security:
  - ApiKeyAuth: []
  - SubscriptionRequired: []
  
responses:
  402:
    description: "Active subscription required"
    content:
      application/json:
        schema:
          type: object
          properties:
            detail:
              type: string
              example: "Active subscription required to access this endpoint"
```

---

**TLDR: We need to gate 28+ additional endpoints immediately to prevent massive revenue leakage!**