"""
FastAPI Application Entry Point
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.config.settings import settings
from app.database.connection import init_db
from app.kafka.consumer.consumer_manager import consumer_manager
from app.kafka.producer import kafka_producer
from app.middleware.logging import LoggingMiddleware
from app.routes import auth, bulk_notification, health, notification, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting up the application...")

    # Initialize database

    # Initialize database
    await init_db()

    # Initialize Kafka consumers
    try:
        await consumer_manager.start_all()
        logger.info("Kafka consumers initialized successfully")
    except Exception as e:
        logger.warning(f"Kafka consumers initialization failed: {e}")

    # Initialize Kafka producer

    # Initialize Kafka consumers
    try:
        await consumer_manager.start_all()
        logger.info("Kafka consumers initialized successfully")
    except Exception as e:
        logger.warning(f"Kafka consumers initialization failed: {e}")

    # Initialize Kafka producer
    try:
        await kafka_producer.start()
        logger.info("Kafka producer initialized successfully")
    except Exception as e:
        logger.warning(f"Kafka producer initialization failed: {e}")

    # Initialize Kafka consumers
    try:
        await consumer_manager.start_all()
        logger.info("Kafka consumers initialized successfully")
    except Exception as e:
        logger.warning(f"Kafka consumers initialization failed: {e}")

    yield
    # Shutdown
    await consumer_manager.stop_all()
    logger.info("Kafka consumers stopped")
    await consumer_manager.stop_all()
    logger.info("Kafka consumers stopped")
    await kafka_producer.stop()
    logger.info("Kafka producer stopped")
    logger.info("Shutting down the application...")


def create_application() -> FastAPI:
    """Create and configure FastAPI application"""

    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description=settings.DESCRIPTION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add custom middleware
    app.add_middleware(LoggingMiddleware)

    # Include routers
    app.include_router(health.router, prefix=settings.API_V1_STR, tags=["health"])
    app.include_router(auth.router, prefix=settings.API_V1_STR, tags=["authentication"])
    app.include_router(
        notification.router,
        prefix=f"{settings.API_V1_STR}/notification",
        tags=["notifications"],
    )
    app.include_router(
        bulk_notification.router,
        prefix=f"{settings.API_V1_STR}/bulk-notification",
        tags=["bulk-notifications"],
    )

    return app


app = create_application()
