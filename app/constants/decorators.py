"""
Database decorators and wrappers for automatic session management
"""
import functools
from typing import Any, Callable, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import AsyncSessionLocal

F = TypeVar("F", bound=Callable[..., Any])


def with_db_session(func: F) -> F:
    """
    Decorator that automatically provides a database session to the decorated function.
    The session will be passed as the first argument after 'self'.

    Usage:
    @with_db_session
    async def get_user(self, session: AsyncSession, user_id: int):
        result = await session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
    """

    @functools.wraps(func)
    async def wrapper(self, *args, **kwargs):
        async with AsyncSessionLocal() as session:
            try:
                return await func(self, session, *args, **kwargs)
            except Exception:
                await session.rollback()
                raise

    return wrapper


def with_db_transaction(func: F) -> F:
    """
    Decorator that provides a session and automatically commits successful operations.
    Use this for write operations (create, update, delete).

    Usage:
    @with_db_transaction
    async def create_user(self, session: AsyncSession, user_data: dict):
        user = User(**user_data)
        session.add(user)
        await session.flush()  # Gets the ID
        return user
    """

    @functools.wraps(func)
    async def wrapper(self, *args, **kwargs):
        async with AsyncSessionLocal() as session:
            try:
                result = await func(self, session, *args, **kwargs)
                await session.commit()
                return result
            except Exception:
                await session.rollback()
                raise

    return wrapper


def with_db_session_no_self(func: F) -> F:
    """
    Decorator for standalone functions (not class methods).
    Session is passed as the first argument.

    Usage:
    @with_db_session_no_self
    async def get_user_count(session: AsyncSession):
        result = await session.execute(select(func.count(User.id)))
        return result.scalar()
    """

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        async with AsyncSessionLocal() as session:
            try:
                return await func(session, *args, **kwargs)
            except Exception:
                await session.rollback()
                raise

    return wrapper


class DatabaseWrapper:
    """Alternative wrapper approach - compose operations instead of decorating"""

    @staticmethod
    async def execute(operation_func, *args, **kwargs):
        """Execute any database operation with automatic session management"""
        async with AsyncSessionLocal() as session:
            try:
                result = await operation_func(session, *args, **kwargs)
                if hasattr(session, "new") and session.new:  # Has pending changes
                    await session.commit()
                return result
            except Exception:
                await session.rollback()
                raise
