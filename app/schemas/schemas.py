# app/schemas/schemas.py
# Schemas = the shape of data coming IN to the API and going OUT.
# Think of them as contracts: "this is exactly what I expect / what I'll return"
# Pydantic automatically validates data and returns clear errors if it's wrong.

from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from app.models.models import TaskStatus, TaskPriority


# ─── USER SCHEMAS ────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    """What we need from the user to create an account"""
    username: str
    email: str
    password: str

    @field_validator("username")
    def username_must_be_valid(cls, v):
        if len(v) < 3:
            raise ValueError("Username must be at least 3 characters")
        if not v.isalnum():
            raise ValueError("Username must only contain letters and numbers")
        return v

    @field_validator("password")
    def password_must_be_strong(cls, v):
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        return v


class UserResponse(BaseModel):
    """What we send BACK when returning user info — never include the password!"""
    id: int
    username: str
    email: str
    is_active: bool

    class Config:
        from_attributes = True  # lets pydantic read SQLAlchemy model objects


# ─── AUTH SCHEMAS ─────────────────────────────────────────────────────────────

class Token(BaseModel):
    """The JWT token we return after a successful login"""
    access_token: str
    token_type: str  # always "bearer"


class TokenData(BaseModel):
    """Data we store inside the token"""
    username: Optional[str] = None


# ─── TASK SCHEMAS ─────────────────────────────────────────────────────────────

class TaskCreate(BaseModel):
    """What we need to create a new task"""
    title: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.todo
    priority: TaskPriority = TaskPriority.medium
    due_date: Optional[str] = None  # format: "YYYY-MM-DD"

    @field_validator("title")
    def title_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError("Title cannot be empty")
        return v.strip()


class TaskUpdate(BaseModel):
    """All fields optional — user can update just one field if they want"""
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[str] = None


class TaskResponse(BaseModel):
    """What we send back when returning a task"""
    id: int
    title: str
    description: Optional[str]
    status: TaskStatus
    priority: TaskPriority
    due_date: Optional[str]
    owner_id: int

    class Config:
        from_attributes = True
