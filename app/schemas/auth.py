"""
Authentication Pydantic Schemas
"""
from pydantic import BaseModel

from app.schemas.user import UserResponse


class Token(BaseModel):
    """Token response schema"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class LoginResponse(BaseModel):
    """Login response schema"""
    user: UserResponse
    token: Token
