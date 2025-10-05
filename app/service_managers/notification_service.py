"""
Notification Service Manager
"""
import uuid
from datetime import datetime
from typing import Dict, List, Union

from loguru import logger

from app.constants.enums import NotificationType
from app.kafka.producer import get_kafka_producer
from app.schemas.notification import (
    EmailContent,
    EmailServicePayload,
    KafkaNotificationPayload,
    NotificationRequest,
    NotificationResponse,
    ServicePayload,
    SMSContent,
    SMSServicePayload,
    WhatsAppContent,
    WhatsAppServicePayload,
)


class NotificationService:
    async def process_notification_request(
        self, notification_request: NotificationRequest
    ) -> NotificationResponse:
        """
        Main method to process notification request following the flowchart
        """
        logger.info(
            f"Processing notification request for channels: {notification_request.channels}"
        )

        # Step 1: Generate unique notification ID
        notification_id = str(uuid.uuid4())

        # Step 2: Prepare array to determine which services will be involved
        services_to_process = self._prepare_services_array(notification_request)

        # Step 3: Extract services to which request will be forwarded
        extracted_services = self._extract_services_for_forwarding(
            services_to_process, notification_request
        )

        # Step 4: Prepare payload that will be forwarded to Kafka
        kafka_payload = self._prepare_kafka_payload(
            notification_id, extracted_services, notification_request
        )

        # Step 5: Send to Kafka (NEW - Actually send to Kafka)
        kafka_success = await self._send_to_kafka(extracted_services, notification_id)

        # Return response to client
        status = "sent_to_kafka" if kafka_success else "kafka_error"
        return NotificationResponse(
            notification_id=notification_id,
            services_to_process=notification_request.channels,
            estimated_delivery=self._calculate_estimated_delivery(
                notification_request.priority
            ),
            status=status,
        )

    async def _send_to_kafka(
        self,
        service_payloads: List[
            Union[EmailServicePayload, SMSServicePayload, WhatsAppServicePayload]
        ],
        notification_id: str,
    ) -> bool:
        """
        Step 5: Actually send payloads to Kafka
        """
        try:
            kafka_producer = await get_kafka_producer()
            success_count = 0

            for payload in service_payloads:
                # Send each service payload to its respective Kafka topic
                success = await kafka_producer.send_notification(
                    payload.service_type,
                    payload,
                    key=f"{notification_id}_{payload.service_type.value}",
                )

                if success:
                    success_count += 1
                    logger.info(
                        f"Sent {payload.service_type.value} notification to Kafka"
                    )
                else:
                    logger.error(
                        f"Failed to send {payload.service_type.value} notification to Kafka"
                    )

            all_successful = success_count == len(service_payloads)
            logger.info(
                f"Kafka sending completed: {success_count}/{len(service_payloads)} successful"
            )

            return all_successful

        except Exception as e:
            logger.error(f"Error sending to Kafka: {str(e)}")
            return False

    def _prepare_services_array(
        self, request: NotificationRequest
    ) -> List[NotificationType]:
        """
        Step 2: Prepare array to determine which services will be involved
        Validates and filters the requested channels based on available recipient info
        """
        available_services = []
        recipient = request.recipient

        for channel in request.channels:
            if channel == NotificationType.EMAIL and recipient.email:
                available_services.append(channel)
                logger.debug(f"Email service available for {recipient.email}")

            elif channel == NotificationType.SMS and recipient.phone:
                available_services.append(channel)
                logger.debug(f"SMS service available for {recipient.phone}")

            elif channel == NotificationType.WHATSAPP and recipient.whatsapp:
                available_services.append(channel)
                logger.debug(f"WhatsApp service available for {recipient.whatsapp}")

            else:
                logger.warning(
                    f"Service {channel} requested but recipient info missing"
                )

        logger.info(f"Available services: {available_services}")
        return available_services

    def _extract_services_for_forwarding(
        self, services: List[NotificationType], request: NotificationRequest
    ) -> List[Union[EmailServicePayload, SMSServicePayload, WhatsAppServicePayload]]:
        """
        Step 3: Extract services to which request will be forwarded
        Creates service-specific payloads for each channel
        """
        service_payloads = []
        correlation_id = str(uuid.uuid4())
        notification_id = str(uuid.uuid4())

        for service_type in services:
            service_payload = self._create_service_specific_payload(
                service_type, request, correlation_id, notification_id
            )

            if service_payload:
                service_payloads.append(service_payload)
            logger.debug(f"Created payload for {service_type} service")

        return service_payloads

    def _extract_recipient_info_for_service(
        self, service_type: NotificationType, recipient
    ) -> Dict:
        """
        Extract relevant recipient information for each service type
        """
        base_info = {
            "name": recipient.name,
        }

        if service_type == NotificationType.EMAIL:
            base_info.update({"email": recipient.email, "channel": "email"})
        elif service_type == NotificationType.SMS:
            base_info.update({"phone": recipient.phone, "channel": "sms"})
        elif service_type == NotificationType.WHATSAPP:
            base_info.update({"whatsapp": recipient.whatsapp, "channel": "whatsapp"})

        return base_info

    def _create_service_specific_payload(
        self,
        service_type: NotificationType,
        request: NotificationRequest,
        correlation_id: str,
        notification_id: str,
    ) -> Union[EmailServicePayload, SMSServicePayload, WhatsAppServicePayload, None]:
        """
        Create service-specific payload based on service type
        """
        try:
            if service_type == NotificationType.EMAIL:
                return self._create_email_payload(
                    request, correlation_id, notification_id
                )
            elif service_type == NotificationType.SMS:
                return self._create_sms_payload(
                    request, correlation_id, notification_id
                )
            elif service_type == NotificationType.WHATSAPP:
                return self._create_whatsapp_payload(
                    request, correlation_id, notification_id
                )
            else:
                logger.error(f"Unsupported service type: {service_type}")
                return None

        except Exception as e:
            logger.error(f"Error creating {service_type} payload: {str(e)}")
            return None

    def _create_email_payload(
        self, request: NotificationRequest, correlation_id: str, notification_id: str
    ) -> EmailServicePayload:
        """Create email-specific payload"""

        # Use provided email content or create from generic content
        if request.content.email_content:
            email_data = request.content.email_content
        else:
            # Convert generic content to email format
            email_data = EmailContent(
                to=[request.recipient.email],
                subject=request.content.subject or "Notification",
                text_body=request.content.message,
                template_id=request.content.template_id,
                template_data=request.content.template_data,
            )

        return EmailServicePayload(
            email_data=email_data,
            priority=request.priority,
            correlation_id=correlation_id,
            notification_id=notification_id,
            metadata=request.metadata or {},
        )

    def _create_sms_payload(
        self, request: NotificationRequest, correlation_id: str, notification_id: str
    ) -> SMSServicePayload:
        """Create SMS-specific payload"""

        # Use provided SMS content or create from generic content
        if request.content.sms_content:
            sms_data = request.content.sms_content
        else:
            # Convert generic content to SMS format
            sms_data = SMSContent(
                to=request.recipient.phone,
                message=request.content.message,
                message_type="transactional",
            )

        return SMSServicePayload(
            sms_data=sms_data,
            priority=request.priority,
            correlation_id=correlation_id,
            notification_id=notification_id,
            metadata=request.metadata or {},
        )

    def _create_whatsapp_payload(
        self, request: NotificationRequest, correlation_id: str, notification_id: str
    ) -> WhatsAppServicePayload:
        """Create WhatsApp-specific payload"""

        # Use provided WhatsApp content or create from generic content
        if request.content.whatsapp_content:
            whatsapp_data = request.content.whatsapp_content
        else:
            # Convert generic content to WhatsApp format
            whatsapp_data = WhatsAppContent(
                to=request.recipient.whatsapp,
                message_type="text",
                text=request.content.message,
                template_name=request.content.template_id,
            )

        return WhatsAppServicePayload(
            whatsapp_data=whatsapp_data,
            priority=request.priority,
            correlation_id=correlation_id,
            notification_id=notification_id,
            metadata=request.metadata or {},
        )

    def _prepare_kafka_payload(
        self,
        notification_id: str,
        service_payloads: List[ServicePayload],
        original_request: NotificationRequest,
    ) -> KafkaNotificationPayload:
        """
        Step 4: Prepare payload that will be forwarded to Kafka
        Creates the final Kafka message payload
        """
        kafka_payload = KafkaNotificationPayload(
            notification_id=notification_id,
            services=service_payloads,
            original_request=original_request,
            created_at=datetime.now(),
            scheduled_at=original_request.scheduled_at,
        )

        logger.info(f"Prepared Kafka payload with {len(service_payloads)} services")
        return kafka_payload

    def _calculate_estimated_delivery(self, priority) -> datetime:
        """
        Calculate estimated delivery time based on priority
        """
        from datetime import timedelta

        base_time = datetime.now()

        if priority.value == "urgent":
            return base_time + timedelta(minutes=1)
        elif priority.value == "high":
            return base_time + timedelta(minutes=5)
        elif priority.value == "medium":
            return base_time + timedelta(minutes=15)
        else:  # low
            return base_time + timedelta(hours=1)
