"""
Notification Schemas
"""
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, EmailStr, validator

from app.constants.enums import NotificationType


class NotificationRecipient(BaseModel):
    """Notification recipient information"""

    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    whatsapp: Optional[str] = None
    name: Optional[str] = None

    @validator("phone", "whatsapp")
    def validate_phone_format(cls, v):
        if v and not v.startswith("+"):
            raise ValueError("Phone number must include country code with + prefix")
        return v


class NotificationContent(BaseModel):
    """Notification content for different channels"""

    subject: Optional[str] = None  # For email
    message: str
    template_id: Optional[str] = None
    template_data: Optional[Dict] = None


class NotificationRequest(BaseModel):
    """Main notification request payload"""

    recipient: NotificationRecipient
    content: NotificationContent
    channels: List[NotificationType]  # Which services to use (email, sms, whatsapp)
    scheduled_at: Optional[datetime] = None  # For future scheduling
    metadata: Optional[Dict] = None

    @validator("channels")
    def validate_channels_and_recipient(cls, v, values):
        """Ensure recipient has contact info for requested channels"""
        if "recipient" in values:
            recipient = values["recipient"]

            if NotificationType.EMAIL in v and not recipient.email:
                raise ValueError("Email channel requires recipient email")
            if NotificationType.SMS in v and not recipient.phone:
                raise ValueError("SMS channel requires recipient phone")
            if NotificationType.WHATSAPP in v and not recipient.whatsapp:
                raise ValueError("WhatsApp channel requires recipient WhatsApp number")

        return v


class ServicePayload(BaseModel):
    """Individual service payload for Kafka"""

    service_type: NotificationType
    recipient_info: Dict
    content: NotificationContent
    metadata: Optional[Dict] = None
    correlation_id: str  # To track across services


class KafkaNotificationPayload(BaseModel):
    """Final payload structure sent to Kafka"""

    notification_id: str
    services: List[ServicePayload]
    original_request: NotificationRequest
    created_at: datetime
    scheduled_at: Optional[datetime] = None


class NotificationResponse(BaseModel):
    """Response after processing notification request"""

    notification_id: str
    status: str = "accepted"
    services_to_process: List[NotificationType]
    estimated_delivery: Optional[datetime] = None
    message: str = "Notification request accepted and queued for processing"


class EmailContent(BaseModel):
    to: List[EmailStr]
    cc: Optional[List[EmailStr]] = None
    bcc: Optional[List[EmailStr]] = None
    subject: str
    html_body: Optional[str] = None
    text_body: Optional[str] = None
    reply_to: Optional[EmailStr] = None
    sender_name: Optional[str] = None
    attachments: Optional[List[Dict[str, str]]] = None
    headers: Optional[Dict[str, str]] = None
    template_id: Optional[str] = None
    template_data: Optional[Dict[str, Any]] = None


class SMSContent(BaseModel):
    to: str  # Phone number with country code
    message: str
    sender_id: Optional[str] = None  # Custom sender ID/name
    message_type: str = "transactional"  # transactional, promotional, otp
    delivery_reports: bool = True
    validity_period: Optional[int] = None  # Minutes
    flash_sms: bool = False
    unicode_message: bool = False

    @validator("message")
    def validate_message_length(cls, v, values):
        """Validate SMS message length"""
        unicode_msg = values.get("unicode_message", False)
        max_length = 70 if unicode_msg else 160

        if len(v) > max_length:
            raise ValueError(
                f'SMS message too long. Max {max_length} characters for {"unicode" if unicode_msg else "standard"} message'
            )
        return v

    @validator("to")
    def validate_phone_number(cls, v):
        if not v.startswith("+"):
            raise ValueError("Phone number must include country code with + prefix")
        return v


class WhatsAppContent(BaseModel):
    """WhatsApp-specific content structure"""

    to: str  # WhatsApp number with country code
    message_type: str = "text"  # text, template, media, interactive

    # For text messages
    text: Optional[str] = None

    # For template messages
    template_name: Optional[str] = None
    template_language: str = "en"
    template_parameters: Optional[List[str]] = None

    # For media messages
    media_type: Optional[str] = None  # image, document, audio, video
    media_url: Optional[str] = None
    media_filename: Optional[str] = None
    media_caption: Optional[str] = None

    # For interactive messages
    interactive_type: Optional[str] = None  # button, list
    buttons: Optional[List[Dict[str, str]]] = None
    list_sections: Optional[List[Dict]] = None

    @validator("to")
    def validate_whatsapp_number(cls, v):
        if not v.startswith("+"):
            raise ValueError("WhatsApp number must include country code with + prefix")
        return v

    @validator("text", "template_name")
    def validate_content_by_type(cls, v, values):
        """Validate content based on message type"""
        message_type = values.get("message_type", "text")

        if message_type == "text" and not v and "text" in cls.__fields__:
            raise ValueError("Text message requires text content")
        elif message_type == "template" and not v and "template_name" in cls.__fields__:
            raise ValueError("Template message requires template_name")

        return v


# Union type for service-specific content
ServiceSpecificContent = Union[EmailContent, SMSContent, WhatsAppContent]


# Generic notification content (backward compatibility)
class NotificationContent(BaseModel):
    """Generic notification content (for backward compatibility)"""

    subject: Optional[str] = None  # For email
    message: str
    template_id: Optional[str] = None
    template_data: Optional[Dict] = None

    # Service-specific content
    email_content: Optional[EmailContent] = None
    sms_content: Optional[SMSContent] = None
    whatsapp_content: Optional[WhatsAppContent] = None


# Service-specific payload models for Kafka
class EmailServicePayload(BaseModel):
    """Email service payload for Kafka"""

    service_type: NotificationType = NotificationType.EMAIL
    email_data: EmailContent
    correlation_id: str
    notification_id: str
    metadata: Optional[Dict] = None


class SMSServicePayload(BaseModel):
    """SMS service payload for Kafka"""

    service_type: NotificationType = NotificationType.SMS
    sms_data: SMSContent
    correlation_id: str
    notification_id: str
    metadata: Optional[Dict] = None


class WhatsAppServicePayload(BaseModel):
    """WhatsApp service payload for Kafka"""

    service_type: NotificationType = NotificationType.WHATSAPP
    whatsapp_data: WhatsAppContent
    correlation_id: str
    notification_id: str
    metadata: Optional[Dict] = None


# Union type for all service payloads
ServicePayload = Union[EmailServicePayload, SMSServicePayload, WhatsAppServicePayload]


# Generic service payload (backward compatibility)
class ServicePayload(BaseModel):
    """Individual service payload for Kafka"""

    service_type: NotificationType
    content: NotificationContent
    metadata: Optional[Dict] = None
    """Final payload structure sent to Kafka"""

    notification_id: str
    services: List[
        Union[EmailServicePayload, SMSServicePayload, WhatsAppServicePayload]
    ]
    original_request: NotificationRequest
    created_at: datetime
    scheduled_at: Optional[datetime] = None
