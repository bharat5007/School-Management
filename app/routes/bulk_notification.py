"""
Bulk Notification Routes
"""
from fastapi import APIRouter, HTTPException, Request, status
from loguru import logger

from app.decorators import auth_required
from app.schemas.bulk_notification import BulkNotificationRequest
from app.service_managers.bulk_notification_service import BulkNotificationService

router = APIRouter()
bulk_notification_service = BulkNotificationService()


@router.post("/bulk-send")
@auth_required()
async def send_bulk_notification(
    request: Request, bulk_request: BulkNotificationRequest, current_user=None
):
    response = await bulk_notification_service.process_bulk_notification(bulk_request)
    return response
