from app.routes import auth
from app.routes.bulk_notification import bulk_notification

from . import health, notification

__all__ = [
    "auth",
    "bulk_notification",
    "health",
    "notification",
]
