from fastapi import FastAPI
from app.database import Base, engine
from app import auth, chatroom, subscription, models, admin,user

app = FastAPI()
Base.metadata.create_all(bind=engine)

app.include_router(auth.router, prefix="/auth")
app.include_router(user.router, prefix="/user")
app.include_router(chatroom.router, prefix="/chatroom")
app.include_router(admin.router, prefix="/admin") #For view the data in the database
app.include_router(subscription.router)

### 13. celery_worker.py
from app.tasks import celery

if __name__ == "__main__":
    celery.start()