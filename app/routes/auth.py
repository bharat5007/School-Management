"""
Authentication Routes
"""
from fastapi import APIRouter, Request

from app.service_managers.auth_service import AuthService

router = APIRouter()
auth_service = AuthService()


@router.post("/sign_up")
async def register(request: Request):
    payload = await request.json()

    response = await auth_service.register_user(payload)
    return response


@router.post("/login")
async def login(request: Request):
    payload = await request.json()

    response = await auth_service.login_user(payload)
    return response
