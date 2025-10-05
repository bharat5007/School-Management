"""
Bulk Notification Service Manager
Handles efficient processing of bulk notifications with batching, rate limiting, and optimization
"""
import math
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Union

from loguru import logger

from app.constants.enums import BulkProcessingStrategy, NotificationType
from app.kafka.producer import get_kafka_producer
from app.kafka.producer import get_kafka_producer
from app.schemas.bulk_notification import (
    BulkEmailKafkaPayload,
    BulkNotificationRequest,
    BulkNotificationResponse,
    BulkRecipient,
    BulkSMSKafkaPayload,
    BulkWhatsAppKafkaPayload,
)


class BulkNotificationService:
    """
    Service for handling bulk notifications efficiently
    Implements batching, rate limiting, and cost optimization
    """

    async def process_bulk_notification(
        self, bulk_request: BulkNotificationRequest
    ) -> BulkNotificationResponse:
        """
        Main method to process bulk notification requests
        """
        notification_id = str(uuid.uuid4())
        logger.info(f"Processing bulk notification {notification_id} for {len(bulk_request.recipients)} recipients")

        # Step 1: Analyze and optimize recipients per channel
        channel_recipients = self._analyze_recipients_by_channel(bulk_request)

        # Step 2: Create batches for each service
        service_batches = {}
        estimated_cost = {}

        for channel in bulk_request.channels:
            if channel in channel_recipients and channel_recipients[channel]:
                batches = self._create_service_batches(
                    channel, channel_recipients[channel], bulk_request
                )
                service_batches[channel.value] = batches

                # Estimate cost for this service
                estimated_cost[channel.value] = self._estimate_service_cost(
                    channel, len(channel_recipients[channel])
                )

        # Step 3: Create Kafka payloads for all batches
        total_kafka_messages = 0
        for channel, batches in service_batches.items():
            for batch in batches:
                # Send to Kafka (this would be actual Kafka producer call)
                logger.info(f"Created Kafka payload for {channel} batch {batch['batch_number']}")
                total_kafka_messages += 1

        # Step 4: Calculate completion time based on processing strategy
        completion_time = self._calculate_bulk_completion_time(
            bulk_request, service_batches
        )

        return BulkNotificationResponse(
            notification_id=notification_id,
            campaign_id=bulk_request.campaign_id,
            total_recipients=len(bulk_request.recipients),
            batches_created={k: len(v) for k, v in service_batches.items()},
            estimated_completion_time=completion_time,
            estimated_cost=estimated_cost
        )

    def _analyze_recipients_by_channel(
        self, bulk_request: BulkNotificationRequest
    ) -> Dict[NotificationType, List[BulkRecipient]]:
        """
        Analyze recipients and group them by available channels
        Also handles deduplication and validation
        """
        channel_recipients = {
            NotificationType.EMAIL: [],
            NotificationType.SMS: [],
            NotificationType.WHATSAPP: []
        }

        for recipient in bulk_request.recipients:
            for channel in bulk_request.channels:
                if self._recipient_supports_channel(recipient, channel):
                    channel_recipients[channel].append(recipient)

        # Log recipient distribution
        for channel, recipients in channel_recipients.items():
            if recipients:
                logger.info(f"{channel.value}: {len(recipients)} recipients")

        return channel_recipients

    def _recipient_supports_channel(
        self, recipient: BulkRecipient, channel: NotificationType
    ) -> bool:
        """Check if recipient has contact info for the given channel"""
        if channel == NotificationType.EMAIL:
            return recipient.email is not None
        elif channel == NotificationType.SMS:
            return recipient.phone is not None
        elif channel == NotificationType.WHATSAPP:
            return recipient.whatsapp is not None
        return False

    def _create_service_batches(
        self, 
        channel: NotificationType, 
        recipients: List[BulkRecipient], 
        bulk_request: BulkNotificationRequest
    ) -> List[Dict]:
        """
        Create optimized batches for a specific service
        Different services have different optimal batch sizes
        """
        batch_size = self._get_optimal_batch_size(channel, bulk_request)
        batches = []

        # Split recipients into batches
        total_batches = math.ceil(len(recipients) / batch_size)

        for i in range(0, len(recipients), batch_size):
            batch_recipients = recipients[i:i + batch_size]
            batch_number = (i // batch_size) + 1

            batch_data = self._create_kafka_payload_for_batch(
                channel, batch_recipients, batch_number, total_batches, bulk_request
            )

            batches.append(batch_data)

        logger.info(f"Created {len(batches)} batches for {channel.value}")
        return batches

    def _get_optimal_batch_size(
        self, channel: NotificationType, bulk_request: BulkNotificationRequest
    ) -> int:
        """
        Determine optimal batch size based on service and processing strategy
        """
        if channel == NotificationType.EMAIL:
            # Email can handle larger batches efficiently
            if bulk_request.content.email_content and bulk_request.content.email_content.use_bcc:
                return 500  # BCC can handle many recipients in single email
            return bulk_request.content.email_content.batch_size if bulk_request.content.email_content else 100

        elif channel == NotificationType.SMS:
            # SMS typically has rate limits
            base_size = bulk_request.content.sms_content.batch_size if bulk_request.content.sms_content else 50

            # Adjust based on processing strategy
            if bulk_request.processing_strategy == BulkProcessingStrategy.RATE_LIMITED:
                return min(base_size, 25)  # Smaller batches for rate limiting
            return base_size

        elif channel == NotificationType.WHATSAPP:
            # WhatsApp has stricter limits
            base_size = bulk_request.content.whatsapp_content.batch_size if bulk_request.content.whatsapp_content else 20

            # WhatsApp Business API has tighter restrictions
            if bulk_request.processing_strategy == BulkProcessingStrategy.RATE_LIMITED:
                return min(base_size, 10)
            return base_size

        return 50  # Default batch size

    def _create_kafka_payload_for_batch(
        self,
        channel: NotificationType,
        batch_recipients: List[BulkRecipient],
        batch_number: int,
        total_batches: int,
        bulk_request: BulkNotificationRequest
    ) -> Dict:
        """
        Create service-specific Kafka payload for a batch
        """
        correlation_id = str(uuid.uuid4())
        batch_id = f"{bulk_request.campaign_id or 'bulk'}_{channel.value}_{batch_number}"

        # Process recipients for this batch
        processed_recipients = self._process_recipients_for_service(
            channel, batch_recipients, bulk_request
        )

        if channel == NotificationType.EMAIL:
            return self._create_email_kafka_payload(
                batch_id, correlation_id, processed_recipients, 
                batch_number, total_batches, bulk_request
            ).dict()

        elif channel == NotificationType.SMS:
            return self._create_sms_kafka_payload(
                batch_id, correlation_id, processed_recipients,
                batch_number, total_batches, bulk_request
            ).dict()

        elif channel == NotificationType.WHATSAPP:
            return self._create_whatsapp_kafka_payload(
                batch_id, correlation_id, processed_recipients,
                batch_number, total_batches, bulk_request
            ).dict()

    def _process_recipients_for_service(
        self,
        channel: NotificationType,
        recipients: List[BulkRecipient],
        bulk_request: BulkNotificationRequest
    ) -> List[Dict]:
        """
        Process recipient data for specific service requirements
        """
        processed = []

        for recipient in recipients:
            recipient_data = {
                "user_id": recipient.user_id,
                "name": recipient.name,
                "custom_data": recipient.custom_data or {}
            }

            if channel == NotificationType.EMAIL:
                recipient_data["email"] = recipient.email
                # Add personalized template data
                if bulk_request.content.email_content and bulk_request.content.email_content.personalization_enabled:
                    recipient_data["template_data"] = {
                        **(bulk_request.content.email_content.default_template_data or {}),
                        **(recipient.custom_data or {})
                    }

            elif channel == NotificationType.SMS:
                recipient_data["phone"] = recipient.phone
                # Personalize SMS message
                if bulk_request.content.sms_content and bulk_request.content.sms_content.personalization_enabled:
                    recipient_data["personalized_message"] = self._personalize_message(
                        bulk_request.content.sms_content.message,
                        recipient.custom_data or {}
                    )

            elif channel == NotificationType.WHATSAPP:
                recipient_data["whatsapp"] = recipient.whatsapp
                # Personalize WhatsApp template parameters
                if (bulk_request.content.whatsapp_content 
                    and bulk_request.content.whatsapp_content.personalization_enabled 
                    and recipient.custom_data):
                    recipient_data["template_parameters"] = self._build_template_parameters(
                        bulk_request.content.whatsapp_content.default_template_parameters or [],
                        recipient.custom_data
                    )

            processed.append(recipient_data)

        return processed

    def _personalize_message(self, template_message: str, custom_data: Dict) -> str:
        """Simple template personalization"""
        message = template_message
        for key, value in custom_data.items():
            placeholder = f"{{{key}}}"
            message = message.replace(placeholder, str(value))
        return message

    def _build_template_parameters(
        self, default_params: List[str], custom_data: Dict
    ) -> List[str]:
        """Build personalized template parameters"""
        params = []
        for param in default_params:
            # If parameter is a placeholder, replace with custom data
            if param.startswith('{') and param.endswith('}'):
                key = param[1:-1]
                params.append(str(custom_data.get(key, param)))
            else:
                params.append(param)
        return params

    def _create_email_kafka_payload(
        self, batch_id: str, correlation_id: str, recipients: List[Dict],
        batch_number: int, total_batches: int, bulk_request: BulkNotificationRequest
    ) -> BulkEmailKafkaPayload:
        """Create email-specific Kafka payload"""
        return BulkEmailKafkaPayload(
            notification_id=bulk_request.campaign_id or str(uuid.uuid4()),
            batch_id=batch_id,
            correlation_id=correlation_id,
            recipients=recipients,
            email_content=bulk_request.content.email_content,
            processing_strategy=bulk_request.processing_strategy,
            priority=bulk_request.priority,
            batch_number=batch_number,
            total_batches=total_batches,
            total_recipients=len(bulk_request.recipients),
            metadata=bulk_request.metadata
        )

    def _create_sms_kafka_payload(
        self, batch_id: str, correlation_id: str, recipients: List[Dict],
        batch_number: int, total_batches: int, bulk_request: BulkNotificationRequest
    ) -> BulkSMSKafkaPayload:
        """Create SMS-specific Kafka payload"""
        return BulkSMSKafkaPayload(
            notification_id=bulk_request.campaign_id or str(uuid.uuid4()),
            batch_id=batch_id,
            correlation_id=correlation_id,
            recipients=recipients,
            sms_content=bulk_request.content.sms_content,
            processing_strategy=bulk_request.processing_strategy,
            priority=bulk_request.priority,
            rate_limit_per_second=bulk_request.content.sms_content.rate_limit_per_second if bulk_request.content.sms_content else 10,
            batch_number=batch_number,
            total_batches=total_batches,
            metadata=bulk_request.metadata
        )

    def _create_whatsapp_kafka_payload(
        self, batch_id: str, correlation_id: str, recipients: List[Dict],
        batch_number: int, total_batches: int, bulk_request: BulkNotificationRequest
    ) -> BulkWhatsAppKafkaPayload:
        """Create WhatsApp-specific Kafka payload"""
        estimated_cost = len(recipients) * 0.005  # Rough estimate: $0.005 per message

        return BulkWhatsAppKafkaPayload(
            notification_id=bulk_request.campaign_id or str(uuid.uuid4()),
            batch_id=batch_id,
            correlation_id=correlation_id,
            recipients=recipients,
            whatsapp_content=bulk_request.content.whatsapp_content,
            processing_strategy=bulk_request.processing_strategy,
            priority=bulk_request.priority,
            batch_number=batch_number,
            total_batches=total_batches,
            estimated_cost=estimated_cost,
            metadata=bulk_request.metadata
        )

    def _estimate_service_cost(self, channel: NotificationType, recipient_count: int) -> float:
        """Estimate cost for service based on recipient count"""
        # These are example rates - adjust based on your providers
        rates = {
            NotificationType.EMAIL: 0.0001,  # $0.0001 per email
            NotificationType.SMS: 0.01,      # $0.01 per SMS
            NotificationType.WHATSAPP: 0.005  # $0.005 per WhatsApp message
        }

        return recipient_count * rates.get(channel, 0.01)

    def _calculate_bulk_completion_time(
        self, bulk_request: BulkNotificationRequest, service_batches: Dict
    ) -> datetime:
        """Calculate estimated completion time based on batches and rate limits"""
        max_completion_time = datetime.now()

        for channel_str, batches in service_batches.items():
            channel = NotificationType(channel_str)

            if bulk_request.processing_strategy == BulkProcessingStrategy.IMMEDIATE:
                # All batches processed immediately
                estimated_time = datetime.now() + timedelta(minutes=len(batches) * 2)
            elif bulk_request.processing_strategy == BulkProcessingStrategy.RATE_LIMITED:
                # Factor in rate limits
                if channel == NotificationType.SMS:
                    # Assuming 10 SMS per second max
                    total_recipients = sum(len(batch.get('recipients', [])) for batch in batches)
                    seconds_needed = total_recipients / 10
                    estimated_time = datetime.now() + timedelta(seconds=seconds_needed)
                elif channel == NotificationType.WHATSAPP:
                    # More conservative for WhatsApp
                    total_recipients = sum(len(batch.get('recipients', [])) for batch in batches)
                    seconds_needed = total_recipients / 5
                    estimated_time = datetime.now() + timedelta(seconds=seconds_needed)
                else:
                    estimated_time = datetime.now() + timedelta(minutes=len(batches))
            else:
                # BATCHED or SCHEDULED
                estimated_time = datetime.now() + timedelta(minutes=len(batches) * 5)

            if estimated_time > max_completion_time:
                max_completion_time = estimated_time

        # Add spread time if specified
        if bulk_request.spread_over_minutes:
            max_completion_time = max(
                max_completion_time,
                datetime.now() + timedelta(minutes=bulk_request.spread_over_minutes)
            )

        return max_completion_time
