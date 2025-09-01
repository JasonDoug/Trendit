# Subscription Gating Implementation Guide

## Overview

This document explains how Trendit implements **subscription-based access control** to gate premium endpoints behind paid subscriptions. The system uses FastAPI dependency injection to enforce subscription requirements at the endpoint level.

## ✅ IMPLEMENTATION COMPLETE

**Status: All 28+ valuable endpoints are now protected with subscription requirements**

### Protected Endpoint Categories

**Export API (4 endpoints)** - High-value data export features
**Data API (6 endpoints)** - Stored data query & analytics  
**Scenarios API (7 endpoints)** - Live Reddit data collection scenarios
**Query API (5 endpoints)** - Live Reddit API access
**Sentiment API (4 endpoints)** - AI-powered sentiment analysis
**Collection Management (6 endpoints)** - Data collection job management

All endpoints now require active subscriptions, eliminating revenue leakage where users previously accessed premium features for free.

## Implementation Architecture

### 1. Dependency Chain
```python
# Authentication & Authorization Dependency Chain
API Request 
    ↓
require_active_subscription()  # Subscription gate
    ↓  
get_current_user_from_api_key()  # API key validation
    ↓
HTTPBearer security  # Extract Bearer token
    ↓
Protected Endpoint Access
```

### 2. Code Implementation

#### Step 1: Authentication Dependencies (`api/auth.py`)
```python
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from models.models import User, APIKey, SubscriptionStatus

# Security scheme for Bearer token extraction
security = HTTPBearer()

async def get_current_user_from_api_key(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Extract user from API key with validation"""
    # Validate API key format (must start with "tk_")
    if not credentials.credentials.startswith("tk_"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key format",
        )
    
    # Hash provided key to compare with stored hash
    key_hash = hashlib.sha256(credentials.credentials.encode()).hexdigest()
    
    # Look up API key in database
    api_key = db.query(APIKey).filter(
        APIKey.key_hash == key_hash,
        APIKey.is_active == True
    ).first()
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )
    
    # Update usage tracking
    api_key.last_used_at = datetime.utcnow()
    db.commit()
    
    # Get associated user
    user = db.query(User).filter(User.id == api_key.user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive",
        )
    
    return user

async def require_active_subscription(
    user: User = Depends(get_current_user_from_api_key)
) -> User:
    """Subscription gate - require ACTIVE subscription status"""
    if user.subscription_status != SubscriptionStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Active subscription required to access this endpoint",
        )
    return user
```

#### Step 2: Protecting the Endpoint (`api/collect.py`)
```python
from api.auth import require_active_subscription
from models.models import User

@router.post("/jobs", response_model=CollectionJobResponse)
async def create_collection_job(
    job_request: CollectionJobRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_active_subscription)  # 🔒 SUBSCRIPTION GATE
):
    """
    Create a new persistent collection job
    
    🔒 PROTECTED: Requires active subscription
    """
    try:
        # Generate unique job ID
        job_id = str(uuid.uuid4())
        
        # Create collection job record - LINKED TO AUTHENTICATED USER
        collection_job = CollectionJob(
            job_id=job_id,
            user_id=current_user.id,  # Associate with paying customer
            subreddits=job_request.subreddits,
            sort_types=[st.value for st in job_request.sort_types],
            time_filters=[tf.value for tf in job_request.time_filters],
            post_limit=job_request.post_limit,
            comment_limit=job_request.comment_limit,
            max_comment_depth=job_request.max_comment_depth,
            keywords=job_request.keywords,
            min_score=job_request.min_score,
            date_from=job_request.date_from,
            date_to=job_request.date_to,
            anonymize_users=job_request.anonymize_users,
            include_comments=job_request.include_comments,
            status=JobStatus.PENDING
        )
        
        # Save to database
        db.add(collection_job)
        db.commit()
        db.refresh(collection_job)
        
        # Start background collection process
        background_tasks.add_task(run_collection_job, job_id, db)
        
        return CollectionJobResponse(
            job_id=job_id,
            status="pending",
            message="Collection job created successfully"
        )
        
    except Exception as e:
        logger.error(f"Error creating collection job: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create collection job: {str(e)}"
        )
```

## Step-by-Step Gating Process

### 1. Request Arrives
```bash
POST /api/collect/jobs
Authorization: Bearer tk_vcOyYhjjkbcFkeLQ_jmvNjFkUfTzSpGRsUPE7P5oeRE
Content-Type: application/json

{
    "subreddits": ["python"],
    "keywords": ["machine learning"],
    "post_limit": 100
}
```

### 2. FastAPI Dependency Injection
```python
# FastAPI automatically calls dependency chain:

# 1. HTTPBearer extracts token
credentials = HTTPAuthorizationCredentials(
    scheme="Bearer",
    credentials="tk_vcOyYhjjkbcFkeLQ_jmvNjFkUfTzSpGRsUPE7P5oeRE"
)

# 2. get_current_user_from_api_key() called
user = await get_current_user_from_api_key(credentials, db)

# 3. require_active_subscription() called
authenticated_user = await require_active_subscription(user)

# 4. Only if ALL dependencies pass, endpoint function is called
await create_collection_job(..., current_user=authenticated_user)
```

### 3. Subscription Validation Logic
```python
# Inside require_active_subscription():

if user.subscription_status != SubscriptionStatus.ACTIVE:
    # Subscription check FAILS
    raise HTTPException(
        status_code=402,  # Payment Required
        detail="Active subscription required to access this endpoint"
    )
    # Request is BLOCKED here - endpoint never reached

# Subscription check PASSES
return user  # Continue to protected endpoint
```

### 4. Response Based on Subscription Status

#### ❌ **Without Active Subscription** (HTTP 402)
```json
{
    "detail": "Active subscription required to access this endpoint"
}
```

#### ✅ **With Active Subscription** (HTTP 201)  
```json
{
    "job_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "pending", 
    "message": "Collection job created successfully"
}
```

## Business Logic Integration

### User Association
Once subscription gate is passed, all collection jobs are linked to the authenticated user:

```python
collection_job = CollectionJob(
    job_id=job_id,
    user_id=current_user.id,  # 💰 Link to paying customer
    # ... other parameters
)
```

This enables:
- **Billing tracking** - Know which customer created which jobs
- **Usage analytics** - Monitor per-user API consumption  
- **Customer support** - Link support tickets to specific accounts
- **Usage-based pricing** - Future metered billing implementation

### API Key Usage Tracking
```python
# Every authenticated request updates usage tracking
api_key.last_used_at = datetime.utcnow()
db.commit()
```

This provides:
- **Activity monitoring** - When customers last used the API
- **Usage patterns** - Frequency and timing of API calls
- **Billing verification** - Proof of service delivery
- **Security monitoring** - Detect suspicious API key usage

## Testing the Subscription Gate

### Test Scenario 1: No Authentication
```bash
curl -X POST http://localhost:8000/api/collect/jobs \
  -H "Content-Type: application/json" \
  -d '{"subreddits": ["python"]}'

# Response: 401 Unauthorized
# "detail": "Not authenticated"
```

### Test Scenario 2: Invalid API Key
```bash
curl -X POST http://localhost:8000/api/collect/jobs \
  -H "Authorization: Bearer invalid_key" \
  -H "Content-Type: application/json" \
  -d '{"subreddits": ["python"]}'

# Response: 401 Unauthorized  
# "detail": "Invalid API key format" or "Invalid API key"
```

### Test Scenario 3: Valid API Key, No Subscription
```bash
curl -X POST http://localhost:8000/api/collect/jobs \
  -H "Authorization: Bearer tk_valid_api_key_here" \
  -H "Content-Type: application/json" \
  -d '{"subreddits": ["python"]}'

# Response: 402 Payment Required
# "detail": "Active subscription required to access this endpoint"
```

### Test Scenario 4: Valid API Key, Active Subscription  
```bash
curl -X POST http://localhost:8000/api/collect/jobs \
  -H "Authorization: Bearer tk_valid_api_key_here" \
  -H "Content-Type: application/json" \
  -d '{"subreddits": ["python"]}'

# Response: 201 Created
# Collection job created successfully
```

## Subscription Status Management

### Subscription Status Enum
```python
class SubscriptionStatus(Enum):
    INACTIVE = "inactive"    # Free tier - blocked from premium
    ACTIVE = "active"        # Paid subscription - full access  
    SUSPENDED = "suspended"  # Temporarily blocked (payment issues)
    CANCELLED = "cancelled"  # Ended subscription - blocked
```

### Status Change Scenarios

#### Activate Subscription (Payment Successful)
```python
# Triggered by Stripe webhook or admin action
user.subscription_status = SubscriptionStatus.ACTIVE
db.commit()
# User can now access premium endpoints
```

#### Suspend Subscription (Payment Failed)  
```python
# Triggered by failed payment webhook
user.subscription_status = SubscriptionStatus.SUSPENDED  
db.commit()
# User blocked from premium endpoints until payment resolved
```

#### Cancel Subscription
```python
# User cancels or subscription expires
user.subscription_status = SubscriptionStatus.CANCELLED
db.commit() 
# User blocked from premium endpoints
```

## Why This Endpoint Was Chosen

### Business Value Analysis

**High Value Features:**
- ✅ **Data Collection Jobs** - Core product offering
- ✅ **Background Processing** - CPU/memory intensive  
- ✅ **Data Storage** - Database costs
- ✅ **Reddit API Usage** - External API rate limits
- ✅ **Export Capabilities** - Multiple format support

**Free Tier Features:** (Not gated)
- ✅ **Health Checks** - `/health`
- ✅ **API Documentation** - `/docs`, `/redoc`  
- ✅ **Authentication** - `/auth/*` (need to create accounts)
- ✅ **Account Management** - API key creation, user profile

### Revenue Impact
By gating `/api/collect/jobs`, we ensure:
1. **Free users** can explore and set up accounts
2. **Paying customers** access the core value proposition
3. **Clear value differentiation** between free and paid tiers
4. **Resource protection** from abuse/overuse
5. **Revenue attribution** to specific customers

## Future Expansion

### Additional Endpoints to Gate
As the platform grows, additional premium endpoints could include:

```python
# Advanced Analytics (Premium)
@router.get("/analytics/advanced")
async def advanced_analytics(current_user: User = Depends(require_premium_subscription)):
    pass

# Bulk Export (Premium)  
@router.post("/export/bulk")
async def bulk_export(current_user: User = Depends(require_active_subscription)):
    pass

# Real-time Webhooks (Premium)
@router.post("/webhooks/create") 
async def create_webhook(current_user: User = Depends(require_active_subscription)):
    pass
```

### Tiered Subscriptions
```python
async def require_premium_subscription(
    user: User = Depends(get_current_user_from_api_key)
) -> User:
    """Require premium subscription tier"""
    if user.subscription_tier not in [SubscriptionTier.PREMIUM, SubscriptionTier.ENTERPRISE]:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Premium subscription required for this feature"
        )
    return user
```

---

**Implementation Date:** August 31, 2025  
**Protected Endpoint:** `POST /api/collect/jobs`  
**Gating Mechanism:** `require_active_subscription()` dependency  
**Business Model:** Subscription-based SaaS access control