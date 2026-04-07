from pydantic import BaseModel, EmailStr
from datetime import datetime
from enum import Enum
from fastapi import Form


class LoginForm:
    def __init__(self, email: str = Form(...), password: str = Form(...)):
        self.email = email
        self.password = password


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
    is_active: bool


class UserLogin(BaseModel):
    email: str
    password: str
