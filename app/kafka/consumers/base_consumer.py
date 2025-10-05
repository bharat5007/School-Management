"""
Base Consumer for processing Kafka messages
"""
import asyncio
from abc import ABC, abstractmethod
from typing import Dict, Any

from aiokafka import ConsumerRecord
from loguru import logger

from app.kafka.consumer import KafkaConsumerClient
from app.constants.enums import NotificationType


class BaseNotificationConsumer(ABC):
    """Base class for notification consumers"""

    def __init__(self, topics: list[str], consumer_group_id: str):
        self.topics = topics
        self.consumer_group_id = consumer_group_id
        self.consumer_client = KafkaConsumerClient(topics, consumer_group_id)
        self.is_running = False

    async def start(self):
        """Start the consumer"""
        try:
            await self.consumer_client.start()
            self.is_running = True
            logger.info(f"Started consumer for topics: {self.topics}")

            # Start consuming messages in background
            asyncio.create_task(self._consume_loop())

        except Exception as e:
            logger.error(f"Failed to start consumer: {str(e)}")
            raise

    async def stop(self):
        """Stop the consumer"""
        self.is_running = False
        if self.consumer_client:
            await self.consumer_client.stop()
            logger.info(f"Stopped consumer for topics: {self.topics}")

    async def _consume_loop(self):
        """Main consumption loop"""
        while self.is_running:
            try:
                await self.consumer_client.consume_messages(self._message_handler)
            except Exception as e:
                logger.error(f"Error in consume loop: {str(e)}")
                # Brief pause before retrying
                await asyncio.sleep(5)

    async def _message_handler(self, message: ConsumerRecord):
        """Handle incoming message"""
        try:
            logger.info(f"Processing message from topic {message.topic}, partition {message.partition}, offset {message.offset}")

            # Extract message data
            message_data = message.value

            # Process the message
            await self.process_message(message_data)

            logger.info(f"Successfully processed message from {message.topic}")

        except Exception as e:
            logger.error(f"Error processing message from {message.topic}: {str(e)}")
            # You might want to send to DLQ here
            await self._handle_message_error(message, str(e))

    @abstractmethod
    async def process_message(self, message_data: Dict[str, Any]):
        """Process the notification message - to be implemented by subclasses"""
        pass

    async def _handle_message_error(self, message: ConsumerRecord, error: str):
        """Handle message processing errors"""
        try:
            # Log error details
            logger.error(f"Message processing failed - Topic: {message.topic}, Partition: {message.partition}, Offset: {message.offset}, Error: {error}")

            # Here you could implement DLQ logic, retry mechanisms, etc.
            # For now, we'll just log the failure

        except Exception as dlq_error:
            logger.error(f"Failed to handle message error: {str(dlq_error)}")