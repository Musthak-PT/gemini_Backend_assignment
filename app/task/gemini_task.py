# app/tasks/gemini_task.py
from app.config import settings
from app import models, database
from celery import Celery

celery = Celery("gemini_tasks", broker=settings.REDIS_URL)

@celery.task
def gemini_response(chatroom_id: int, user_message: str):
    gemini_reply = f"Gemini says: {user_message[::-1]}"  # mocked reply

    db = next(database.get_db())
    gemini_msg = models.Message(
        chatroom_id=chatroom_id,
        sender="gemini",
        content=gemini_reply
    )
    db.add(gemini_msg)
    db.commit()
    db.close()
