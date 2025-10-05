"""
Application Settings and Configuration
"""
from typing import List, Optional

from pydantic import AnyHttpUrl, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""

    # Application
    PROJECT_NAME: str = "FastAPI Production App"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "A production-ready FastAPI application"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"

    # Security
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"

    # Database
    DATABASE_URL: str
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: int = 5432
    DATABASE_NAME: str = "fastapi_db"
    DATABASE_USER: str = "username"
    DATABASE_PASSWORD: str = "password"

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # Kafka Configuration
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_SECURITY_PROTOCOL: str = "PLAINTEXT"
    KAFKA_SASL_MECHANISM: Optional[str] = None
    KAFKA_SASL_USERNAME: Optional[str] = None
    KAFKA_SASL_PASSWORD: Optional[str] = None

    # Kafka Topics
    KAFKA_TOPIC_EMAIL_NOTIFICATIONS: str = "email-notifications"
    KAFKA_TOPIC_SMS_NOTIFICATIONS: str = "sms-notifications"
    KAFKA_TOPIC_WHATSAPP_NOTIFICATIONS: str = "whatsapp-notifications"
    KAFKA_TOPIC_BULK_NOTIFICATIONS: str = "bulk-notifications"
    KAFKA_TOPIC_DLQ: str = "notification-dlq"  # Dead Letter Queue

    # Kafka Producer Settings
    KAFKA_PRODUCER_BATCH_SIZE: int = 16384
    KAFKA_PRODUCER_LINGER_MS: int = 100
    KAFKA_PRODUCER_RETRIES: int = 3
    KAFKA_PRODUCER_ACKS: str = "all"

    # Kafka Consumer Settings
    KAFKA_CONSUMER_GROUP_ID: str = "notification-service"
    KAFKA_CONSUMER_AUTO_OFFSET_RESET: str = "latest"
    KAFKA_CONSUMER_MAX_POLL_RECORDS: int = 100

    # CORS
    ALLOWED_ORIGINS: List[AnyHttpUrl] = []

    @validator("ALLOWED_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: str) -> List[str]:
        """Assemble CORS origins from string or list"""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
