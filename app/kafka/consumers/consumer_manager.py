"""
Consumer Manager for coordinating all notification consumers
"""
import asyncio
from typing import List

from loguru import logger

from app.kafka.consumer.base_consumer import BaseNotificationConsumer
from app.kafka.consumer.email_consumer import EmailNotificationConsumer
from app.kafka.consumer.sms_consumer import SMSNotificationConsumer
from app.kafka.consumer.whatsapp_consumer import WhatsAppNotificationConsumer


class NotificationConsumerManager:
    """Manages all notification consumers"""

    def __init__(self):
        self.consumers: List[BaseNotificationConsumer] = []
        self.is_running = False

        # Initialize all consumers
        self._initialize_consumers()

    def _initialize_consumers(self):
        """Initialize all notification consumers"""
        try:
            # Email consumer
            email_consumer = EmailNotificationConsumer()
            self.consumers.append(email_consumer)

            # SMS consumer
            sms_consumer = SMSNotificationConsumer()
            self.consumers.append(sms_consumer)

            # WhatsApp consumer
            whatsapp_consumer = WhatsAppNotificationConsumer()
            self.consumers.append(whatsapp_consumer)

            logger.info(f"Initialized {len(self.consumers)} notification consumers")

        except Exception as e:
            logger.error(f"Failed to initialize consumers: {str(e)}")
            raise

    async def start_all(self):
        """Start all consumers"""
        try:
            logger.info("Starting all notification consumers...")

            # Start all consumers concurrently
            start_tasks = [consumer.start() for consumer in self.consumers]
            await asyncio.gather(*start_tasks)

            self.is_running = True
            logger.info("All notification consumers started successfully")

        except Exception as e:
            logger.error(f"Failed to start consumers: {str(e)}")
            # Stop any consumers that might have started
            await self.stop_all()
            raise

    async def stop_all(self):
        """Stop all consumers"""
        try:
            logger.info("Stopping all notification consumers...")

            # Stop all consumers concurrently
            stop_tasks = [consumer.stop() for consumer in self.consumers]
            await asyncio.gather(*stop_tasks, return_exceptions=True)

            self.is_running = False
            logger.info("All notification consumers stopped")

        except Exception as e:
            logger.error(f"Error stopping consumers: {str(e)}")


# Global consumer manager instance
consumer_manager = NotificationConsumerManager()