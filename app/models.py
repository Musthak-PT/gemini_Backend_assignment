from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class User(Base):
    __tablename__   = "users"
    id              = Column(Integer, primary_key=True, index=True)
    mobile          = Column(String, unique=True)
    otp             = Column(String)
    is_verified     = Column(Boolean, default=False)
    password        = Column(String, nullable=True)
    subscription    = Column(String, default="Basic")
    chatrooms       = relationship("Chatroom", back_populates="owner")


class Chatroom(Base):
    __tablename__   = "chatrooms"
    id              = Column(Integer, primary_key=True, index=True)
    name            = Column(String)
    user_id         = Column(Integer, ForeignKey("users.id"))
    created_at      = Column(DateTime, default=datetime.utcnow)
    owner           = relationship("User", back_populates="chatrooms")


class Message(Base):
    __tablename__   = "messages"
    id              = Column(Integer, primary_key=True, index=True)
    chatroom_id     = Column(Integer, ForeignKey("chatrooms.id"))
    sender          = Column(String)
    content         = Column(String)
    created_at      = Column(DateTime, default=datetime.utcnow)