"""
Notification Routes
"""
from fastapi import APIRouter, HTTPException, Request, status
from loguru import logger

from app.decorators import auth_required
from app.schemas.notification import NotificationRequest, NotificationResponse
from app.service_managers.notification_service import NotificationService

router = APIRouter()
notification_service = NotificationService()


@router.post("/send", response_model=NotificationResponse)
@auth_required()
async def send_notification(
    request: Request, notification_request: NotificationRequest, current_user=None
) -> NotificationResponse:
    """
    Send notification through multiple channels (email, SMS, WhatsApp)

    This endpoint follows the notification flow:
    1. Receives notification request
    2. Prepares array of services to use
    3. Extracts services for forwarding
    4. Prepares payload for Kafka

    Requires authentication.
    """
    try:
        logger.info(f"Notification request from user {current_user.username}")

        # Process the notification request
        response = await notification_service.process_notification_request(
            notification_request
        )

        logger.info(f"Notification {response.notification_id} processed successfully")
        return response

    except Exception as e:
        logger.error(f"Error processing notification: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing notification: {str(e)}",
        )
