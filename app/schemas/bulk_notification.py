"""
Bulk Notification Schemas for handling mass notifications efficiently
"""
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, EmailStr, validator

from app.constants.enums import (
    BulkProcessingStrategy,
    NotificationMode,
    NotificationPriority,
    NotificationType,
)


class BulkRecipient(BaseModel):
    """Individual recipient in bulk notification"""

    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    whatsapp: Optional[str] = None
    name: Optional[str] = None
    user_id: Optional[str] = None  # For tracking
    custom_data: Optional[Dict[str, Any]] = None  # Personalization data

    @validator("phone", "whatsapp")
    def validate_phone_format(cls, v):
        if v and not v.startswith("+"):
            raise ValueError("Phone number must include country code with + prefix")
        return v


class BulkEmailContent(BaseModel):
    """Bulk email content with personalization support"""

    subject: str
    html_body: Optional[str] = None
    text_body: Optional[str] = None
    sender_name: Optional[str] = None
    reply_to: Optional[EmailStr] = None

    # Bulk-specific fields
    use_bcc: bool = False  # Send as BCC (single email with hidden recipients)
    batch_size: int = 100  # How many recipients per batch
    personalization_enabled: bool = True  # Use recipient custom_data for templating

    # Template support
    template_id: Optional[str] = None
    default_template_data: Optional[Dict[str, Any]] = None

    # Attachments (shared across all recipients)
    attachments: Optional[List[Dict[str, str]]] = None
    headers: Optional[Dict[str, str]] = None


class BulkSMSContent(BaseModel):
    """Bulk SMS content with rate limiting support"""

    message: str
    sender_id: Optional[str] = None
    message_type: str = "transactional"

    # Bulk-specific fields
    batch_size: int = 50  # Messages per batch
    rate_limit_per_second: int = 10  # Max messages per second
    personalization_enabled: bool = True
    unicode_message: bool = False

    # Delivery options
    delivery_reports: bool = True
    validity_period: Optional[int] = None  # Minutes

    @validator("message")
    def validate_message_length(cls, v, values):
        """Validate SMS message length"""
        unicode_msg = values.get("unicode_message", False)
        max_length = 70 if unicode_msg else 160

        if len(v) > max_length:
            raise ValueError(f"SMS message too long. Max {max_length} characters")
        return v


class BulkWhatsAppContent(BaseModel):
    """Bulk WhatsApp content with template support"""

    message_type: str = "template"  # Bulk usually uses templates

    # Template-based content (recommended for bulk)
    template_name: Optional[str] = None
    template_language: str = "en"
    default_template_parameters: Optional[List[str]] = None

    # Text-based content (for smaller batches)
    text: Optional[str] = None

    # Bulk-specific settings
    batch_size: int = 20  # WhatsApp has stricter limits
    rate_limit_per_second: int = 5  # Conservative rate limit
    personalization_enabled: bool = True

    @validator("template_name", "text")
    def validate_content_by_type(cls, v, values):
        """Validate content based on message type"""
        message_type = values.get("message_type", "template")

        if message_type == "template" and not v and "template_name" in cls.__fields__:
            raise ValueError("Template message requires template_name")
        elif message_type == "text" and not v and "text" in cls.__fields__:
            raise ValueError("Text message requires text content")

        return v


class BulkNotificationContent(BaseModel):
    """Content for bulk notifications across different channels"""

    # Service-specific content
    email_content: Optional[BulkEmailContent] = None
    sms_content: Optional[BulkSMSContent] = None
    whatsapp_content: Optional[BulkWhatsAppContent] = None

    # Fallback content
    fallback_subject: Optional[str] = None
    fallback_message: str


class BulkNotificationRequest(BaseModel):
    """Main bulk notification request"""

    recipients: List[BulkRecipient]
    content: BulkNotificationContent
    channels: List[NotificationType]

    # Bulk processing settings
    mode: NotificationMode = NotificationMode.BULK
    processing_strategy: BulkProcessingStrategy = BulkProcessingStrategy.BATCHED
    priority: NotificationPriority = NotificationPriority.MEDIUM

    # Scheduling
    scheduled_at: Optional[datetime] = None
    spread_over_minutes: Optional[int] = None  # Spread delivery over time

    # Metadata and tracking
    campaign_id: Optional[str] = None
    metadata: Optional[Dict] = None

    @validator("recipients")
    def validate_recipients_count(cls, v):
        """Validate recipient count for bulk operations"""
        if len(v) < 2:
            raise ValueError("Bulk notifications require at least 2 recipients")
        if len(v) > 10000:
            raise ValueError("Maximum 10,000 recipients per bulk request")
        return v

    @validator("channels")
    def validate_channels_and_recipients(cls, v, values):
        """Ensure recipients have required contact info for channels"""
        if "recipients" in values:
            recipients = values["recipients"]

            for channel in v:
                valid_recipients = 0

                for recipient in recipients:
                    if channel == NotificationType.EMAIL and recipient.email:
                        valid_recipients += 1
                    elif channel == NotificationType.SMS and recipient.phone:
                        valid_recipients += 1
                    elif channel == NotificationType.WHATSAPP and recipient.whatsapp:
                        valid_recipients += 1

                if valid_recipients == 0:
                    raise ValueError(f"No recipients have {channel.value} contact info")

        return v


# Bulk-specific Kafka payload schemas
class BulkEmailKafkaPayload(BaseModel):
    """Bulk email payload for Kafka"""

    service_type: NotificationType = NotificationType.EMAIL
    notification_id: str
    batch_id: str
    correlation_id: str

    # Bulk email data
    recipients: List[Dict[str, Any]]  # Processed recipient data
    email_content: BulkEmailContent
    processing_strategy: BulkProcessingStrategy
    priority: NotificationPriority

    # Batch information
    batch_number: int
    total_batches: int
    total_recipients: int

    metadata: Optional[Dict] = None


class BulkSMSKafkaPayload(BaseModel):
    """Bulk SMS payload for Kafka"""

    service_type: NotificationType = NotificationType.SMS
    notification_id: str
    batch_id: str
    correlation_id: str

    # Bulk SMS data
    recipients: List[Dict[str, Any]]  # Phone numbers with personalization
    sms_content: BulkSMSContent
    processing_strategy: BulkProcessingStrategy
    priority: NotificationPriority

    # Rate limiting info
    rate_limit_per_second: int
    batch_number: int
    total_batches: int

    metadata: Optional[Dict] = None


class BulkWhatsAppKafkaPayload(BaseModel):
    """Bulk WhatsApp payload for Kafka"""

    service_type: NotificationType = NotificationType.WHATSAPP
    notification_id: str
    batch_id: str
    correlation_id: str

    # Bulk WhatsApp data
    recipients: List[Dict[str, Any]]  # WhatsApp numbers with template data
    whatsapp_content: BulkWhatsAppContent
    processing_strategy: BulkProcessingStrategy
    priority: NotificationPriority

    # Template and batching info
    batch_number: int
    total_batches: int
    estimated_cost: Optional[float] = None  # Cost estimation for batch

    metadata: Optional[Dict] = None


class BulkNotificationResponse(BaseModel):
    """Response for bulk notification requests"""

    notification_id: str
    campaign_id: Optional[str] = None
    status: str = "accepted"

    # Processing information
    total_recipients: int
    batches_created: Dict[str, int]  # {"email": 3, "sms": 5, "whatsapp": 2}
    estimated_completion_time: Optional[datetime] = None
    estimated_cost: Optional[Dict[str, float]] = None  # Cost per service

    message: str = "Bulk notification accepted and queued for processing"
