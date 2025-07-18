# from fastapi import APIRouter, Depends, HTTPException, Request,Header
# from app.config import settings
# import stripe
# from app import schemas, models, utils, database
# from sqlalchemy.orm import Session


# router = APIRouter()

# stripe.api_key = settings.STRIPE_SECRET_KEY

# @router.post("/subscribe/pro")
# def start_subscription():
#     session = stripe.checkout.Session.create(
#         payment_method_types=['card'],
#         line_items=[{
#             'price_data': {
#                 'currency': 'usd',
#                 'product_data': {'name': 'Pro Plan'},
#                 'unit_amount': 1000,
#             },
#             'quantity': 1,
#         }],
#         mode='subscription',
#         success_url='http://localhost:8000/success',
#         cancel_url='http://localhost:8000/cancel',
#     )
#     return {"checkout_url": session.url}


# #Handle Stripe webhook
# @router.post("/webhook/stripe")
# async def stripe_webhook(request: Request):
#     payload = await request.body()
#     sig_header = request.headers.get('stripe-signature')
#     try:
#         event = stripe.Webhook.construct_event(
#             payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
#         )
#     except stripe.error.SignatureVerificationError:
#         raise HTTPException(status_code=400, detail="Invalid signature")

#     # Handle event types (e.g., payment succeeded)
#     if event['type'] == 'checkout.session.completed':
#         # TODO: update user subscription here
#         pass

#     return {"status": "success"}

# #Get subscription tier


# @router.get("/subscription/status")
# def get_subscription_status(token: str = Header(...), db: Session = Depends(database.get_db)):
#     payload = utils.verify_token(token)
#     if not payload:
#         raise HTTPException(status_code=401, detail="Invalid token")
#     user = db.query(models.User).get(int(payload["sub"]))
#     return {"subscription": user.subscription}
# routes/subscription.py
from fastapi import APIRouter, Depends, Request, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.chatroom import get_current_user
from app.database import get_db
from app.models import User
from app.config import settings
import stripe
import hmac
import hashlib
import base64

router = APIRouter()

# Set Stripe secret key
stripe.api_key = settings.STRIPE_SECRET_KEY

#Initiates a Pro subscription via Stripe Checkout
@router.post("/subscribe/pro", status_code=200)
def start_subscription(user=Depends(get_current_user)):
    """
    Creates a Stripe Checkout Session for the Pro plan.
    Requires authenticated user.
    """
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {'name': 'Pro Plan'},
                    'unit_amount': 1000,  # $10.00
                    'recurring': {'interval': 'month'}
                },
                'quantity': 1,
            }],
            mode='subscription',
            metadata={"user_id": str(user.id)},
            success_url='http://localhost:8000/success',
            cancel_url='http://localhost:8000/cancel',
        )
        return {"checkout_url": session.url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#Stripe Handles Stripe webhook events (e.g., only) payment success/failure
@router.post("/webhook/stripe")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=sig_header,
            secret=settings.STRIPE_WEBHOOK_SECRET
        )
    except Exception as e:
        print("❌ Webhook signature error:", e)
        return JSONResponse(status_code=400, content={"error": str(e)})

    print("✅ Webhook event received:", event['type'])

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        print("➡️ Checkout Session Metadata:", session.get('metadata'))

        try:
            user_id = int(session['metadata']['user_id'])
            print("🔍 Looking up user ID:", user_id)
            user = db.query(User).filter(User.id == user_id).first()

            if user:
                print("✅ User found:", user.id)
                user.subscription = "Pro"
                db.commit()
                print("✅ Subscription updated to Pro")
            else:
                print("❌ User not found")
        except Exception as e:
            print("❌ Error updating subscription:", e)

    return {"status": "success"}


# Checks the user's current subscription tier atus (Basic or Pro)
@router.get("/subscription/status")
def get_subscription_status(user=Depends(get_current_user)):
    """
    Returns the user's current subscription tier (Basic or Pro)
    """
    return {"subscription_tier": user.subscription}