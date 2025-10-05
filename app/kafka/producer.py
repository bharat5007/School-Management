"""
Kafka Producer for sending notification messages
"""
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Union

from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaError
from loguru import logger

from app.config.settings import settings
from app.constants.enums import NotificationType
from app.schemas.bulk_notification import (
    BulkEmailKafkaPayload,
    BulkSMSKafkaPayload,
    BulkWhatsAppKafkaPayload,
)
from app.schemas.notification import (
    EmailServicePayload,
    SMSServicePayload,
    WhatsAppServicePayload,
)


class KafkaProducerClient:
    """
    Async Kafka Producer for sending notification messages
    """
    
    def __init__(self):
        self.producer: Optional[AIOKafkaProducer] = None
        self.is_connected = False
        
    async def start(self):
        """Initialize and start Kafka producer"""
        try:
            self.producer = AIOKafkaProducer(
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=lambda x: json.dumps(x, default=str).encode('utf-8'),
                key_serializer=lambda x: x.encode('utf-8') if x else None,
                # Producer optimization settings
                batch_size=settings.KAFKA_PRODUCER_BATCH_SIZE,
                linger_ms=settings.KAFKA_PRODUCER_LINGER_MS,
                retries=settings.KAFKA_PRODUCER_RETRIES,
                acks=settings.KAFKA_PRODUCER_ACKS,
                # Compression for better throughput
                compression_type='gzip',
                # Error handling
                retry_backoff_ms=100,
                request_timeout_ms=30000,
            )
            
            await self.producer.start()
            self.is_connected = True
            logger.info("Kafka producer started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start Kafka producer: {str(e)}")
            self.is_connected = False
            raise
    
    async def stop(self):
        """Stop Kafka producer"""
        if self.producer:
            try:
                await self.producer.stop()
                self.is_connected = False
                logger.info("Kafka producer stopped")
            except Exception as e:
                logger.error(f"Error stopping Kafka producer: {str(e)}")
    
    async def send_notification(
        self, 
        service_type: NotificationType, 
        payload: Union[
            EmailServicePayload, 
            SMSServicePayload, 
            WhatsAppServicePayload,
            BulkEmailKafkaPayload,
            BulkSMSKafkaPayload,
            BulkWhatsAppKafkaPayload
        ],
        key: Optional[str] = None
    ) -> bool:
        """
        Send notification payload to appropriate Kafka topic
        
        Args:
            service_type: Type of notification service
            payload: Service-specific payload
            key: Optional message key for partitioning
            
        Returns:
            bool: True if sent successfully
        """
        if not self.is_connected or not self.producer:
            logger.error("Kafka producer not connected")
            return False
        
        try:
            # Determine topic based on service type
            topic = self._get_topic_for_service(service_type)
            
            # Generate key if not provided (for partitioning)
            if not key:
                key = f"{service_type.value}_{datetime.now().strftime('%Y%m%d_%H')}"
            
            # Convert payload to dict
            message_data = payload.dict() if hasattr(payload, 'dict') else payload
            
            # Add metadata
            message_data.update({
                "kafka_metadata": {
                    "sent_at": datetime.now().isoformat(),
                    "producer_id": str(uuid.uuid4()),
                    "topic": topic,
                    "service_type": service_type.value
                }
            })
            
            # Send message
            await self.producer.send_and_wait(topic, message_data, key=key)
            
            logger.info(f"Message sent to Kafka topic '{topic}' with key '{key}'")
            return True
            
        except KafkaError as e:
            logger.error(f"Kafka error sending message: {str(e)}")
            await self._send_to_dlq(service_type, payload, str(e))
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending to Kafka: {str(e)}")
            return False
    
    async def send_bulk_notification(
        self,
        service_type: NotificationType,
        batch_payloads: List[Dict],
        campaign_id: str
    ) -> Dict[str, int]:
        """
        Send multiple notification payloads for bulk processing
        
        Returns:
            Dict with success/failure counts
        """
        results = {"success": 0, "failed": 0}
        
        for i, payload in enumerate(batch_payloads):
            key = f"{campaign_id}_{service_type.value}_{i}"
            success = await self.send_notification(service_type, payload, key)
            
            if success:
                results["success"] += 1
            else:
                results["failed"] += 1
        
        logger.info(f"Bulk send completed: {results}")
        return results
    
    def _get_topic_for_service(self, service_type: NotificationType) -> str:
        """Get Kafka topic name for service type"""
        topic_mapping = {
            NotificationType.EMAIL: settings.KAFKA_TOPIC_EMAIL_NOTIFICATIONS,
            NotificationType.SMS: settings.KAFKA_TOPIC_SMS_NOTIFICATIONS,
            NotificationType.WHATSAPP: settings.KAFKA_TOPIC_WHATSAPP_NOTIFICATIONS,
        }
        return topic_mapping.get(service_type, settings.KAFKA_TOPIC_BULK_NOTIFICATIONS)
    
    async def _send_to_dlq(self, service_type: NotificationType, payload, error_message: str):
        """Send failed message to Dead Letter Queue"""
        try:
            dlq_payload = {
                "original_payload": payload.dict() if hasattr(payload, 'dict') else payload,
                "service_type": service_type.value,
                "error": error_message,
                "failed_at": datetime.now().isoformat(),
                "retry_count": 0
            }
            
            await self.producer.send_and_wait(
                settings.KAFKA_TOPIC_DLQ, 
                dlq_payload,
                key=f"dlq_{service_type.value}_{datetime.now().timestamp()}"
            )
            
            logger.warning(f"Message sent to DLQ for {service_type.value}")
            
        except Exception as dlq_error:
            logger.error(f"Failed to send to DLQ: {str(dlq_error)}")


# Global Kafka producer instance
kafka_producer = KafkaProducerClient()


async def get_kafka_producer() -> KafkaProducerClient:
    """Get global Kafka producer instance"""
    if not kafka_producer.is_connected:
        await kafka_producer.start()
    return kafka_producer