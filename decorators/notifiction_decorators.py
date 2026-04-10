from services.send_email import send_email
from functools import wraps
import inspect
from fastapi import HTTPException, status
from models.tickets import Ticket
from models.users import User
from schemas.ticket_schema import TicketStatus
from services.notification_service import notify_user


def notify_password_change(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        result = await func(*args, **kwargs)
        current_user = kwargs.get("current_user")
        db = kwargs.get("db")
        if current_user and db:
            notify_user(
                user_id=current_user.id,
                message="Your password has been changed successfully",
                db=db,
            )
        return result
    return wrapper

