# Trendit + Paddle Integration Architecture

## 🎯 Business Model Implementation

### **Subscription Tiers with Paddle**
```python
# Trendit pricing strategy
TRENDIT_TIERS = {
    "FREE": {
        "price": 0,
        "paddle_price_id": None,
        "limits": {
            "api_calls_per_month": 100,
            "exports_per_month": 5,
            "sentiment_analysis_per_month": 50,
            "data_retention_days": 30
        }
    },
    "PRO": {
        "price": 29,  # $29/month
        "paddle_price_id": "pri_trendit_pro_29_monthly",
        "limits": {
            "api_calls_per_month": 10000,
            "exports_per_month": 100,
            "sentiment_analysis_per_month": 2000,
            "data_retention_days": 365
        }
    },
    "ENTERPRISE": {
        "price": 299,  # $299/month
        "paddle_price_id": "pri_trendit_enterprise_299_monthly",
        "limits": {
            "api_calls_per_month": 100000,
            "exports_per_month": 1000,
            "sentiment_analysis_per_month": 20000,
            "data_retention_days": -1  # Unlimited
        }
    }
}
```

## 💾 **1. DATABASE SCHEMA EXTENSIONS**

### **Updated Models (Extends Current Authentication)**
```python
# Add to models/models.py

from enum import Enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum, ForeignKey, Float, Boolean, Text

class SubscriptionTier(Enum):
    FREE = "free"
    PRO = "pro" 
    ENTERPRISE = "enterprise"

class PaddleSubscription(Base):
    """Extended subscription model for Paddle integration"""
    __tablename__ = "paddle_subscriptions"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    
    # Paddle Integration
    paddle_customer_id = Column(String, nullable=True, unique=True)
    paddle_subscription_id = Column(String, nullable=True, unique=True)
    paddle_price_id = Column(String, nullable=True)
    
    # Subscription Details
    tier = Column(SQLEnum(SubscriptionTier), default=SubscriptionTier.FREE)
    status = Column(SQLEnum(SubscriptionStatus), default=SubscriptionStatus.INACTIVE)
    
    # Billing Cycle
    current_period_start = Column(DateTime, nullable=True)
    current_period_end = Column(DateTime, nullable=True)
    next_billed_at = Column(DateTime, nullable=True)
    
    # Usage Limits (based on tier)
    monthly_api_calls_limit = Column(Integer, default=100)
    monthly_exports_limit = Column(Integer, default=5)
    monthly_sentiment_limit = Column(Integer, default=50)
    data_retention_days = Column(Integer, default=30)
    
    # Billing Info
    price_per_month = Column(Float, default=0.0)
    currency = Column(String, default="USD")
    
    # Trial Management
    trial_start_date = Column(DateTime, nullable=True)
    trial_end_date = Column(DateTime, nullable=True)
    is_trial = Column(Boolean, default=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="paddle_subscription")
    usage_records = relationship("UsageRecord", back_populates="subscription")
    billing_events = relationship("BillingEvent", back_populates="subscription")

class UsageRecord(Base):
    """Track API usage for billing and rate limiting"""
    __tablename__ = "usage_records"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    subscription_id = Column(Integer, ForeignKey("paddle_subscriptions.id"), nullable=False)
    
    # Usage Details
    endpoint = Column(String, nullable=False)  # "/api/export/posts"
    usage_type = Column(String, nullable=False)  # "api_call", "export", "sentiment_analysis"
    cost_units = Column(Integer, default=1)  # How many "units" this consumed
    
    # Request Context
    request_id = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)
    user_agent = Column(Text, nullable=True)
    
    # Timing
    created_at = Column(DateTime, default=datetime.utcnow)
    billing_period_start = Column(DateTime, nullable=False)  # Which billing period this belongs to
    
    # Relationships
    user = relationship("User")
    subscription = relationship("PaddleSubscription", back_populates="usage_records")

class BillingEvent(Base):
    """Track billing events from Paddle webhooks"""
    __tablename__ = "billing_events"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    subscription_id = Column(Integer, ForeignKey("paddle_subscriptions.id"), nullable=True)
    
    # Paddle Event Data
    paddle_event_id = Column(String, nullable=False, unique=True)
    event_type = Column(String, nullable=False)  # "subscription.created", "transaction.completed"
    paddle_subscription_id = Column(String, nullable=True)
    paddle_transaction_id = Column(String, nullable=True)
    
    # Event Details
    amount = Column(Float, nullable=True)
    currency = Column(String, nullable=True)
    status = Column(String, nullable=False)  # "success", "failed", "pending"
    
    # Raw Data
    raw_event_data = Column(Text, nullable=False)  # JSON dump of full Paddle event
    
    # Timing
    paddle_event_time = Column(DateTime, nullable=False)
    processed_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User")
    subscription = relationship("PaddleSubscription", back_populates="billing_events")

# Update User model to include paddle subscription
class User(Base):
    # ... existing fields ...
    paddle_subscription = relationship("PaddleSubscription", back_populates="user", uselist=False)
```

## 🔧 **2. PADDLE SERVICE IMPLEMENTATION**

### **Core Paddle Integration Service**
```python
# services/paddle_service.py

import httpx
import hmac
import hashlib
import json
from typing import Dict, List, Optional
from datetime import datetime
import os
from models.models import User, PaddleSubscription, SubscriptionTier, SubscriptionStatus

class PaddleService:
    """Paddle Billing API integration for Trendit"""
    
    def __init__(self, sandbox: bool = True):
        self.api_key = os.getenv("PADDLE_API_KEY")
        self.webhook_secret = os.getenv("PADDLE_WEBHOOK_SECRET")
        self.base_url = (
            "https://sandbox-api.paddle.com" if sandbox 
            else "https://api.paddle.com"
        )
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    # Customer Management
    async def create_customer(self, user: User) -> Dict:
        """Create Paddle customer for Trendit user"""
        
        payload = {
            "email": user.email,
            "name": user.email.split("@")[0],  # Use email prefix as name
            "locale": "en",
            "custom_data": {
                "trendit_user_id": str(user.id),
                "signup_date": datetime.utcnow().isoformat(),
                "platform": "trendit"
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/customers",
                json=payload,
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
    
    # Subscription Management
    async def create_subscription(
        self, 
        customer_id: str, 
        tier: SubscriptionTier,
        trial_days: Optional[int] = None
    ) -> Dict:
        """Create Paddle subscription for specific tier"""
        
        price_id = TRENDIT_TIERS[tier.value.upper()]["paddle_price_id"]
        
        payload = {
            "customer_id": customer_id,
            "items": [{
                "price_id": price_id,
                "quantity": 1
            }],
            "collection_mode": "automatic",
            "billing_cycle": {
                "interval": "month",
                "frequency": 1
            },
            "custom_data": {
                "trendit_tier": tier.value,
                "created_via": "trendit_api"
            }
        }
        
        # Add trial period if specified
        if trial_days:
            trial_end = datetime.utcnow() + timedelta(days=trial_days)
            payload["scheduled_change"] = {
                "action": "resume", 
                "effective_at": trial_end.isoformat(),
                "resume_immediately": False
            }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/subscriptions",
                json=payload,
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
    
    async def update_subscription(
        self, 
        subscription_id: str, 
        new_tier: SubscriptionTier
    ) -> Dict:
        """Upgrade/downgrade subscription"""
        
        new_price_id = TRENDIT_TIERS[new_tier.value.upper()]["paddle_price_id"]
        
        payload = {
            "items": [{
                "price_id": new_price_id,
                "quantity": 1
            }],
            "proration_billing_mode": "prorated_immediately"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"{self.base_url}/subscriptions/{subscription_id}",
                json=payload,
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
    
    async def cancel_subscription(self, subscription_id: str) -> Dict:
        """Cancel subscription at end of billing period"""
        
        payload = {
            "scheduled_change": {
                "action": "cancel",
                "effective_at": "next_billing_period"
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"{self.base_url}/subscriptions/{subscription_id}",
                json=payload,
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
    
    # Checkout Session
    async def create_checkout_url(
        self, 
        user: User, 
        tier: SubscriptionTier,
        success_url: str,
        cancel_url: str
    ) -> str:
        """Create Paddle checkout URL for subscription"""
        
        price_id = TRENDIT_TIERS[tier.value.upper()]["paddle_price_id"]
        
        payload = {
            "items": [{
                "price_id": price_id,
                "quantity": 1
            }],
            "customer_email": user.email,
            "custom_data": {
                "trendit_user_id": str(user.id),
                "tier": tier.value
            },
            "return_url": success_url,
            "discount_id": None,  # Could add promo codes here
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/transactions",
                json=payload,
                headers=self.headers
            )
            response.raise_for_status()
            data = response.json()
            return data["data"]["checkout"]["url"]
    
    # Webhook Verification
    def verify_webhook(self, payload: bytes, signature: str, timestamp: str) -> bool:
        """Verify Paddle webhook signature (2025 enhanced security)"""
        
        if not self.webhook_secret:
            return False
        
        # Construct signed payload
        signed_payload = f"{timestamp}.{payload.decode()}"
        
        # Calculate expected signature
        expected_signature = hmac.new(
            self.webhook_secret.encode(),
            signed_payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected_signature)

# Paddle price IDs (set in Paddle dashboard)
PADDLE_PRICE_IDS = {
    SubscriptionTier.PRO: "pri_01h8example1234567890",
    SubscriptionTier.ENTERPRISE: "pri_01h8example0987654321"
}
```

## 📡 **3. BILLING API ENDPOINTS**

### **Subscription Management Endpoints**
```python
# api/billing.py (new file)

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from models.database import get_db
from models.models import User, PaddleSubscription, SubscriptionTier, SubscriptionStatus
from services.paddle_service import PaddleService
from api.auth import get_current_user_from_api_key
import logging

router = APIRouter(prefix="/api/billing", tags=["billing"])
logger = logging.getLogger(__name__)

# Initialize Paddle service
paddle_service = PaddleService(sandbox=True)  # Change to False in production

@router.post("/checkout/create")
async def create_checkout_session(
    tier: SubscriptionTier,
    current_user: User = Depends(get_current_user_from_api_key),
    db: Session = Depends(get_db)
):
    """Create Paddle checkout session for subscription upgrade"""
    
    try:
        # Check if user already has active subscription
        if (current_user.paddle_subscription and 
            current_user.paddle_subscription.status == SubscriptionStatus.ACTIVE):
            return {
                "error": "already_subscribed",
                "message": "User already has active subscription",
                "current_tier": current_user.paddle_subscription.tier.value,
                "manage_url": f"/billing/manage/{current_user.paddle_subscription.paddle_subscription_id}"
            }
        
        # Create or get Paddle customer
        if not current_user.paddle_subscription or not current_user.paddle_subscription.paddle_customer_id:
            customer_data = await paddle_service.create_customer(current_user)
            customer_id = customer_data["data"]["id"]
            
            # Create or update subscription record
            if not current_user.paddle_subscription:
                subscription = PaddleSubscription(
                    user_id=current_user.id,
                    paddle_customer_id=customer_id,
                    tier=tier
                )
                db.add(subscription)
            else:
                current_user.paddle_subscription.paddle_customer_id = customer_id
                current_user.paddle_subscription.tier = tier
            
            db.commit()
        
        # Create checkout URL
        checkout_url = await paddle_service.create_checkout_url(
            user=current_user,
            tier=tier,
            success_url="https://trendit.com/billing/success",
            cancel_url="https://trendit.com/billing/cancel"
        )
        
        return {
            "checkout_url": checkout_url,
            "tier": tier.value,
            "price": TRENDIT_TIERS[tier.value.upper()]["price"]
        }
        
    except Exception as e:
        logger.error(f"Checkout creation failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to create checkout session")

@router.get("/subscription/status")
async def get_subscription_status(
    current_user: User = Depends(get_current_user_from_api_key)
):
    """Get current user's subscription status and usage"""
    
    if not current_user.paddle_subscription:
        return {
            "tier": "free",
            "status": "inactive",
            "limits": TRENDIT_TIERS["FREE"]["limits"]
        }
    
    subscription = current_user.paddle_subscription
    
    return {
        "tier": subscription.tier.value,
        "status": subscription.status.value,
        "current_period_end": subscription.current_period_end.isoformat() if subscription.current_period_end else None,
        "price_per_month": subscription.price_per_month,
        "limits": {
            "api_calls_per_month": subscription.monthly_api_calls_limit,
            "exports_per_month": subscription.monthly_exports_limit,
            "sentiment_analysis_per_month": subscription.monthly_sentiment_limit,
            "data_retention_days": subscription.data_retention_days
        },
        "is_trial": subscription.is_trial,
        "trial_end_date": subscription.trial_end_date.isoformat() if subscription.trial_end_date else None
    }

@router.post("/subscription/upgrade")
async def upgrade_subscription(
    new_tier: SubscriptionTier,
    current_user: User = Depends(get_current_user_from_api_key),
    db: Session = Depends(get_db)
):
    """Upgrade/downgrade existing subscription"""
    
    if not current_user.paddle_subscription or not current_user.paddle_subscription.paddle_subscription_id:
        raise HTTPException(status_code=404, detail="No active subscription found")
    
    try:
        subscription_data = await paddle_service.update_subscription(
            current_user.paddle_subscription.paddle_subscription_id,
            new_tier
        )
        
        # Update local database
        current_user.paddle_subscription.tier = new_tier
        tier_limits = TRENDIT_TIERS[new_tier.value.upper()]["limits"]
        current_user.paddle_subscription.monthly_api_calls_limit = tier_limits["api_calls_per_month"]
        current_user.paddle_subscription.monthly_exports_limit = tier_limits["exports_per_month"]
        current_user.paddle_subscription.monthly_sentiment_limit = tier_limits["sentiment_analysis_per_month"]
        
        db.commit()
        
        return {"message": "Subscription updated successfully", "new_tier": new_tier.value}
        
    except Exception as e:
        logger.error(f"Subscription upgrade failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to upgrade subscription")

@router.post("/subscription/cancel")
async def cancel_subscription(
    current_user: User = Depends(get_current_user_from_api_key),
    db: Session = Depends(get_db)
):
    """Cancel subscription at end of billing period"""
    
    if not current_user.paddle_subscription or not current_user.paddle_subscription.paddle_subscription_id:
        raise HTTPException(status_code=404, detail="No active subscription found")
    
    try:
        await paddle_service.cancel_subscription(
            current_user.paddle_subscription.paddle_subscription_id
        )
        
        # Don't immediately downgrade - let Paddle webhook handle it
        logger.info(f"Subscription cancellation initiated for user {current_user.id}")
        
        return {
            "message": "Subscription will be cancelled at the end of current billing period",
            "current_period_end": current_user.paddle_subscription.current_period_end.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Subscription cancellation failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to cancel subscription")
```

## 📡 **4. WEBHOOK HANDLER**

### **Paddle Webhook Processing**
```python
# api/webhooks.py (new file)

from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.orm import Session
from models.database import get_db
from models.models import PaddleSubscription, BillingEvent, SubscriptionStatus, SubscriptionTier
from services.paddle_service import paddle_service
import json
import logging
from datetime import datetime

router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])
logger = logging.getLogger(__name__)

@router.post("/paddle")
async def handle_paddle_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """Handle Paddle Billing API webhooks"""
    
    try:
        payload = await request.body()
        signature = request.headers.get("paddle-signature")
        timestamp = request.headers.get("paddle-timestamp")
        
        # Verify webhook authenticity
        if not paddle_service.verify_webhook(payload, signature, timestamp):
            logger.error("Invalid Paddle webhook signature")
            raise HTTPException(status_code=401, detail="Invalid signature")
        
        event_data = json.loads(payload.decode())
        event_type = event_data.get("event_type")
        
        # Log the event
        logger.info(f"Received Paddle webhook: {event_type}")
        
        # Route to specific handlers
        handlers = {
            "subscription.created": handle_subscription_created,
            "subscription.updated": handle_subscription_updated,
            "subscription.canceled": handle_subscription_canceled,
            "subscription.resumed": handle_subscription_resumed,
            "transaction.completed": handle_transaction_completed,
            "transaction.payment_failed": handle_payment_failed,
            "customer.updated": handle_customer_updated,
        }
        
        if event_type in handlers:
            await handlers[event_type](event_data, db)
        else:
            logger.warning(f"Unhandled webhook event type: {event_type}")
        
        # Store the event for audit purposes
        await store_billing_event(event_data, db)
        
        return {"status": "success", "event_type": event_type}
        
    except Exception as e:
        logger.error(f"Webhook processing failed: {e}")
        raise HTTPException(status_code=500, detail="Webhook processing failed")

async def handle_subscription_created(event_data: dict, db: Session):
    """Handle new subscription creation"""
    
    subscription_data = event_data["data"]
    customer_id = subscription_data["customer_id"]
    
    # Find subscription by Paddle customer ID
    paddle_subscription = db.query(PaddleSubscription).filter(
        PaddleSubscription.paddle_customer_id == customer_id
    ).first()
    
    if paddle_subscription:
        # Update subscription with Paddle data
        paddle_subscription.paddle_subscription_id = subscription_data["id"]
        paddle_subscription.status = SubscriptionStatus.ACTIVE
        paddle_subscription.current_period_start = datetime.fromisoformat(
            subscription_data["current_billing_period"]["starts_at"]
        )
        paddle_subscription.current_period_end = datetime.fromisoformat(
            subscription_data["current_billing_period"]["ends_at"]
        )
        paddle_subscription.next_billed_at = datetime.fromisoformat(
            subscription_data["next_billed_at"]
        ) if subscription_data.get("next_billed_at") else None
        
        # Set tier and limits based on price
        for item in subscription_data["items"]:
            price_id = item["price"]["id"]
            if price_id == PADDLE_PRICE_IDS[SubscriptionTier.PRO]:
                paddle_subscription.tier = SubscriptionTier.PRO
                paddle_subscription.price_per_month = 29.0
                # Set Pro limits
                paddle_subscription.monthly_api_calls_limit = 10000
                paddle_subscription.monthly_exports_limit = 100
                paddle_subscription.monthly_sentiment_limit = 2000
                paddle_subscription.data_retention_days = 365
            elif price_id == PADDLE_PRICE_IDS[SubscriptionTier.ENTERPRISE]:
                paddle_subscription.tier = SubscriptionTier.ENTERPRISE
                paddle_subscription.price_per_month = 299.0
                # Set Enterprise limits
                paddle_subscription.monthly_api_calls_limit = 100000
                paddle_subscription.monthly_exports_limit = 1000
                paddle_subscription.monthly_sentiment_limit = 20000
                paddle_subscription.data_retention_days = -1
        
        db.commit()
        logger.info(f"Subscription created for user {paddle_subscription.user_id}")

async def handle_subscription_canceled(event_data: dict, db: Session):
    """Handle subscription cancellation"""
    
    subscription_id = event_data["data"]["id"]
    
    paddle_subscription = db.query(PaddleSubscription).filter(
        PaddleSubscription.paddle_subscription_id == subscription_id
    ).first()
    
    if paddle_subscription:
        paddle_subscription.status = SubscriptionStatus.CANCELLED
        # Downgrade to free tier
        paddle_subscription.tier = SubscriptionTier.FREE
        paddle_subscription.monthly_api_calls_limit = 100
        paddle_subscription.monthly_exports_limit = 5
        paddle_subscription.monthly_sentiment_limit = 50
        paddle_subscription.data_retention_days = 30
        
        db.commit()
        logger.info(f"Subscription cancelled for user {paddle_subscription.user_id}")

async def handle_payment_failed(event_data: dict, db: Session):
    """Handle failed payment"""
    
    subscription_id = event_data["data"]["subscription_id"]
    
    paddle_subscription = db.query(PaddleSubscription).filter(
        PaddleSubscription.paddle_subscription_id == subscription_id
    ).first()
    
    if paddle_subscription:
        paddle_subscription.status = SubscriptionStatus.SUSPENDED
        db.commit()
        logger.warning(f"Payment failed for user {paddle_subscription.user_id}")

async def store_billing_event(event_data: dict, db: Session):
    """Store billing event for audit purposes"""
    
    try:
        subscription_data = event_data.get("data", {})
        customer_id = subscription_data.get("customer_id")
        
        # Find user by customer ID
        paddle_subscription = None
        if customer_id:
            paddle_subscription = db.query(PaddleSubscription).filter(
                PaddleSubscription.paddle_customer_id == customer_id
            ).first()
        
        billing_event = BillingEvent(
            user_id=paddle_subscription.user_id if paddle_subscription else None,
            subscription_id=paddle_subscription.id if paddle_subscription else None,
            paddle_event_id=event_data.get("event_id"),
            event_type=event_data.get("event_type"),
            paddle_subscription_id=subscription_data.get("id"),
            paddle_transaction_id=subscription_data.get("transaction_id"),
            status="processed",
            raw_event_data=json.dumps(event_data),
            paddle_event_time=datetime.fromisoformat(event_data.get("occurred_at"))
        )
        
        db.add(billing_event)
        db.commit()
        
    except Exception as e:
        logger.error(f"Failed to store billing event: {e}")
```

## 🚀 **Next Implementation Steps**

1. **Database Migration** - Add new Paddle models
2. **Environment Variables** - Set Paddle API keys
3. **Billing Endpoints** - Implement checkout and management
4. **Webhook Handler** - Process Paddle events
5. **Usage Tracking Integration** - Connect to existing gated endpoints

**Ready to start implementing? Which component should we build first while waiting for CodeRabbit?**