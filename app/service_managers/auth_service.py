"""
Authentication Service Manager
"""

from datetime import datetime, timedelta

from fastapi import HTTPException, status

from app.config.settings import settings
from app.constants.messages import ERROR_MESSAGES
from app.database.sql_operations import sql_ops
from app.schemas.auth import LoginResponse, Token
from app.utils import create_access_token, get_password_hash, verify_password


class AuthService:
    async def authenticate_user(self, payload):
        email = payload.get("email")
        password = payload.get("password")
        user = await sql_ops.get_user_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user

    async def register_user(self, payload):
        username = payload.get("username")
        email = payload.get("email")
        password = payload.get("password")
        existing_user = await sql_ops.get_user_by_email(email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ERROR_MESSAGES["USER_ALREADY_EXISTS"],
            )

        # Hash password and create user
        hashed_password = get_password_hash(password)
        user_dict = {"username": username, "email": email, "password": hashed_password}
        user_dict["hashed_password"] = hashed_password

        return await sql_ops.create_user(user_dict)

    async def login_user(self, payload):
        user = await self.authenticate_user(payload)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=ERROR_MESSAGES["INVALID_CREDENTIALS"],
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Create access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )

        token = {
            "access_token": access_token,
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        }

        return {"user": user, "token": token}
