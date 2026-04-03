from pydantic import BaseModel, EmailStr
from datetime import datetime
from enum import Enum


class Role(Enum):
    ADMIN = "admin"
    CUSTOMER = "customer"
    AGENT = "agent"


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: Role


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    created_at: datetime


class UserLogin(BaseModel):
    email: str
    password: str
