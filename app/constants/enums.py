"""
Application Enums
"""
from enum import Enum


class UserRole(str, Enum):
    """User role enumeration"""

    ADMIN = "admin"
    USER = "user"
    MODERATOR = "moderator"


class UserStatus(str, Enum):
    """User status enumeration"""

    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"


class NotificationType(str, Enum):
    """Notification type enumeration"""

    EMAIL = "email"
    SMS = "sms"
    WHATSAPP = "whatsapp"


class NotificationStatus(str, Enum):
    """Notification status enumeration"""

    PENDING = "pending"
    PROCESSING = "processing"
    SENT = "sent"
    FAILED = "failed"
    DELIVERED = "delivered"
    READ = "read"


class NotificationMode(str, Enum):
    """Notification mode enumeration"""

    SINGLE = "single"  # Single recipient
    BULK = "bulk"  # Multiple recipients
    BROADCAST = "broadcast"  # Send to all users with certain criteria


class BulkProcessingStrategy(str, Enum):
    """Bulk processing strategy enumeration"""

    IMMEDIATE = "immediate"  # Process all at once
    BATCHED = "batched"  # Process in batches
    RATE_LIMITED = "rate_limited"  # Respect rate limits
    SCHEDULED = "scheduled"  # Schedule processing over time


class NotificationPriority(str, Enum):
    """Notification priority enumeration"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"
