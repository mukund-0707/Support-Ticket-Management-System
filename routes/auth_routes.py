from fastapi import APIRouter, Depends, HTTPException, status
from models.users import User
from services.auth_service import send_password_reset_otp, verify_otp_and_reset_password
from utils.security import get_password_hash, verify_password, create_access_token
from utils.role import get_current_user
from app.database import db_dependecies, db_conn
from sqlalchemy.orm import Session
from schemas.user_schema import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    LoginForm,
    UserCreate,
    UserResponse,
    VerifyOtpResetRequest,
)
from services.notification_service import notify_user

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
    if new_user.role == "customer":
        notify_user(new_user.id, "Welcome to the Ticketing System!", db)
    elif new_user.role == "agent":
        notify_user(new_user.id, "Welcome to the Ticketing System! You are now an agent.", db)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user role"
        )
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


@router.post("/forgot-password")
async def forgot_password(
    request: ForgotPasswordRequest, db: Session = Depends(db_conn)
):
    await send_password_reset_otp(request.email, db)
    user = db.query(User).filter(User.email == request.email).first()
    if request.email:
        notify_user(
            user_id=user.id if user else 0,
            message="OTP sent to your email for password reset",
            db=db,
        )
    return {"message": "OTP sent to email"}


@router.post("/verify-otp-reset-password")
async def reset_password(
    request: VerifyOtpResetRequest, db: Session = Depends(db_conn)
):
    await verify_otp_and_reset_password(request, db)
    if request.email:
        user = db.query(User).filter(User.email == request.email).first()
        notify_user(
            user_id=user.id if user else 0,
            message="Your password has been reset successfully",
            db=db,
        )
    return {"message": "Password reset successful"}


@router.post("/change-password")
def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(db_conn),
):
    if not verify_password(request.current_password, current_user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )
    if verify_password(request.new_password, current_user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password cannot be the same as the current password",
        )
    current_user.password = get_password_hash(request.new_password[:72])
    db.commit()
    
    if current_user:
        notify_user(
            user_id=current_user.id,
            message="Your password has been changed successfully",
            db=db,
        )
        
    return {"message": "Password changed successfully"}
