"""
FastAPI Application Entry Point
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.config.settings import settings
from app.database.connection import init_db
from app.middleware.logging import LoggingMiddleware
from app.routes import auth, bulk_notification, health, notification, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting up the application...")
    await init_db()
    logger.info("Database initialized successfully")
    yield
    # Shutdown
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
