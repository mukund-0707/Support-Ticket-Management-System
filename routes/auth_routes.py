import re

from fastapi import APIRouter, Depends, HTTPException, status
from models.users import User
from utils.security import get_password_hash, verify_password, create_access_token
from app.database import db_dependecies, db_conn
from sqlalchemy.orm import Session
from schemas.user_schema import LoginForm, UserCreate, UserResponse

router = APIRouter(tags=["Auth"])


@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: db_dependecies):
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists"
        )
    new_user = User(
        name=user.name,
        email=user.email,
        password=get_password_hash(user.password[:72]),
        role=user.role.value,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/login")
def login(form_data: LoginForm = Depends(), db: Session = Depends(db_conn)):
    email_user = db.query(User).filter(User.email == form_data.email).first()
    if not email_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )
    if not verify_password(form_data.password, email_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )
    access_token = create_access_token(data={"sub": email_user.email})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "id": email_user.id,
    }
