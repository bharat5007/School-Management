"""
Simplified SQL Operations Manager - No Session Dependencies Required
"""
from typing import Any, Dict, List, Optional

from sqlalchemy import delete, func, select, text, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants.decorators import with_db_session, with_db_transaction
from app.models.user import User


class SQLOperations:
    """Global database operations - No session parameters needed in calling code!"""

    # ==================== READ OPERATIONS ====================

    @with_db_session
    async def get_user_by_id(self, session, username) -> Optional[User]:
        result = await session.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    @with_db_session
    async def get_user_by_email(self, email, session=None):
        result = await session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    @with_db_session
    async def get_users_paginated(
        self,
        session: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[User]:
        """Get users with pagination and optional filters"""
        query = select(User)

        if filters:
            for field, value in filters.items():
                if hasattr(User, field):
                    query = query.where(getattr(User, field) == value)

        query = query.offset(skip).limit(limit)
        result = await session.execute(query)
        return list(result.scalars().all())

    @with_db_session
    async def get_user_count(self, session: AsyncSession) -> int:
        """Get total user count"""
        result = await session.execute(select(func.count(User.id)))
        return result.scalar()

    # ==================== WRITE OPERATIONS ====================

    @with_db_transaction
    async def create_user(self, user_data, session=None) -> User:
        """Create a new user"""
        user = User(**user_data)
        session.add(user)
        await session.flush()  # Get the ID without committing
        await session.refresh(user)  # Load the full object
        return user

    @with_db_transaction
    async def update_user(
        self, session: AsyncSession, user_id: int, update_data: dict
    ) -> Optional[User]:
        """Update user by ID"""
        stmt = (
            update(User).where(User.id == user_id).values(**update_data).returning(User)
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @with_db_transaction
    async def delete_user(self, session: AsyncSession, user_id: int) -> bool:
        """Delete user by ID"""
        stmt = delete(User).where(User.id == user_id)
        result = await session.execute(stmt)
        return result.rowcount > 0

    @with_db_transaction
    async def bulk_create_users(
        self, session: AsyncSession, users_data: List[dict]
    ) -> List[User]:
        """Create multiple users in one transaction"""
        users = [User(**user_data) for user_data in users_data]
        session.add_all(users)
        await session.flush()
        for user in users:
            await session.refresh(user)
        return users

    # ==================== RAW SQL OPERATIONS ====================

    @with_db_session
    async def execute_raw_query(
        self, session: AsyncSession, query: str, params: Optional[dict] = None
    ):
        """Execute raw SQL query (SELECT)"""
        result = await session.execute(text(query), params or {})
        return result.fetchall()

    @with_db_transaction
    async def execute_raw_query_with_commit(
        self, session: AsyncSession, query: str, params: Optional[dict] = None
    ):
        """Execute raw SQL query with commit (INSERT/UPDATE/DELETE)"""
        result = await session.execute(text(query), params or {})
        return result


# Global instance
sql_ops = SQLOperations()
