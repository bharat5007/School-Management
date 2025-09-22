"""
Authentication Service Manager
"""
from datetime import datetime, timedelta
from typing import Optional

from fastapi import HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import settings
from app.constants.messages import ERROR_MESSAGES
from app.models.user import User
from app.schemas.user import UserCreate
from app.service_managers.user_service import UserService


class AuthService:
    """Authentication service manager"""

    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.user_service = UserService()

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Generate password hash"""
        return self.pwd_context.hash(password)

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )
        return encoded_jwt

    async def authenticate_user(
        self, db: AsyncSession, email: str, password: str
    ) -> Optional[User]:
        """Authenticate user by email and password"""
        user = await self.user_service.get_user_by_email(db, email)
        if not user:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        return user

    async def register_user(self, db: AsyncSession, user_data: UserCreate) -> User:
        """Register a new user"""
        # Check if user already exists
        existing_user = await self.user_service.get_user_by_email(db, user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ERROR_MESSAGES["USER_ALREADY_EXISTS"]
            )

        # Hash password and create user
        hashed_password = self.get_password_hash(user_data.password)
        user_dict = user_data.dict(exclude={"password"})
        user_dict["hashed_password"] = hashed_password

        return await self.user_service.create_user(db, user_dict)

    def decode_access_token(self, token: str) -> Optional[str]:
        """Decode JWT access token"""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            return payload.get("sub")
        except JWTError:
            return None
