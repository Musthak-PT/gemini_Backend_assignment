# app/admin.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app import models, schemas
from app.database import get_db

router = APIRouter()

# -------- USERS --------
@router.get("/users", response_model=List[schemas.UserOut])
def get_all_users(db: Session = Depends(get_db)):
    return db.query(models.User).all()

# -------- CHATROOMS --------
@router.get("/chatrooms", response_model=List[schemas.ChatroomOut])
def get_all_chatrooms(db: Session = Depends(get_db)):
    return db.query(models.Chatroom).all()

# -------- MESSAGES --------
@router.get("/messages", response_model=List[schemas.MessageOut])
def get_all_messages(db: Session = Depends(get_db)):
    return db.query(models.Message).all()
