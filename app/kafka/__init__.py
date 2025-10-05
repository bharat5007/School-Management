"""
Kafka utilities for notification system

This package provides:
- Producer: For sending messages to Kafka topics
- Consumer: Base client for consuming messages 
- Admin: Administrative functions for topic management
- Consumers: Specialized consumers for different notification types
"""

from app.kafka.admin import (
    create_notification_topics,
    delete_notification_topics,
    get_topic_info,
)
from app.kafka.consumer import KafkaConsumerClient
from app.kafka.consumer import KafkaConsumerClient as KafkaConsumerClient_Legacy

# Import for backward compatibility (if needed)
# Import main classes for easy access
from app.kafka.producer import KafkaProducerClient
from app.kafka.producer import KafkaProducerClient as KafkaProducerClient_Legacy
from app.kafka.producer import get_kafka_producer, kafka_producer

__all__ = [
    "KafkaProducerClient",
    "KafkaConsumerClient",
    "kafka_producer",
    "get_kafka_producer",
    "create_notification_topics",
    "get_topic_info",
    "delete_notification_topics",
]
