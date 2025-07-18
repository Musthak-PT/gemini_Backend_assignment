from app.config import settings
from app import models, database
from celery import Celery
import httpx

celery = Celery(__name__, broker=settings.REDIS_URL)

@celery.task
def gemini_response(chatroom_id: int, user_message: str):
    # Simulate call to Gemini API
    gemini_reply = f"Gemini says: {user_message[::-1]}"  # mock response by reversing

    # Save Gemini response in DB
    db = next(database.get_db())
    gemini_msg = models.Message(
        chatroom_id=chatroom_id,
        sender="gemini",
        content=gemini_reply
    )
    db.add(gemini_msg)
    db.commit()
    db.close()
