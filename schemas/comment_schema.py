#    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
#     ticket_id: Mapped[int] = mapped_column(Integer, ForeignKey("tickets.id"))
#     user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
#     message: Mapped[str] = mapped_column(String)
#     created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now())

from pydantic import BaseModel
from  datetime import datetime

class CommentCreate(BaseModel):
    ticket_id:int
    message:str

class CommentResponse(BaseModel):
    id:int
    ticket_id:int
    user_id:int
    message:str
    created_at:datetime
