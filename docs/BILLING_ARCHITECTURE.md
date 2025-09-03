# Trendit Billing & Usage Tracking Architecture

## 🎯 Business Model Implementation

### **SaaS Pricing Tiers**
```python
# Subscription tiers with clear value props
FREE_TIER = {
    "api_calls_per_month": 100,
    "exports_per_month": 5,
    "sentiment_analysis_per_month": 50,
    "data_retention_days": 30,
    "price": 0
}

PRO_TIER = {
    "api_calls_per_month": 10000,
    "exports_per_month": 100,
    "sentiment_analysis_per_month": 2000,
    "data_retention_days": 365,
    "price": 29  # $29/month
}

ENTERPRISE_TIER = {
    "api_calls_per_month": 100000,
    "exports_per_month": 1000,
    "sentiment_analysis_per_month": 20000,
    "data_retention_days": -1,  # Unlimited
    "price": 299  # $299/month
}
```

## 💰 **1. STRIPE INTEGRATION SYSTEM**

### **Database Schema Extensions**
```python
# Add to models/models.py

class SubscriptionTier(Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"

class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Stripe integration
    stripe_customer_id = Column(String, nullable=True)
    stripe_subscription_id = Column(String, nullable=True)
    stripe_price_id = Column(String, nullable=True)
    
    # Subscription details
    tier = Column(Enum(SubscriptionTier), default=SubscriptionTier.FREE)
    status = Column(Enum(SubscriptionStatus), default=SubscriptionStatus.INACTIVE)
    
    # Billing cycle
    current_period_start = Column(DateTime, nullable=True)
    current_period_end = Column(DateTime, nullable=True)
    
    # Limits for this subscription
    monthly_api_calls_limit = Column(Integer, default=100)
    monthly_exports_limit = Column(Integer, default=5)
    monthly_sentiment_limit = Column(Integer, default=50)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="subscription")
    usage_records = relationship("UsageRecord", back_populates="subscription")

class UsageRecord(Base):
    __tablename__ = "usage_records"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=False)
    
    # Usage tracking
    endpoint = Column(String, nullable=False)  # "/api/export/posts", "/api/sentiment/analyze"
    usage_type = Column(String, nullable=False)  # "api_call", "export", "sentiment_analysis"
    cost_units = Column(Integer, default=1)  # How much this action "costs"
    
    # Metadata
    request_id = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User")
    subscription = relationship("Subscription", back_populates="usage_records")

# Update User model
class User(Base):
    # ... existing fields ...
    subscription = relationship("Subscription", back_populates="user", uselist=False)
```

### **Stripe Service Implementation**
```python
# services/stripe_service.py

import stripe
from typing import Dict, Optional
import os

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

class StripeService:
    
    @staticmethod
    async def create_customer(user: User) -> str:
        """Create Stripe customer for user"""
        customer = stripe.Customer.create(
            email=user.email,
            name=f"User {user.id}",
            metadata={"user_id": str(user.id)}
        )
        return customer.id
    
    @staticmethod
    async def create_subscription(
        customer_id: str, 
        price_id: str  # Stripe price ID for tier
    ) -> Dict:
        """Create Stripe subscription"""
        subscription = stripe.Subscription.create(
            customer=customer_id,
            items=[{"price": price_id}],
            payment_behavior="default_incomplete",
            expand=["latest_invoice.payment_intent"]
        )
        return subscription
    
    @staticmethod
    async def upgrade_subscription(subscription_id: str, new_price_id: str) -> Dict:
        """Upgrade/downgrade subscription"""
        subscription = stripe.Subscription.retrieve(subscription_id)
        
        stripe.Subscription.modify(
            subscription_id,
            items=[{
                "id": subscription["items"]["data"][0].id,
                "price": new_price_id
            }],
            proration_behavior="immediate_with_options"
        )
    
    @staticmethod
    async def cancel_subscription(subscription_id: str) -> Dict:
        """Cancel subscription"""
        return stripe.Subscription.delete(subscription_id)
    
    # Price IDs (set in Stripe dashboard)
    STRIPE_PRICES = {
        SubscriptionTier.PRO: "price_1234567890",  # $29/month
        SubscriptionTier.ENTERPRISE: "price_0987654321"  # $299/month
    }
```

### **Billing API Endpoints**
```python
# Add to api/auth.py or create api/billing.py

from services.stripe_service import StripeService

@router.post("/billing/create-checkout-session")
async def create_checkout_session(
    tier: SubscriptionTier,
    current_user: User = Depends(get_current_user_from_api_key),
    db: Session = Depends(get_db)
):
    """Create Stripe checkout session for subscription"""
    
    # Create or get Stripe customer
    if not current_user.subscription or not current_user.subscription.stripe_customer_id:
        customer_id = await StripeService.create_customer(current_user)
        
        # Update subscription record
        subscription = Subscription(
            user_id=current_user.id,
            stripe_customer_id=customer_id,
            tier=tier
        )
        db.add(subscription)
        db.commit()
    else:
        customer_id = current_user.subscription.stripe_customer_id
    
    # Create checkout session
    price_id = StripeService.STRIPE_PRICES[tier]
    
    checkout_session = stripe.checkout.Session.create(
        customer=customer_id,
        line_items=[{"price": price_id, "quantity": 1}],
        mode="subscription",
        success_url="http://localhost:8000/billing/success",
        cancel_url="http://localhost:8000/billing/cancel"
    )
    
    return {"checkout_url": checkout_session.url}

@router.post("/billing/webhooks/stripe")
async def stripe_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """Handle Stripe webhooks for subscription events"""
    
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, os.getenv("STRIPE_WEBHOOK_SECRET")
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    
    # Handle subscription events
    if event["type"] == "customer.subscription.created":
        await handle_subscription_created(event["data"]["object"], db)
    elif event["type"] == "customer.subscription.updated": 
        await handle_subscription_updated(event["data"]["object"], db)
    elif event["type"] == "customer.subscription.deleted":
        await handle_subscription_cancelled(event["data"]["object"], db)
    elif event["type"] == "invoice.payment_succeeded":
        await handle_payment_succeeded(event["data"]["object"], db)
    elif event["type"] == "invoice.payment_failed":
        await handle_payment_failed(event["data"]["object"], db)
    
    return {"status": "success"}

async def handle_subscription_created(subscription_data: dict, db: Session):
    """Update user subscription status when Stripe subscription created"""
    customer_id = subscription_data["customer"]
    
    # Find user by Stripe customer ID
    user_subscription = db.query(Subscription).filter(
        Subscription.stripe_customer_id == customer_id
    ).first()
    
    if user_subscription:
        user_subscription.stripe_subscription_id = subscription_data["id"]
        user_subscription.status = SubscriptionStatus.ACTIVE
        user_subscription.current_period_start = datetime.fromtimestamp(
            subscription_data["current_period_start"]
        )
        user_subscription.current_period_end = datetime.fromtimestamp(
            subscription_data["current_period_end"]
        )
        
        # Set limits based on tier
        tier_limits = get_tier_limits(user_subscription.tier)
        user_subscription.monthly_api_calls_limit = tier_limits["api_calls_per_month"]
        user_subscription.monthly_exports_limit = tier_limits["exports_per_month"]
        user_subscription.monthly_sentiment_limit = tier_limits["sentiment_analysis_per_month"]
        
        db.commit()
```

## 📊 **2. USAGE TRACKING & RATE LIMITING SYSTEM**

### **Usage Tracking Service**
```python
# services/usage_tracker.py

from datetime import datetime, timedelta
from sqlalchemy import func
from models.models import UsageRecord, Subscription

class UsageTracker:
    
    @staticmethod
    async def record_usage(
        user_id: int,
        endpoint: str,
        usage_type: str,
        cost_units: int = 1,
        db: Session = None,
        request_info: dict = None
    ):
        """Record API usage for billing and rate limiting"""
        
        usage_record = UsageRecord(
            user_id=user_id,
            subscription_id=get_user_subscription_id(user_id, db),
            endpoint=endpoint,
            usage_type=usage_type,
            cost_units=cost_units,
            request_id=request_info.get("request_id") if request_info else None,
            ip_address=request_info.get("ip_address") if request_info else None,
            user_agent=request_info.get("user_agent") if request_info else None
        )
        
        db.add(usage_record)
        db.commit()
    
    @staticmethod
    async def get_monthly_usage(user_id: int, usage_type: str, db: Session) -> int:
        """Get user's usage for current billing period"""
        
        # Get current billing period
        subscription = db.query(Subscription).filter(
            Subscription.user_id == user_id
        ).first()
        
        if not subscription or not subscription.current_period_start:
            # Use calendar month for free users
            start_date = datetime.now().replace(day=1, hour=0, minute=0, second=0)
        else:
            start_date = subscription.current_period_start
        
        usage_count = db.query(func.sum(UsageRecord.cost_units)).filter(
            UsageRecord.user_id == user_id,
            UsageRecord.usage_type == usage_type,
            UsageRecord.created_at >= start_date
        ).scalar() or 0
        
        return usage_count
    
    @staticmethod
    async def check_rate_limit(
        user_id: int,
        usage_type: str,
        db: Session
    ) -> tuple[bool, int, int]:
        """Check if user has exceeded rate limits
        
        Returns: (is_allowed, current_usage, limit)
        """
        
        subscription = db.query(Subscription).filter(
            Subscription.user_id == user_id
        ).first()
        
        # Get limits based on subscription tier
        if not subscription or subscription.tier == SubscriptionTier.FREE:
            limits = {
                "api_call": 100,
                "export": 5,
                "sentiment_analysis": 50
            }
        elif subscription.tier == SubscriptionTier.PRO:
            limits = {
                "api_call": 10000,
                "export": 100,
                "sentiment_analysis": 2000
            }
        else:  # ENTERPRISE
            limits = {
                "api_call": 100000,
                "export": 1000,
                "sentiment_analysis": 20000
            }
        
        current_usage = await UsageTracker.get_monthly_usage(user_id, usage_type, db)
        limit = limits.get(usage_type, 0)
        
        is_allowed = current_usage < limit
        return is_allowed, current_usage, limit
```

### **Rate Limiting Middleware**
```python
# middleware/rate_limiting.py

from fastapi import HTTPException, status
from services.usage_tracker import UsageTracker

async def enforce_rate_limit_and_track_usage(
    user: User,
    endpoint: str, 
    usage_type: str,
    cost_units: int = 1,
    db: Session = None
):
    """Enforce rate limits and track usage"""
    
    # Check rate limit before processing request
    is_allowed, current_usage, limit = await UsageTracker.check_rate_limit(
        user.id, usage_type, db
    )
    
    if not is_allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": "rate_limit_exceeded",
                "message": f"Monthly {usage_type} limit exceeded",
                "current_usage": current_usage,
                "limit": limit,
                "upgrade_url": "http://localhost:8000/billing/upgrade"
            }
        )
    
    # Record usage after successful request
    await UsageTracker.record_usage(
        user_id=user.id,
        endpoint=endpoint,
        usage_type=usage_type,
        cost_units=cost_units,
        db=db
    )
    
    return True
```

### **Updated Endpoint Dependencies**
```python
# Update require_active_subscription to include usage tracking

async def require_active_subscription_with_usage_tracking(
    usage_type: str,
    cost_units: int = 1
):
    """Dependency factory for subscription + usage tracking"""
    
    async def dependency(
        request: Request,
        user: User = Depends(get_current_user_from_api_key),
        db: Session = Depends(get_db)
    ):
        # Check subscription status
        if user.subscription.status != SubscriptionStatus.ACTIVE and user.subscription.tier != SubscriptionTier.FREE:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="Active subscription required"
            )
        
        # Enforce rate limits and track usage
        await enforce_rate_limit_and_track_usage(
            user=user,
            endpoint=str(request.url.path),
            usage_type=usage_type,
            cost_units=cost_units,
            db=db
        )
        
        return user
    
    return dependency

# Usage in endpoints
@router.post("/export/posts/csv")
async def export_posts_csv(
    request: ExportRequest,
    current_user: User = Depends(require_active_subscription_with_usage_tracking("export", cost_units=1))
):
    # Export logic here
    pass

@router.post("/sentiment/analyze-batch")
async def analyze_batch_sentiment(
    request: BatchSentimentRequest,
    current_user: User = Depends(require_active_subscription_with_usage_tracking("sentiment_analysis", cost_units=len(request.texts)))
):
    # Sentiment analysis logic
    pass
```

## 🎯 **3. PRICING STRATEGY IMPLEMENTATION**

### **Tier Definitions**
```python
# config/pricing.py

PRICING_TIERS = {
    SubscriptionTier.FREE: {
        "name": "Free",
        "price": 0,
        "limits": {
            "api_calls_per_month": 100,
            "exports_per_month": 5,
            "sentiment_analysis_per_month": 50,
            "data_retention_days": 30
        },
        "features": [
            "Basic API access",
            "5 data exports per month", 
            "30-day data retention",
            "Community support"
        ]
    },
    SubscriptionTier.PRO: {
        "name": "Pro",
        "price": 29,
        "limits": {
            "api_calls_per_month": 10000,
            "exports_per_month": 100,
            "sentiment_analysis_per_month": 2000,
            "data_retention_days": 365
        },
        "features": [
            "10,000 API calls per month",
            "100 data exports per month",
            "2,000 sentiment analyses per month",
            "1-year data retention",
            "Priority email support",
            "Advanced analytics"
        ]
    },
    SubscriptionTier.ENTERPRISE: {
        "name": "Enterprise", 
        "price": 299,
        "limits": {
            "api_calls_per_month": 100000,
            "exports_per_month": 1000, 
            "sentiment_analysis_per_month": 20000,
            "data_retention_days": -1  # Unlimited
        },
        "features": [
            "100,000 API calls per month",
            "1,000 data exports per month", 
            "20,000 sentiment analyses per month",
            "Unlimited data retention",
            "Phone & chat support",
            "Custom integrations",
            "Dedicated account manager"
        ]
    }
}
```

## 🚀 **Implementation Priority**

1. **Database Schema** - Add Subscription and UsageRecord models
2. **Basic Stripe Integration** - Create checkout sessions  
3. **Usage Tracking** - Record API calls, exports, sentiment analysis
4. **Rate Limiting** - Enforce limits per tier
5. **Webhook Handling** - Process Stripe subscription events
6. **Billing Dashboard** - Frontend for subscription management

This architecture transforms your authentication system into a complete SaaS billing platform with proper usage tracking and rate limiting!

**Ready to start implementing? Which component should we build first?**