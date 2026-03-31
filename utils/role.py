from fastapi import HTTPException,status,Depends
from app.database import db_dependecies
from models.users import User
from utils.security import oauth2_scheme
from jose import jwt,JWTError

def get_current_user(db: db_dependecies,token: str = Depends(oauth2_scheme),):
    try:
        payload = jwt.decode(token, "SECRET_KEY", algorithms=["HS256"])
        email = payload.get("sub")
        role = payload.get("role")

        user = db.query(User).filter(User.email == email).first()

        if user is None:
            raise HTTPException(status_code=401, detail="login first")
        return user

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# def admin_only(current_user: User = Depends(get_current_user)):
#     if current_user.role != "admin":
#         raise HTTPException(
#             status_code=403,
#             detail="Only admin allowed"
#         )
#     return current_user

# def customer_only(current_user: User = Depends(get_current_user)):
#     if current_user.role != "customer":
#         raise HTTPException(
#             status_code=403,
#             detail="Only customer allowed"
#         )
#     return current_user

# def agent_only(current_user: User = Depends(get_current_user)):
    if current_user.role != "agent":
        raise HTTPException(
            status_code=403,
            detail="Only agent allowed"
        )
    return current_user