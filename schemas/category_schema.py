from pydantic import BaseModel
from datetime import datetime


class CategoryCreate(BaseModel):
    name: str
    description: str


class CategoryResponse(BaseModel):
    id: int
    name: str
    description: str
    created_at: datetime
    updated_at: datetime
