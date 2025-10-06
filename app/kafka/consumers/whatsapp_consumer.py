"""
WhatsApp Notification Consumer
"""
import asyncio
from typing import Dict, Any, List

from loguru import logger

from app.config.settings import settings
from app.kafka.consumers.base_consumer import BaseNotificationConsumer
from app.schemas.bulk_notification import BulkWhatsAppKafkaPayload


class WhatsAppNotificationConsumer(BaseNotificationConsumer):
    """Consumer for processing WhatsApp notification messages"""

    def __init__(self):
        topics = [settings.KAFKA_TOPIC_WHATSAPP_NOTIFICATIONS]
        consumer_group_id = f"{settings.KAFKA_CONSUMER_GROUP_ID}-whatsapp"
        super().__init__(topics, consumer_group_id)

    async def process_message(self, message_data: Dict[str, Any]):
        """Process WhatsApp notification message"""
        try:
            # Parse the Kafka payload
            whatsapp_payload = BulkWhatsAppKafkaPayload(**message_data)

            logger.info(f"Processing WhatsApp batch {whatsapp_payload.batch_id} with {len(whatsapp_payload.recipients)} recipients")

            # Process WhatsApp batch with conservative rate limiting
            results = await self._process_whatsapp_batch(whatsapp_payload)

            logger.info(f"WhatsApp batch {whatsapp_payload.batch_id} processed: {results}")

        except Exception as e:
            logger.error(f"Failed to process WhatsApp message: {str(e)}")
            raise

    async def _process_whatsapp_batch(self, payload: BulkWhatsAppKafkaPayload) -> Dict[str, int]:
        """Process a batch of WhatsApp notifications with rate limiting"""
        results = {"success": 0, "failed": 0}

        # WhatsApp Business API has stricter rate limits
        # Conservative approach: 5 messages per second max
        delay_between_messages = 0.2  # 200ms delay = 5 messages/second

        logger.info(f"Processing WhatsApp batch with conservative rate limiting (5/sec)")

        for i, recipient in enumerate(payload.recipients):
            try:
                success = await self._send_whatsapp_message(recipient, payload)
                if success:
                    results["success"] += 1
                else:
                    results["failed"] += 1

                # Rate limiting - add delay between messages
                if i < len(payload.recipients) - 1:  # No delay after the last message
                    await asyncio.sleep(delay_between_messages)

            except Exception as e:
                logger.error(f"Failed to send WhatsApp to {recipient.get('whatsapp', 'unknown')}: {str(e)}")
                results["failed"] += 1

        return results

    async def _send_whatsapp_message(self, recipient: Dict[str, Any], payload: BulkWhatsAppKafkaPayload) -> bool:
        """Send WhatsApp message to a recipient"""
        try:
            whatsapp_number = recipient["whatsapp"]
            recipient_name = recipient.get("name", "")

            # Get template parameters if available
            template_parameters = recipient.get("template_parameters", payload.whatsapp_content.default_template_parameters or [])

            logger.info(f"Sending WhatsApp to {whatsapp_number} for batch {payload.batch_id}")

            # TODO: Implement actual WhatsApp Business API sending logic here
            # This would include:
            # 1. WhatsApp number validation and formatting
            # 2. Template message preparation
            # 3. WhatsApp Business API call
            # 4. Handling template approval status
            # 5. Managing conversation windows

            # Placeholder for actual WhatsApp sending
            await self._simulate_whatsapp_sending(whatsapp_number, payload.whatsapp_content.template_name, template_parameters, recipient_name)

            return True

        except Exception as e:
            logger.error(f"Failed to send WhatsApp to {recipient.get('whatsapp', 'unknown')}: {str(e)}")
            return False

    async def _simulate_whatsapp_sending(self, whatsapp_number: str, template_name: str, parameters: List[str], recipient_name: str = None):
        """Simulate WhatsApp sending (replace with actual implementation)"""
        # Simulate API call delay (WhatsApp API can be slower)
        await asyncio.sleep(0.1)

        name_display = f" ({recipient_name})" if recipient_name else ""
        params_display = f" with params: {parameters}" if parameters else ""
        logger.info(f"💬 WhatsApp sent to {whatsapp_number}{name_display}: Template '{template_name}'{params_display}")

        # In a real implementation, you would:
        # 1. Format WhatsApp number correctly (+country_code)
        # 2. Validate template exists and is approved
        # 3. Make API call to WhatsApp Business API
        # 4. Handle conversation window restrictions
        # 5. Track message delivery status
        # 6. Handle opt-out and spam reporting
        # 7. Manage template parameter substitution