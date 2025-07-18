from fastapi import APIRouter, Depends, HTTPException, status,Request
from sqlalchemy.orm import Session
from app import schemas, models, utils, database
import random
from fastapi import Header
from pydantic import BaseModel


router = APIRouter()

def get_user_by_mobile(db, mobile):
    return db.query(models.User).filter(models.User.mobile == mobile).first()

@router.post("/signup")
def signup(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    db_user = get_user_by_mobile(db, user.mobile)
    if db_user:
        raise HTTPException(status_code=400, detail="User already exists")
    otp = str(random.randint(1000, 9999))
    new_user = models.User(mobile=user.mobile, otp=otp)
    db.add(new_user)
    db.commit()
    return {"otp": otp}  # mocked


@router.post("/send-otp")
def send_otp(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    user_obj = get_user_by_mobile(db, user.mobile)
    if not user_obj:
        raise HTTPException(status_code=404, detail="User not found")
    user_obj.otp = str(random.randint(1000, 9999))
    db.commit()
    return {"otp": user_obj.otp}


@router.post("/verify-otp", response_model=schemas.Token)
def verify_otp(data: schemas.OTPVerify, db: Session = Depends(database.get_db)):
    user = get_user_by_mobile(db, data.mobile)
    if user and user.otp == data.otp:
        user.is_verified = True
        db.commit()
        token = utils.create_access_token({"sub": str(user.id)})
        return {"access_token": token, "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Invalid OTP")


#Forgot password
@router.post("/forgot-password")
def forgot_password(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    db_user = get_user_by_mobile(db, user.mobile)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db_user.otp = str(random.randint(1000, 9999))
    db.commit()
    return {"otp": db_user.otp}

#Change password

class PasswordChange(BaseModel):
    new_password: str

@router.post("/change-password")
def change_password(data: PasswordChange,request: Request,db: Session = Depends(database.get_db)):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization header missing or malformed")
    
    token = auth_header.split(" ")[1]
    payload = utils.verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(models.User).get(int(payload["sub"]))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.password = data.new_password
    db.commit()

    return {"message": "Password updated"}