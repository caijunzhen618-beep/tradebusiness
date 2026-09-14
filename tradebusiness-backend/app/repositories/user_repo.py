"""
用户数据访问层
处理用户相关的数据库操作
"""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserRole
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """用户 Repository"""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(User, session)

    async def get_by_username(self, username: str) -> Optional[User]:
        """
        通过用户名获取用户

        Args:
            username: 用户名

        Returns:
            用户对象或 None
        """
        stmt = select(User).where(User.username == username)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        """
        通过邮箱获取用户

        Args:
            email: 邮箱地址

        Returns:
            用户对象或 None
        """
        stmt = select(User).where(User.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_active_users(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> list[User]:
        """
        获取活跃用户列表

        Args:
            skip: 跳过的记录数
            limit: 返回的记录数

        Returns:
            用户列表
        """
        stmt = (
            select(User)
            .where(User.is_active == True)
            .order_by(User.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_users_by_role(
        self,
        role: UserRole,
        skip: int = 0,
        limit: int = 100,
    ) -> list[User]:
        """
        根据角色获取用户列表

        Args:
            role: 用户角色
            skip: 跳过的记录数
            limit: 返回的记录数

        Returns:
            用户列表
        """
        stmt = (
            select(User)
            .where(User.role == role)
            .order_by(User.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def search_users(
        self,
        keyword: str,
        skip: int = 0,
        limit: int = 100,
    ) -> list[User]:
        """
        搜索用户（按用户名、邮箱或全名）

        Args:
            keyword: 搜索关键词
            skip: 跳过的记录数
            limit: 返回的记录数

        Returns:
            用户列表
        """
        stmt = (
            select(User)
            .where(
                (User.username.ilike(f"%{keyword}%"))
                | (User.email.ilike(f"%{keyword}%"))
                | (User.full_name.ilike(f"%{keyword}%"))
            )
            .order_by(User.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count_total(self) -> int:
        """
        统计用户总数

        Returns:
            用户总数
        """
        from sqlalchemy import func

        stmt = select(func.count(User.id))
        result = await self.session.execute(stmt)
        return result.scalar() or 0

    async def count_by_role(self, role: UserRole) -> int:
        """
        统计指定角色的用户数量

        Args:
            role: 用户角色

        Returns:
            用户数量
        """
        from sqlalchemy import func

        stmt = select(func.count(User.id)).where(User.role == role)
        result = await self.session.execute(stmt)
        return result.scalar() or 0
