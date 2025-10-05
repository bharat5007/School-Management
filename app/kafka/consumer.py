"""
Kafka Consumer client for processing notification messages
"""
import json
from typing import List, Optional

from aiokafka import AIOKafkaConsumer
from loguru import logger

from app.config.settings import settings


class KafkaConsumerClient:
    """
    Async Kafka Consumer for processing notification messages
    """

    def __init__(self, topics: List[str], group_id: Optional[str] = None):
        self.topics = topics
        self.group_id = group_id or settings.KAFKA_CONSUMER_GROUP_ID
        self.consumer: Optional[AIOKafkaConsumer] = None
        self.is_running = False

    async def start(self):
        """Initialize and start Kafka consumer"""
        try:
            self.consumer = AIOKafkaConsumer(
                *self.topics,
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                group_id=self.group_id,
                value_deserializer=lambda x: json.loads(x.decode("utf-8")),
                auto_offset_reset=settings.KAFKA_CONSUMER_AUTO_OFFSET_RESET,
                max_poll_records=settings.KAFKA_CONSUMER_MAX_POLL_RECORDS,
                # Consumer optimization
                fetch_min_bytes=1,
                fetch_max_wait_ms=500,
                # Error handling
                retry_backoff_ms=100,
                request_timeout_ms=40000,
            )

            await self.consumer.start()
            self.is_running = True
            logger.info(f"Kafka consumer started for topics: {self.topics}")

        except Exception as e:
            logger.error(f"Failed to start Kafka consumer: {str(e)}")
            raise

    async def stop(self):
        """Stop Kafka consumer"""
        if self.consumer:
            try:
                self.is_running = False
                await self.consumer.stop()
                logger.info("Kafka consumer stopped")
            except Exception as e:
                logger.error(f"Error stopping Kafka consumer: {str(e)}")

    async def consume_messages(self, message_handler):
        """
        Consume messages and process them with provided handler

        Args:
            message_handler: Async function to process messages
        """
        if not self.is_running or not self.consumer:
            logger.error("Kafka consumer not running")
            return

        logger.info("Starting message consumption...")

        try:
            async for message in self.consumer:
                try:
                    # Process message
                    await message_handler(message)

                    # Commit offset after successful processing
                    await self.consumer.commit()

                except Exception as e:
                    logger.error(f"Error processing message: {str(e)}")
                    # Don't commit offset for failed messages
                    continue

        except Exception as e:
            logger.error(f"Error in message consumption: {str(e)}")
        finally:
            logger.info("Message consumption stopped")
