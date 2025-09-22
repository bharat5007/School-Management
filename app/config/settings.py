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