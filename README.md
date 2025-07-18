# Gemini Backend Clone - Kuvaka Tech Assignment

A scalable backend system inspired by Google Gemini Chat, supporting:
- OTP-based authentication
- AI-powered conversations via Gemini API
- Chatroom and message management
- Subscription plans via Stripe
- Redis cache & Celery queue for async processing

---------------------------------------------------------------------------------------------------------------------

## Tech Stack

| Component       | Technology             |
|----------------|------------------------|
| Backend         | FastAPI                |
| Database        | PostgreSQL             |
| Cache/Queue     | Redis                  |
| Task Queue      | Celery                 |
| AI Integration  | Google Gemini API      |
| Payments        | Stripe (Test Mode)     |
| Auth            | JWT + OTP (Simulated)  |
| Docs / Testing  | Postman, Swagger       |


---------------------------------------------------------------------------------------------------------------------


## Setup & Run Instructions

### 🛠 Prerequisites
- Python 3.10+
-Docker + Docker Compose installed
- PostgreSQL 13+
- Redis
- [Stripe CLI (for webhook testing)](https://stripe.com/docs/stripe-cli)
- Google Gemini API Key

---------------------------------------------------------------------------------------------------------------------

### 🔧 Installation Steps

# Clone the repo
git clone https://github.com/yourusername/gemini-backend-clone.git
cd gemini-backend-clone

# Create virtualenv
python -m venv venv
source venv/bin/activate

## Start the Project
docker-compose up --build

# Install dependencies
pip install -r requirements.txt

# Create .env file (edit as needed)
cp .env.example .env

# Start Redis server (if not already running)
redis-server

# Start Celery worker
docker exec -it gemini_backend-backend-1 celery -A app.tasks worker --loglevel=info

# Run the FastAPI app
docker-compose up --build

---------------------------------------------------------------------------------------------------------------------
## Architecture Overview

User → Auth (OTP + JWT) → Chatroom → Message → Gemini API
                              ↓
                    Subscription via Stripe
                              ↓
                    Async Tasks via Celery
                              ↓
                       Caching via Redis

FastAPI handles routing, auth, and core business logic.
PostgreSQL stores users, chatrooms, and messages.
Redis acts as both cache (e.g., chatroom listing) and Celery broker.
Celery handles async tasks like sending messages to Gemini API or webhook processing.
Stripe handles payments and subscriptions.
Google Gemini API is used to generate AI-powered responses to user messages.


---------------------------------------------------------------------------------------------------------------------
# Queue System (Celery)
We use Celery with Redis to offload:
    AI message processing
    Stripe webhook events
    Email/SMS (future scope)

---------------------------------------------------------------------------------------------------------------------

# Gemini API Integration
We use Google's Gemini Pro via REST.

Messages sent by user are sent to Gemini API in the background (via Celery).
Gemini's response is saved as a new message in the chatroom.

Example Flow
    User sends: "Hello, what's the weather?"
    API queues the message to Celery
    Celery calls Gemini API
    Gemini response is stored & sent to user

---------------------------------------------------------------------------------------------------------------------

##  API Endpoints & Payloads
1. User Signup (Register)
URL: http://localhost:8000/auth/signup

Method: POST

Payload:
{
  "mobile": "8989898989"
}

2. Send OTP
URL: http://localhost:8000/auth/send-otp

Method: POST

Payload:
{
  "mobile": "8989898989"
}


3. Verify OTP
URL: http://localhost:8000/auth/verify-otp

Method: POST

Payload:

{
  "mobile": "8989898989",
  "otp": "1318"
}
Response:
{
  "access_token": "<JWT_ACCESS_TOKEN>",
  "token_type": "bearer"
}

4. Forgot Password
URL: http://localhost:8000/auth/forgot-password

Method: POST

Payload:

{
  "mobile": "8989898989"
}

5. Change Password
URL: http://localhost:8000/auth/change-password

Method: POST

Headers:

Authorization: Bearer <access_token>

Payload:

{
  "new_password": "strongpass123"
}


6. Get Current User
URL: http://localhost:8000/user/me

Method: GET

Headers:

Authorization: Bearer <access_token>

7. Create Chatroom
URL: http://localhost:8000/chatroom

Method: POST

Headers:
Authorization: Bearer <access_token>

Payload:

{
  "name": "AI Assistant"
}

8. Get All Chatrooms
URL: http://localhost:8000/chatroom

Method: GET

Headers:
Authorization: Bearer <access_token>

9. Get Chatroom by ID
URL: http://localhost:8000/chatroom/<id>

Method: GET

Headers:
Authorization: Bearer <access_token>

10. Send a Message
URL: http://localhost:8000/chatroom/<id>/message

Method: POST

Headers:
Authorization: Bearer <access_token>

Payload:
{
  "content": "Hello, how can I track my order?"
}

11. Start Pro Subscription (via Stripe Checkout)
URL: http://localhost:8000/subscribe/pro

Method: GET

Headers:
Authorization: Bearer <access_token>

Response:
{
  "checkout_url": "<Stripe Checkout URL>"
}

12. Handle Stripe Webhooks
This endpoint handles Stripe webhook events such as successful or failed payments. To test locally:

-Install Stripe CLI.

-Run the following command:
stripe listen --forward-to localhost:8000/webhook/stripe

Upon successful payment, the subscription tier will automatically upgrade from Basic to Pro.

13. Check Subscription Status
URL: http://localhost:8000/subscription/status

Method: GET

Headers:
Authorization: Bearer <access_token>

Response:
{
  "subscription_tier": "Pro"
}


## .env Configuration
----------------------
Make sure to configure the following environment variables in your .env file:

SECRET_KEY=supersecretkey
REDIS_URL=redis://redis:6379
# Stripe Configuration
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
STRIPE_WEBHOOK_SECRET=whsec_your_stripe_webhook_secret
# Gemini API
GEMINI_API_KEY=your_gemini_api_key_here
# Database (PostgreSQL)
DATABASE_URL=postgresql://postgres:postgres@db:5432/gemini_db
