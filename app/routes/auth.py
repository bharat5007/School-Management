"""
Authentication Routes
"""
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import settings
from app.constants.messages import ERROR_MESSAGES, SUCCESS_MESSAGES
from app.database.connection import get_db
from app.schemas.auth import LoginResponse, Token
from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.service_managers.auth_service import AuthService

router = APIRouter()
auth_service = AuthService()


@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user"""
    try:
        user = await auth_service.register_user(db, user_data)
        return UserResponse.from_orm(user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_MESSAGES["INTERNAL_SERVER_ERROR"]
        )


@router.post("/login", response_model=LoginResponse)
async def login(
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """Login user and return access token"""
    user = await auth_service.authenticate_user(
        db, credentials.email, credentials.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_MESSAGES["INVALID_CREDENTIALS"],
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_service.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    token = Token(
        access_token=access_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

    return LoginResponse(
        user=UserResponse.from_orm(user),
        token=token
    )
