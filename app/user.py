from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app import schemas, models, utils, database
from fastapi import Header

router = APIRouter()

#User me
#Authorization : Bearer <token> ->this is the form of adding the authorization
@router.get("/me", response_model=schemas.UserOut)
def get_me(request: Request, db: Session = Depends(database.get_db)):
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

    return user
