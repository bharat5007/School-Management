"""
SMS Notification Consumer
"""
import asyncio
from typing import Any, Dict

from loguru import logger

from app.config.settings import settings
from app.kafka.consumer.base_consumer import BaseNotificationConsumer
from app.schemas.bulk_notification import BulkSMSKafkaPayload


class SMSNotificationConsumer(BaseNotificationConsumer):
    """Consumer for processing SMS notification messages"""

    def __init__(self):
        topics = [settings.KAFKA_TOPIC_SMS_NOTIFICATIONS]
        consumer_group_id = f"{settings.KAFKA_CONSUMER_GROUP_ID}-sms"
        super().__init__(topics, consumer_group_id)

    async def process_message(self, message_data: Dict[str, Any]):
        """Process SMS notification message"""
        try:
            # Parse the Kafka payload
            sms_payload = BulkSMSKafkaPayload(**message_data)

            logger.info(
                f"Processing SMS batch {sms_payload.batch_id} with {len(sms_payload.recipients)} recipients"
            )

            # Process SMS batch with rate limiting
            results = await self._process_sms_batch(sms_payload)

            logger.info(f"SMS batch {sms_payload.batch_id} processed: {results}")

        except Exception as e:
            logger.error(f"Failed to process SMS message: {str(e)}")
            raise

    async def _process_sms_batch(self, payload: BulkSMSKafkaPayload) -> Dict[str, int]:
        """Process a batch of SMS notifications with rate limiting"""
        results = {"success": 0, "failed": 0}

        # Calculate rate limiting delay
        rate_limit = payload.rate_limit_per_second
        delay_between_sms = 1.0 / rate_limit if rate_limit > 0 else 0.1

        logger.info(
            f"Processing SMS batch with rate limit: {rate_limit}/sec (delay: {delay_between_sms}s)"
        )

        for i, recipient in enumerate(payload.recipients):
            try:
                success = await self._send_sms(recipient, payload)
                if success:
                    results["success"] += 1
                else:
                    results["failed"] += 1

                # Rate limiting - add delay between SMS sends
                if i < len(payload.recipients) - 1:  # No delay after the last SMS
                    await asyncio.sleep(delay_between_sms)

            except Exception as e:
                logger.error(
                    f"Failed to send SMS to {recipient.get('phone', 'unknown')}: {str(e)}"
                )
                results["failed"] += 1

        return results

    async def _send_sms(
        self, recipient: Dict[str, Any], payload: BulkSMSKafkaPayload
    ) -> bool:
        """Send SMS to a recipient"""
        try:
            phone_number = recipient["phone"]
            recipient_name = recipient.get("name", "")

            # Get personalized message if available
            message = recipient.get("personalized_message", payload.sms_content.message)

            logger.info(f"Sending SMS to {phone_number} for batch {payload.batch_id}")

            # TODO: Implement actual SMS sending logic here
            # This would include:
            # 1. Phone number validation and formatting
            # 2. SMS service provider API call (Twilio, AWS SNS, etc.)
            # 3. Character count validation
            # 4. Delivery status tracking

            # Placeholder for actual SMS sending
            await self._simulate_sms_sending(phone_number, message, recipient_name)

            return True

        except Exception as e:
            logger.error(
                f"Failed to send SMS to {recipient.get('phone', 'unknown')}: {str(e)}"
            )
            return False

    async def _simulate_sms_sending(
        self, phone: str, message: str, recipient_name: str = None
    ):
        """Simulate SMS sending (replace with actual implementation)"""
        # Simulate API call delay
        await asyncio.sleep(0.05)

        name_display = f" ({recipient_name})" if recipient_name else ""
        logger.info(
            f"📱 SMS sent to {phone}{name_display}: '{message[:50]}{'...' if len(message) > 50 else ''}'"
        )

        # In a real implementation, you would:
        # 1. Format phone number correctly
        # 2. Validate message length and content
        # 3. Make API call to SMS provider (Twilio, AWS SNS, etc.)
        # 4. Handle rate limiting and carrier restrictions
        # 5. Track delivery receipts and failures
        # 6. Handle opt-out requests
