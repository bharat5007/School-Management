"""
Bulk Notification Routes
"""
from fastapi import APIRouter, HTTPException, Request, status
from loguru import logger

from app.decorators import admin_or_moderator_required, auth_required
from app.schemas.bulk_notification import (
    BulkNotificationRequest,
    BulkNotificationResponse,
)
from app.service_managers.bulk_notification_service import BulkNotificationService

router = APIRouter()
bulk_notification_service = BulkNotificationService()


@router.post("/bulk-send", response_model=BulkNotificationResponse)
@admin_or_moderator_required
async def send_bulk_notification(
    request: Request, bulk_request: BulkNotificationRequest, current_user=None
) -> BulkNotificationResponse:
    """
    Send bulk notifications to multiple recipients

    This endpoint handles:
    - Email: Can use BCC for efficiency or individual sends with personalization
    - SMS: Batched with rate limiting (typically 10-50 per second)
    - WhatsApp: Smaller batches with templates (typically 5-20 per second)

    Requires admin or moderator role due to potential high volume and cost.

    Features:
    - Automatic batching based on service limits
    - Rate limiting for SMS/WhatsApp
    - Cost estimation
    - Personalization support
    - Processing strategy selection
    """
    try:
        logger.info(
            f"Bulk notification request from {current_user.username} "
            f"for {len(bulk_request.recipients)} recipients"
        )

        # Validate bulk request size based on user role
        max_recipients = 10000 if current_user.role == "admin" else 1000
        if len(bulk_request.recipients) > max_recipients:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Maximum {max_recipients} recipients allowed for {current_user.role} role",
            )

        # Process the bulk notification
        response = await bulk_notification_service.process_bulk_notification(
            bulk_request
        )

        logger.info(
            f"Bulk notification {response.notification_id} processed: "
            f"{response.total_recipients} recipients, "
            f"{sum(response.batches_created.values())} batches created"
        )

        return response

    except Exception as e:
        logger.error(f"Error processing bulk notification: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing bulk notification: {str(e)}",
        )


@router.get("/bulk-limits")
@auth_required()
async def get_bulk_limits(request: Request, current_user=None):
    """
    Get bulk notification limits and recommendations for current user
    """
    limits = {
        "max_recipients": 10000 if current_user.role == "admin" else 1000,
        "recommended_batch_sizes": {"email": 100, "sms": 50, "whatsapp": 20},
        "rate_limits_per_second": {"email": 50, "sms": 10, "whatsapp": 5},
        "estimated_costs_per_message": {
            "email": 0.0001,
            "sms": 0.01,
            "whatsapp": 0.005,
        },
    }

    return limits
