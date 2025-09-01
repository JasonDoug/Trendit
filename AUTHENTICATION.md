# Trendit Authentication System Documentation

## Overview

Trendit implements a **subscription-based SaaS authentication system** that gates premium Reddit data collection features behind paid subscriptions. The system supports both web-based JWT authentication and API key-based programmatic access.

## Architecture

### Authentication Flow
```
1. User Registration → Inactive Subscription
2. Login → JWT Token (for web/dashboard)
3. Create API Key → Programmatic access token
4. Activate Subscription → Access to premium endpoints
5. API Key Authentication → Protected endpoint access
```

### Database Models

#### User Model
```python
class User(Base):
    id: int (Primary Key)
    email: str (Unique)
    username: str (Unique)
    password_hash: str (BCrypt hashed)
    is_active: bool (Default: True)
    subscription_status: SubscriptionStatus (Default: INACTIVE)
    created_at: datetime
```

#### APIKey Model
```python
class APIKey(Base):
    id: int (Primary Key)
    user_id: int (Foreign Key → users.id)
    key_hash: str (SHA256 hashed, indexed)
    name: str (User-friendly identifier)
    is_active: bool (Default: True)
    created_at: datetime
    expires_at: datetime (Optional)
    last_used_at: datetime (Updated on use)
```

#### Subscription Status Enum
```python
class SubscriptionStatus(Enum):
    INACTIVE = "inactive"    # Free tier - no premium access
    ACTIVE = "active"        # Paid subscription - full access
    SUSPENDED = "suspended"  # Temporarily disabled
    CANCELLED = "cancelled"  # Ended subscription
```

## API Endpoints

### Authentication Endpoints

#### 1. User Registration
**Endpoint:** `POST /auth/register`

**Request Body:**
```json
{
    "email": "user@example.com",
    "password": "securepassword123",
    "username": "myusername"  // Optional
}
```

**Response:**
```json
{
    "id": 1,
    "email": "user@example.com", 
    "username": "myusername",
    "is_active": true,
    "subscription_status": "inactive",
    "created_at": "2025-08-31T22:35:34.401537+00:00"
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123", 
    "username": "myusername"
  }'
```

#### 2. User Login
**Endpoint:** `POST /auth/login`

**Request Body:**
```json
{
    "email": "user@example.com",
    "password": "securepassword123"
}
```

**Response:**
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'
```

### API Key Management

#### 3. Create API Key
**Endpoint:** `POST /auth/api-keys`
**Authentication:** JWT Token required

**Request Body:**
```json
{
    "name": "My Production API Key"
}
```

**Response:**
```json
{
    "id": 1,
    "name": "My Production API Key",
    "key": "tk_vcOyYhjjkbcFkeLQ_jmvNjFkUfTzSpGRsUPE7P5oeRE",
    "created_at": "2025-08-31T22:35:47.261317+00:00",
    "expires_at": null
}
```

**cURL Example:**
```bash
JWT_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

curl -X POST http://localhost:8000/auth/api-keys \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -d '{"name": "My Production API Key"}'
```

**⚠️ Security Note:** The raw API key is only shown once during creation. Store it securely.

#### 4. List API Keys
**Endpoint:** `GET /auth/api-keys`
**Authentication:** JWT Token required

**Response:**
```json
[
    {
        "id": 1,
        "name": "My Production API Key",
        "is_active": true,
        "created_at": "2025-08-31T22:35:47.261317+00:00",
        "expires_at": null,
        "last_used_at": "2025-08-31T22:40:15.123456+00:00"
    }
]
```

**cURL Example:**
```bash
curl -X GET http://localhost:8000/auth/api-keys \
  -H "Authorization: Bearer $JWT_TOKEN"
```

#### 5. Delete API Key
**Endpoint:** `DELETE /auth/api-keys/{key_id}`
**Authentication:** JWT Token required

**Response:**
```json
{
    "message": "API key deleted successfully"
}
```

**cURL Example:**
```bash
curl -X DELETE http://localhost:8000/auth/api-keys/1 \
  -H "Authorization: Bearer $JWT_TOKEN"
```

## Protected Endpoints

### Collection API (Premium Feature)
**Endpoint:** `POST /api/collect/jobs`
**Authentication:** API Key required
**Subscription:** Active subscription required

**Without Subscription (402 Payment Required):**
```bash
curl -X POST http://localhost:8000/api/collect/jobs \
  -H "Authorization: Bearer tk_your_api_key" \
  -d '{"subreddits": ["python"], "keywords": ["test"]}'

# Response:
{
    "detail": "Active subscription required to access this endpoint"
}
```

**With Active Subscription (Success):**
```bash
# Same request, but user has active subscription
# Response: Collection job created successfully
```

## Complete Authentication Flow Example

### Step 1: Register New User
```bash
# Register user account
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "customer@company.com",
    "password": "SecureP@ssw0rd",
    "username": "company_user"
  }'

# Response: User created with subscription_status: "inactive"
```

### Step 2: Login to Get JWT Token
```bash
# Login to get JWT token
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "customer@company.com", 
    "password": "SecureP@ssw0rd"
  }'

# Save the returned JWT token
JWT_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### Step 3: Create API Key for Programmatic Access
```bash
# Create API key using JWT token
curl -X POST http://localhost:8000/auth/api-keys \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -d '{"name": "Production API Key"}'

# Save the returned API key (shown only once!)
API_KEY="tk_vcOyYhjjkbcFkeLQ_jmvNjFkUfTzSpGRsUPE7P5oeRE"
```

### Step 4: Test Premium Endpoint (Will Fail)
```bash
# Try to use premium collection feature
curl -X POST http://localhost:8000/api/collect/jobs \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_KEY" \
  -d '{
    "subreddits": ["python"],
    "keywords": ["machine learning"], 
    "sort_types": ["hot"],
    "time_filters": ["day"],
    "post_limit": 10
  }'

# Response: "Active subscription required to access this endpoint"
```

### Step 5: Activate Subscription (Payment Processing)
```python
# In production, this would be triggered by Stripe webhook
# For testing, manually activate:

from models.database import SessionLocal
from models.models import User, SubscriptionStatus

db = SessionLocal()
user = db.query(User).filter(User.email == 'customer@company.com').first()
user.subscription_status = SubscriptionStatus.ACTIVE
db.commit()
```

### Step 6: Access Premium Features
```bash
# Same collection request now works
curl -X POST http://localhost:8000/api/collect/jobs \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_KEY" \
  -d '{
    "subreddits": ["python"],
    "keywords": ["machine learning"],
    "sort_types": ["hot"], 
    "time_filters": ["day"],
    "post_limit": 10
  }'

# Response: Collection job created successfully with job_id
```

## Security Features

### Password Security
- **BCrypt hashing** with salt rounds
- Passwords never stored in plain text
- Password verification on login

### API Key Security
- **SHA256 hashing** of API keys in database
- Raw keys only shown once during creation
- `tk_` prefix for easy identification
- Optional expiration dates
- Last used timestamp tracking

### JWT Tokens
- **HS256 algorithm** with secret key
- 30-minute expiration (configurable)
- User ID embedded in payload
- Stateless authentication

### Subscription-Based Access Control
- **Payment-required responses** (HTTP 402) for premium features
- Subscription status validation on every protected request
- User-specific collection job tracking
- Future-ready for usage-based billing

## Integration with Business Logic

### Collection Job Association
```python
# Collection jobs are automatically linked to authenticated users
collection_job = CollectionJob(
    job_id=uuid.uuid4(),
    user_id=current_user.id,  # From API key authentication
    subreddits=request.subreddits,
    # ... other parameters
)
```

### Usage Tracking
- API key `last_used_at` timestamp updated on each request
- Collection jobs linked to specific users for billing
- Foundation for usage-based pricing models

## Environment Configuration

### Required Environment Variables
```bash
# JWT Configuration (move from hardcoded)
SECRET_KEY="your-production-secret-key-here"
ALGORITHM="HS256" 
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database Connection
DATABASE_URL="postgresql://user:password@localhost/trendit"
```

## Error Responses

### Authentication Errors
```json
// Invalid credentials
{
    "detail": "Incorrect email or password"
}

// Invalid JWT token
{
    "detail": "Could not validate credentials"
}

// Invalid API key format
{
    "detail": "Invalid API key format"
}

// Invalid API key
{
    "detail": "Invalid API key"
}
```

### Authorization Errors  
```json
// Inactive subscription
{
    "detail": "Active subscription required to access this endpoint"
}

// Inactive user account
{
    "detail": "User account is inactive"
}
```

## Future Enhancements

### Planned Features
1. **Stripe Integration** - Webhook-based subscription management
2. **Multi-tenant Organizations** - Team accounts with role-based access
3. **Usage-based Billing** - API call and data export metering
4. **Rate Limiting** - Per-user/per-plan request throttling
5. **OAuth2 Support** - Google/GitHub social login
6. **API Key Permissions** - Granular endpoint access control

### Migration Path
The current authentication system is designed to support these future enhancements without breaking changes:

- User table can be extended with `org_id` for multi-tenancy
- APIKey table can be extended with `permissions` JSON field
- Subscription status enum can be extended with more plan types
- Rate limiting hooks are already in place in dependency functions

---

**Last Updated:** August 31, 2025  
**Version:** 1.0.0 (MVP SaaS Authentication)