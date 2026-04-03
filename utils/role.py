from fastapi import HTTPException,status,Depends
from app.database import db_dependecies
from models.users import User
from utils.security import oauth2_scheme
from jose import jwt,JWTError

def get_current_user(db: db_dependecies,token: str = Depends(oauth2_scheme),):
    try:
        payload = jwt.decode(token, "SECRET_KEY", algorithms=["HS256"])
        email = payload.get("sub")

        user = db.query(User).filter(User.email == email).first()

        if user is None:
            raise HTTPException(status_code=401, detail="login first")
        return user

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

