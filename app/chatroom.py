from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app import database, models, schemas, utils
import redis
import json
from app.config import settings
from app.tasks import gemini_response

router = APIRouter()
# r = redis.Redis.from_url(settings.REDIS_URL)
r = redis.Redis.from_url(
    settings.REDIS_URL,
    decode_responses=True
)
#Authorization common function
def get_current_user(request: Request, db: Session = Depends(database.get_db)):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization header missing or malformed")

    token = auth_header.split(" ")[1]
    data = utils.verify_token(token)
    if not data:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(models.User).get(int(data["sub"]))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user

#For the creation of chatroom
@router.post("/", response_model=dict)
def create_chatroom(payload: schemas.ChatroomCreate, user=Depends(get_current_user), db=Depends(database.get_db)):
    chat = models.Chatroom(name=payload.name, owner=user)
    db.add(chat)
    db.commit()
    return {"id": chat.id, "name": chat.name}

#Listing of chatroom
@router.get("/")
def list_chatrooms(user=Depends(get_current_user), db=Depends(database.get_db)):
    print("Authenticated user:", user.id)
    cache_key = f"chatrooms:{user.id}"
    
    if r.exists(cache_key):
        print("Returning from cache")
        return json.loads(r.get(cache_key))

    chats = db.query(models.Chatroom).filter(models.Chatroom.user_id == user.id).all()
    print("DB returned:", chats)
    
    data = [{"id": c.id, "name": c.name} for c in chats]
    r.set(cache_key, json.dumps(data), ex=600)
    return data


#Retrieve specific chatroom
@router.get("/{id}", response_model=schemas.ChatroomOut)
def get_chatroom(id: int, user=Depends(get_current_user), db: Session = Depends(database.get_db)):
    chat = db.query(models.Chatroom).filter_by(id=id, user_id=user.id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chatroom not found")
    return chat


#Send message & get Gemini response (queue)
@router.post("/{id}/message", response_model=schemas.MessageOut)
def send_message(id: int, msg: schemas.MessageCreate, user=Depends(get_current_user), db: Session = Depends(database.get_db)):
    chatroom = db.query(models.Chatroom).filter_by(id=id, user_id=user.id).first()
    if not chatroom:
        raise HTTPException(status_code=404, detail="Chatroom not found")

    # Save user message
    message = models.Message(chatroom_id=chatroom.id, sender="user", content=msg.content)
    db.add(message)
    db.commit()
    db.refresh(message)

    # Trigger Gemini AI reply (background task)
    gemini_response.delay(chatroom.id, msg.content)

    return message



