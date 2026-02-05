"""
Stripe Billing Integration for ASF-Engine SaaS
Handles subscriptions, payments, and invoices
"""
import os
from typing import Dict, Any, Optional, List
import stripe
from datetime import datetime

# Initialize Stripe
stripe.api_key = os.getenv("STRIPE_API_KEY")
if not stripe.api_key:
    raise ValueError("STRIPE_API_KEY environment variable must be set for billing features")


class SubscriptionPlan:
    """Subscription plan definitions"""
    
    FREE = {
        "id": "free",
        "name": "Free",
        "price": 0,
        "features": [
            "Basic monitoring",
            "Up to 100 predictions/month",
            "Email support",
            "7-day data retention"
        ],
        "limits": {
            "predictions_per_month": 100,
            "data_retention_days": 7,
            "users": 1
        }
    }
    
    STARTER = {
        "id": "starter",
        "name": "Starter",
        "price": 49,
        "price_id": "price_starter_monthly",
        "features": [
            "Advanced monitoring",
            "Up to 1,000 predictions/month",
            "Priority email support",
            "30-day data retention",
            "Custom alerts",
            "API access"
        ],
        "limits": {
            "predictions_per_month": 1000,
            "data_retention_days": 30,
            "users": 3
        }
    }
    
    PROFESSIONAL = {
        "id": "professional",
        "name": "Professional",
        "price": 199,
        "price_id": "price_professional_monthly",
        "features": [
            "Full monitoring suite",
            "Unlimited predictions",
            "24/7 priority support",
            "90-day data retention",
            "Advanced analytics",
            "API access",
            "Custom integrations",
            "Team collaboration"
        ],
        "limits": {
            "predictions_per_month": -1,  # Unlimited
            "data_retention_days": 90,
            "users": 10
        }
    }
    
    ENTERPRISE = {
        "id": "enterprise",
        "name": "Enterprise",
        "price": 499,
        "price_id": "price_enterprise_monthly",
        "features": [
            "Everything in Professional",
            "Unlimited everything",
            "Dedicated support",
            "365-day data retention",
            "Custom ML models",
            "On-premise deployment",
            "SLA guarantee",
            "Training & onboarding"
        ],
        "limits": {
            "predictions_per_month": -1,
            "data_retention_days": 365,
            "users": -1  # Unlimited
        }
    }
    
    @classmethod
    def get_all_plans(cls) -> List[Dict[str, Any]]:
        """Get all subscription plans"""
        return [cls.FREE, cls.STARTER, cls.PROFESSIONAL, cls.ENTERPRISE]
    
    @classmethod
    def get_plan(cls, plan_id: str) -> Optional[Dict[str, Any]]:
        """Get specific plan by ID"""
        plans = {p["id"]: p for p in cls.get_all_plans()}
        return plans.get(plan_id)


class BillingService:
    """Stripe billing service"""
    
    def __init__(self):
        """Initialize billing service"""
        self.stripe = stripe
    
    def create_customer(self, email: str, name: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Create a new Stripe customer
        
        Args:
            email: Customer email
            name: Customer name
            metadata: Additional metadata
            
        Returns:
            Customer data
        """
        try:
            customer = self.stripe.Customer.create(
                email=email,
                name=name,
                metadata=metadata or {}
            )
            
            return {
                "customer_id": customer.id,
                "email": customer.email,
                "created": datetime.fromtimestamp(customer.created)
            }
        except Exception as e:
            return {"error": str(e)}
    
    def create_subscription(
        self,
        customer_id: str,
        price_id: str,
        trial_days: int = 0
    ) -> Dict[str, Any]:
        """
        Create a subscription for a customer
        
        Args:
            customer_id: Stripe customer ID
            price_id: Stripe price ID
            trial_days: Number of trial days
            
        Returns:
            Subscription data
        """
        try:
            subscription = self.stripe.Subscription.create(
                customer=customer_id,
                items=[{"price": price_id}],
                trial_period_days=trial_days if trial_days > 0 else None,
                payment_behavior="default_incomplete",
                expand=["latest_invoice.payment_intent"]
            )
            
            return {
                "subscription_id": subscription.id,
                "status": subscription.status,
                "current_period_end": datetime.fromtimestamp(subscription.current_period_end),
                "trial_end": datetime.fromtimestamp(subscription.trial_end) if subscription.trial_end else None
            }
        except Exception as e:
            return {"error": str(e)}
    
    def cancel_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """
        Cancel a subscription
        
        Args:
            subscription_id: Stripe subscription ID
            
        Returns:
            Cancellation data
        """
        try:
            subscription = self.stripe.Subscription.delete(subscription_id)
            
            return {
                "subscription_id": subscription.id,
                "status": subscription.status,
                "canceled_at": datetime.fromtimestamp(subscription.canceled_at)
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """
        Get subscription details
        
        Args:
            subscription_id: Stripe subscription ID
            
        Returns:
            Subscription data
        """
        try:
            subscription = self.stripe.Subscription.retrieve(subscription_id)
            
            return {
                "subscription_id": subscription.id,
                "status": subscription.status,
                "current_period_start": datetime.fromtimestamp(subscription.current_period_start),
                "current_period_end": datetime.fromtimestamp(subscription.current_period_end),
                "cancel_at_period_end": subscription.cancel_at_period_end
            }
        except Exception as e:
            return {"error": str(e)}
    
    def create_checkout_session(
        self,
        price_id: str,
        customer_id: Optional[str] = None,
        success_url: str = "http://localhost:8501/success",
        cancel_url: str = "http://localhost:8501/cancel"
    ) -> Dict[str, Any]:
        """
        Create a Stripe Checkout session
        
        Args:
            price_id: Stripe price ID
            customer_id: Optional customer ID
            success_url: Redirect URL on success
            cancel_url: Redirect URL on cancel
            
        Returns:
            Checkout session data
        """
        try:
            session = self.stripe.checkout.Session.create(
                mode="subscription",
                line_items=[{"price": price_id, "quantity": 1}],
                success_url=success_url,
                cancel_url=cancel_url,
                customer=customer_id
            )
            
            return {
                "session_id": session.id,
                "url": session.url
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_invoices(self, customer_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get customer invoices
        
        Args:
            customer_id: Stripe customer ID
            limit: Number of invoices to retrieve
            
        Returns:
            List of invoice data
        """
        try:
            invoices = self.stripe.Invoice.list(customer=customer_id, limit=limit)
            
            return [
                {
                    "invoice_id": inv.id,
                    "amount": inv.amount_due / 100,  # Convert from cents
                    "currency": inv.currency,
                    "status": inv.status,
                    "created": datetime.fromtimestamp(inv.created),
                    "pdf": inv.invoice_pdf
                }
                for inv in invoices.data
            ]
        except Exception as e:
            return [{"error": str(e)}]
    
    def create_portal_session(
        self,
        customer_id: str,
        return_url: str = "http://localhost:8501"
    ) -> Dict[str, Any]:
        """
        Create a customer portal session for managing subscriptions
        
        Args:
            customer_id: Stripe customer ID
            return_url: URL to return to after portal session
            
        Returns:
            Portal session data
        """
        try:
            session = self.stripe.billing_portal.Session.create(
                customer=customer_id,
                return_url=return_url
            )
            
            return {
                "url": session.url
            }
        except Exception as e:
            return {"error": str(e)}
