from fastapi import HTTPException, Depends
from app.database import db_dependecies
from models.users import User
from utils.security import oauth2_scheme
from jose import jwt, JWTError
from fastapi.security import HTTPAuthorizationCredentials


def get_current_user(
    db: db_dependecies,
    token: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
):
    raw_token = token.credentials
    print("token", raw_token)
    try:
        payload = jwt.decode(raw_token, "SECRET_KEY", algorithms=["HS256"])
        print("payload: ", payload)
        email = payload.get("sub")

        user = db.query(User).filter(User.email == email).first()

        if user is None:
            raise HTTPException(status_code=401, detail="login first")
        return user

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
