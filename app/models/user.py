"""
User Database Model
"""
from sqlalchemy import Boolean, Column, String

from app.constants.enums import UserRole, UserStatus
from app.database.connection import Base


class User(Base):
    """User model"""

    __tablename__ = "users"

    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    role = Column(String(20), default=UserRole.USER, nullable=False)
    status = Column(String(20), default=UserStatus.ACTIVE, nullable=False)

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, username={self.username})>"
