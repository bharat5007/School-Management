"""
Kafka Administration utilities
"""
from loguru import logger

from app.config.settings import settings


async def create_notification_topics():
    """
    Create notification topics if they don't exist
    This would typically be done by Kafka admin client or during deployment
    """
    from kafka import KafkaAdminClient, NewTopic
    from kafka.errors import TopicAlreadyExistsError

    try:
        admin_client = KafkaAdminClient(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            client_id="notification_admin",
        )

        topics = [
            NewTopic(
                name=settings.KAFKA_TOPIC_EMAIL_NOTIFICATIONS,
                num_partitions=3,
                replication_factor=1,
            ),
            NewTopic(
                name=settings.KAFKA_TOPIC_SMS_NOTIFICATIONS,
                num_partitions=3,
                replication_factor=1,
            ),
            NewTopic(
                name=settings.KAFKA_TOPIC_WHATSAPP_NOTIFICATIONS,
                num_partitions=3,
                replication_factor=1,
            ),
            NewTopic(
                name=settings.KAFKA_TOPIC_BULK_NOTIFICATIONS,
                num_partitions=5,
                replication_factor=1,
            ),
            NewTopic(
                name=settings.KAFKA_TOPIC_DLQ, num_partitions=1, replication_factor=1
            ),
        ]

        admin_client.create_topics(new_topics=topics, validate_only=False)
        logger.info("Notification topics created successfully")

    except TopicAlreadyExistsError:
        logger.info("Topics already exist, skipping creation")
    except Exception as e:
        logger.error(f"Error creating topics: {str(e)}")


def get_topic_info():
    """Get information about Kafka topics"""
    from kafka import KafkaAdminClient

    try:
        admin_client = KafkaAdminClient(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            client_id="notification_admin_info",
        )

        metadata = admin_client.list_topics()
        logger.info(f"Available topics: {list(metadata)}")
        return metadata

    except Exception as e:
        logger.error(f"Error getting topic info: {str(e)}")
        return None


def delete_notification_topics():
    """
    Delete notification topics (use with caution!)
    This should only be used in development/testing environments
    """
    from kafka import KafkaAdminClient

    try:
        admin_client = KafkaAdminClient(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            client_id="notification_admin_delete",
        )

        topics_to_delete = [
            settings.KAFKA_TOPIC_EMAIL_NOTIFICATIONS,
            settings.KAFKA_TOPIC_SMS_NOTIFICATIONS,
            settings.KAFKA_TOPIC_WHATSAPP_NOTIFICATIONS,
            settings.KAFKA_TOPIC_BULK_NOTIFICATIONS,
            settings.KAFKA_TOPIC_DLQ,
        ]

        admin_client.delete_topics(topics=topics_to_delete)
        logger.warning("Notification topics deleted successfully")

    except Exception as e:
        logger.error(f"Error deleting topics: {str(e)}")
