"""
Email Notification Consumer
"""
from typing import Dict, Any, List

from loguru import logger

from app.config.settings import settings
from app.kafka.consumers.base_consumer import BaseNotificationConsumer
from app.schemas.bulk_notification import BulkEmailKafkaPayload


class EmailNotificationConsumer(BaseNotificationConsumer):
    """Consumer for processing email notification messages"""

    def __init__(self):
        topics = [settings.KAFKA_TOPIC_EMAIL_NOTIFICATIONS]
        consumer_group_id = f"{settings.KAFKA_CONSUMER_GROUP_ID}-email"
        super().__init__(topics, consumer_group_id)

    async def process_message(self, message_data: Dict[str, Any]):
        """Process email notification message"""
        try:
            # Parse the Kafka payload
            email_payload = BulkEmailKafkaPayload(**message_data)

            logger.info(f"Processing email batch {email_payload.batch_id} with {len(email_payload.recipients)} recipients")

            # Process each recipient in the batch
            results = await self._process_email_batch(email_payload)

            logger.info(f"Email batch {email_payload.batch_id} processed: {results}")

        except Exception as e:
            logger.error(f"Failed to process email message: {str(e)}")
            raise

    async def _process_email_batch(self, payload: BulkEmailKafkaPayload) -> Dict[str, int]:
        """Process a batch of email notifications"""
        results = {"success": 0, "failed": 0}

        # Check if using BCC for bulk sending
        if payload.email_content and payload.email_content.use_bcc:
            # Send single email with BCC
            success = await self._send_bcc_email(payload)
            if success:
                results["success"] = len(payload.recipients)
            else:
                results["failed"] = len(payload.recipients)
        else:
            # Send individual emails
            for recipient in payload.recipients:
                try:
                    success = await self._send_individual_email(recipient, payload)
                    if success:
                        results["success"] += 1
                    else:
                        results["failed"] += 1
                except Exception as e:
                    logger.error(f"Failed to send email to {recipient.get('email', 'unknown')}: {str(e)}")
                    results["failed"] += 1

        return results

    async def _send_bcc_email(self, payload: BulkEmailKafkaPayload) -> bool:
        """Send a single email with BCC to all recipients"""
        try:
            # Extract email addresses
            bcc_emails = [recipient["email"] for recipient in payload.recipients if "email" in recipient]

            logger.info(f"Sending BCC email to {len(bcc_emails)} recipients for batch {payload.batch_id}")

            # TODO: Implement actual email sending logic here
            # This is where you'd integrate with your email service provider
            # (e.g., SendGrid, AWS SES, SMTP server, etc.)

            # Placeholder for actual email sending
            await self._simulate_email_sending(bcc_emails, payload.email_content.subject)

            return True

        except Exception as e:
            logger.error(f"Failed to send BCC email for batch {payload.batch_id}: {str(e)}")
            return False

    async def _send_individual_email(self, recipient: Dict[str, Any], payload: BulkEmailKafkaPayload) -> bool:
        """Send individual email to a recipient"""
        try:
            email_address = recipient["email"]
            recipient_name = recipient.get("name", "")

            logger.info(f"Sending individual email to {email_address} for batch {payload.batch_id}")

            # TODO: Implement actual email sending logic here
            # This would include:
            # 1. Template rendering with recipient-specific data
            # 2. Personalization using recipient.get("template_data", {})
            # 3. Email service provider API call

            # Placeholder for actual email sending
            await self._simulate_email_sending([email_address], payload.email_content.subject, recipient_name)

            return True

        except Exception as e:
            logger.error(f"Failed to send individual email to {recipient.get('email', 'unknown')}: {str(e)}")
            return False

    async def _simulate_email_sending(self, emails: List[str], subject: str, recipient_name: str = None):
        """Simulate email sending (replace with actual implementation)"""
        import asyncio

        # Simulate API call delay
        await asyncio.sleep(0.1)

        if recipient_name:
            logger.info(f"✅ Email sent to {recipient_name} ({emails[0]}): '{subject}'")
        else:
            logger.info(f"✅ BCC Email sent to {len(emails)} recipients: '{subject}'")

        # In a real implementation, you would:
        # 1. Render email template with recipient data
        # 2. Make API call to email service provider
        # 3. Handle rate limiting and retries
        # 4. Track delivery status
        # 5. Handle bounces and complaints