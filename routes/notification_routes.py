from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func

from app.database import db_dependecies
from models.notification import Notification
from models.users import User
from schemas.notification_schema import NotificationCountResponse, NotificationResponse
from utils.role import get_current_user

router = APIRouter(tags=["Notifications"])


@router.get("/notifications", response_model=list[NotificationResponse])
def list_notifications(
    db: db_dependecies,
    current_user: User = Depends(get_current_user),
    unread_only: bool = False,
    limit: int = 20,
    offset: int = 0,
):
    query = db.query(Notification).filter(Notification.user_id == current_user.id)
    if unread_only:
        query = query.filter(Notification.is_read.is_(False))
    return (
        query.order_by(Notification.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


@router.patch("/notifications/{notification_id}/read", response_model=NotificationResponse)
def mark_notification_as_read(
    notification_id: int,
    db: db_dependecies,
    current_user: User = Depends(get_current_user),
):
    notification = (
        db.query(Notification)
        .filter(
            Notification.id == notification_id, Notification.user_id == current_user.id
        )
        .first()
    )
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found"
        )
    notification.is_read = True
    db.commit()
    db.refresh(notification)
    return notification


@router.patch("/notifications/read-all")
def mark_all_notifications_as_read(
    db: db_dependecies,
    current_user: User = Depends(get_current_user),
):
    (
        db.query(Notification)
        .filter(Notification.user_id == current_user.id, Notification.is_read.is_(False))
        .update({"is_read": True}, synchronize_session=False)
    )
    db.commit()
    return {"message": "All notifications marked as read"}


@router.get("/notifications/unread-count", response_model=NotificationCountResponse)
def unread_notification_count(
    db: db_dependecies,
    current_user: User = Depends(get_current_user),
):
    unread_count = (
        db.query(func.count(Notification.id))
        .filter(Notification.user_id == current_user.id, Notification.is_read.is_(False))
        .scalar()
    )
    return {"unread_count": unread_count or 0}
