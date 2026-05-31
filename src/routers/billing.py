import os
import stripe
from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from src.database.connection import get_db
from src.database.models import Organisation, User
from src.routers.auth import verify_token

router = APIRouter(prefix="/billing", tags=["billing"])

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

PRICE_IDS = {
    "starter":      os.getenv("STRIPE_STARTER_PRICE_ID"),
    "professional": os.getenv("STRIPE_PROFESSIONAL_PRICE_ID"),
    "enterprise":   os.getenv("STRIPE_ENTERPRISE_PRICE_ID"),
}

TIER_LIMITS = {
    "free":         5,
    "starter":      50,
    "professional": None,
    "enterprise":   None,
}


@router.get("/plans")
def get_plans():
    return {
        "plans": [
            {
                "id": "free",
                "name": "Free",
                "price": 0,
                "currency": "eur",
                "assessments": 5,
                "features": [
                    "5 assessments per month",
                    "EU AI Act risk classification",
                    "Basic risk tier output",
                ]
            },
            {
                "id": "starter",
                "name": "Starter",
                "price": 4900,
                "currency": "eur",
                "assessments": 50,
                "features": [
                    "50 assessments per month",
                    "EU AI Act risk classification",
                    "GDPR DPIA generation",
                    "OWASP LLM Top 10 check",
                    "NIST AI RMF mapping",
                    "PDF compliance reports",
                    "Assessment history",
                ]
            },
            {
                "id": "professional",
                "name": "Professional",
                "price": 14900,
                "currency": "eur",
                "assessments": -1,
                "features": [
                    "Unlimited assessments",
                    "All Starter features",
                    "RAG compliance assistant",
                    "Regulatory monitoring",
                    "LangGraph compliance agent",
                    "5 organisation users",
                ]
            },
            {
                "id": "enterprise",
                "name": "Enterprise",
                "price": 49900,
                "currency": "eur",
                "assessments": -1,
                "features": [
                    "Unlimited assessments",
                    "All Professional features",
                    "Direct API access",
                    "Custom classification rules",
                    "SLA guarantee",
                    "Unlimited users",
                ]
            },
        ]
    }


@router.post("/create-checkout-session")
def create_checkout_session(
    body: dict,
    current_user: User = Depends(verify_token),
    db: Session = Depends(get_db)
):
    plan = body.get("plan")
    if plan not in PRICE_IDS or not PRICE_IDS[plan]:
        raise HTTPException(status_code=400, detail="Invalid plan")

    org = db.query(Organisation).filter(
        Organisation.id == current_user.org_id
    ).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organisation not found")

    # create Stripe customer on first checkout, reuse on subsequent ones
    if not org.stripe_customer_id:
        customer = stripe.Customer.create(
            email=current_user.email,
            name=org.name,
            metadata={"org_id": str(org.id)}
        )
        org.stripe_customer_id = customer.id
        db.commit()

    frontend_url = os.getenv("APP_URL", "http://localhost:5173")

    session = stripe.checkout.Session.create(
        customer=org.stripe_customer_id,
        payment_method_types=["card"],
        line_items=[{"price": PRICE_IDS[plan], "quantity": 1}],
        mode="subscription",
        success_url=f"{frontend_url}/billing/success?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{frontend_url}/billing/cancelled",
        metadata={"org_id": str(org.id), "plan": plan}
    )
    return {"checkout_url": session.url}


@router.post("/create-portal-session")
def create_portal_session(
    current_user: User = Depends(verify_token),
    db: Session = Depends(get_db)
):
    org = db.query(Organisation).filter(
        Organisation.id == current_user.org_id
    ).first()
    if not org or not org.stripe_customer_id:
        raise HTTPException(status_code=404, detail="No billing account found")

    frontend_url = os.getenv("APP_URL", "http://localhost:5173")

    session = stripe.billing_portal.Session.create(
        customer=org.stripe_customer_id,
        return_url=f"{frontend_url}/dashboard"
    )
    return {"portal_url": session.url}


@router.get("/subscription")
def get_subscription(
    current_user: User = Depends(verify_token),
    db: Session = Depends(get_db)
):
    org = db.query(Organisation).filter(
        Organisation.id == current_user.org_id
    ).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organisation not found")

    limit = TIER_LIMITS.get(org.subscription_tier, 5)

    return {
        "tier": org.subscription_tier,
        "status": org.subscription_status,
        "assessments_used": org.assessment_count_this_month,
        "assessments_limit": limit,
        "unlimited": limit is None,
    }


@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, WEBHOOK_SECRET
        )
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    event_type = event["type"]
    data = event["data"]["object"]

    if event_type in ("customer.subscription.created",
                      "customer.subscription.updated"):
        customer_id = data["customer"]
        status = data["status"]
        subscription_id = data["id"]

        # map Stripe price ID back to our internal tier name
        price_id = data["items"]["data"][0]["price"]["id"]
        tier = "free"
        for t, pid in PRICE_IDS.items():
            if pid == price_id:
                tier = t
                break

        org = db.query(Organisation).filter(
            Organisation.stripe_customer_id == customer_id
        ).first()
        if org:
            org.subscription_tier = tier
            org.subscription_status = status
            org.stripe_subscription_id = subscription_id
            db.commit()

    elif event_type == "customer.subscription.deleted":
        customer_id = data["customer"]
        org = db.query(Organisation).filter(
            Organisation.stripe_customer_id == customer_id
        ).first()
        if org:
            org.subscription_tier = "free"
            org.subscription_status = "cancelled"
            org.stripe_subscription_id = None
            db.commit()

    elif event_type == "invoice.payment_failed":
        customer_id = data["customer"]
        org = db.query(Organisation).filter(
            Organisation.stripe_customer_id == customer_id
        ).first()
        if org:
            org.subscription_status = "past_due"
            db.commit()

    return JSONResponse({"received": True})
