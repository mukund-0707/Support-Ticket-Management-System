from datetime import datetime
from typing import Optional
from sqlalchemy import ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class Ticket(Base):
    __tablename__ = "tickets"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String, index=True)
    description: Mapped[str] = mapped_column(String)
    priority: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String, default="open")
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey("categories.id"))
    created_by: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    assigned_to: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=True
    )
    last_reminder_sent_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
