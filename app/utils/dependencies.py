"""
FastAPI Dependencies
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants.messages import ERROR_MESSAGES
from app.database.connection import get_db
from app.models.user import User
from app.service_managers.auth_service import AuthService
from app.service_managers.user_service import UserService

security = HTTPBearer()
auth_service = AuthService()
user_service = UserService()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get current authenticated user"""

    # Decode token
    email = auth_service.decode_access_token(credentials.credentials)
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_MESSAGES["UNAUTHORIZED"],
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get user from database
    user = await user_service.get_user_by_email(db, email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_MESSAGES["UNAUTHORIZED"],
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES["USER_NOT_FOUND"]
        )
    return current_user
