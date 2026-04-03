from pydantic import BaseModel
from datetime import datetime
from enum import Enum
from typing import Optional

class TicketStatus(str,Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"

class TicketPriority(str,Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class TicketCreate(BaseModel):
    title:str
    description:str
    priority:TicketPriority

class TicketResponse(BaseModel):
    id:int
    title:str
    description:str
    priority:TicketPriority
    status:TicketStatus
    created_at:datetime
    updated_at:datetime


class TicketUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None