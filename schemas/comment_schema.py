from pydantic import BaseModel
from datetime import datetime


class CommentCreate(BaseModel):
    ticket_id: int
    message: str


class CommentResponse(BaseModel):
    id: int
    ticket_id: int
    user_id: int
    message: str
    created_at: datetime
    updated_at: datetime
