"""
User Pydantic Schemas
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, validator

from app.constants.enums import UserRole, UserStatus


class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    username: str
    first_name: str
    last_name: str
    is_active: bool = True
    role: UserRole = UserRole.USER
    status: UserStatus = UserStatus.ACTIVE


class UserCreate(UserBase):
    """User creation schema"""
    password: str

    @validator("password")
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return v

    @validator("username")
    def validate_username(cls, v):
        if len(v) < 3:
            raise ValueError("Username must be at least 3 characters long")
        return v


class UserUpdate(BaseModel):
    """User update schema"""
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: Optional[bool] = None
    role: Optional[UserRole] = None
    status: Optional[UserStatus] = None


class UserResponse(UserBase):
    """User response schema"""
    id: int
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """User login schema"""
    email: EmailStr
    password: str
