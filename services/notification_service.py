import json

from sqlalchemy.orm import Session
from models.notification import Notification
from utils.ws_manager import manager


def notify_user(user_id: int, message: str, db: Session):
    if user_id <= 0:
        return None

    notification = Notification(user_id=user_id, message=message)
    db.add(notification)
    db.commit()
    db.refresh(notification)

    payload = json.dumps(
        {
            "id": notification.id,
            "user_id": notification.user_id,
            "message": notification.message,
            "is_read": notification.is_read,
            "created_at": notification.created_at.isoformat(),
        }
    )
    manager.schedule_send(user_id, payload)
    return notification
