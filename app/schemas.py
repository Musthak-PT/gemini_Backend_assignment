from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class UserCreate(BaseModel):
    mobile: str

class OTPVerify(BaseModel):
    mobile: str
    otp: str

class Token(BaseModel):
    access_token: str
    token_type: str

class ChatroomCreate(BaseModel):
    name: str

class MessageCreate(BaseModel):
    content: str


#Output get schemas
class UserOut(BaseModel):
    id: int
    mobile: str
    is_verified: bool
    subscription: str

    class Config:
        orm_mode = True

class ChatroomOut(BaseModel):
    id: int
    name: str
    user_id: int
    created_at: datetime

    class Config:
        orm_mode = True

class MessageOut(BaseModel):
    id: int
    chatroom_id: int
    sender: str
    content: str
    created_at: datetime

    class Config:
        orm_mode = True