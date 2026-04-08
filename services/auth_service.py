import secrets


from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.users import User
from services.send_email import send_email
from utils.redis_connection import redis_client
from utils.security import get_password_hash, verify_password

OTP_EXPIRE_TIME = 300
OTP_ATTEMPT_LIMIT = 5

def generate_otp():
    return secrets.randbelow(900000) + 100000 

async def send_password_reset_otp(email: str, db: Session):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    otp = generate_otp()
    await redis_client.set(f"password_reset_otp:{email}", otp, ex=OTP_EXPIRE_TIME)
    send_email(
        to_email=email, 
        subject="Password Reset OTP", 
        body=f"Your OTP for password reset is: {otp}"
    )

async def verify_otp_and_reset_password(request, db: Session):
    email = request.email
    otp = request.otp
    new_password = request.new_password

    attempt_key = f"password_reset_attempts:{email}"
    attempts = await redis_client.get(attempt_key)
    attempts = int(attempts) if attempts else 0

    if attempts >= OTP_ATTEMPT_LIMIT:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Too many OTP attempts. Please try again later."
        )
    
    otp_key = f"password_reset_otp:{email}"
    stored_otp = await redis_client.get(otp_key)
    
    if not stored_otp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="OTP expired or not found"
        )
    if str(stored_otp) != str(otp):
        new_attempts = attempts + 1
        await redis_client.set(attempt_key, new_attempts, ex=OTP_EXPIRE_TIME)
        if new_attempts >= OTP_ATTEMPT_LIMIT:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many OTP attempts. Please try again later.",
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OTP"
        )

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    if verify_password(new_password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="New password cannot be the same as the current password"
        )
    
    user.password = get_password_hash(new_password[:72])
    db.commit()
    db.refresh(user)
    await redis_client.delete(otp_key)
    await redis_client.delete(attempt_key)
