"""
用户业务逻辑层
处理用户相关的业务逻辑
"""

import uuid
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    InvalidCredentialsException,
    UserExistsException,
    UserNotFoundException,
)
from app.core.security import hash_password, verify_password
from app.models.user import User, UserRole
from app.repositories.user_repo import UserRepository


class UserService:
    """用户业务逻辑类"""

    def __init__(self, session: AsyncSession) -> None:
        """
        初始化用户服务

        Args:
            session: 数据库会话
        """
        self.session = session
        self.repo = UserRepository(session)

    async def get_user(self, user_id: str) -> User:
        """
        获取用户信息

        Args:
            user_id: 用户 ID

        Returns:
            用户对象

        Raises:
            UserNotFoundException: 用户不存在时
        """
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundException(user_id)
        return user

    async def get_user_by_username(self, username: str) -> User:
        """
        通过用户名获取用户

        Args:
            username: 用户名

        Returns:
            用户对象

        Raises:
            UserNotFoundException: 用户不存在时
        """
        user = await self.repo.get_by_username(username)
        if not user:
            raise UserNotFoundException(username)
        return user

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """
        通过邮箱获取用户

        Args:
            email: 邮箱地址

        Returns:
            用户对象或 None
        """
        return await self.repo.get_by_email(email)

    async def authenticate_user(
        self,
        username: str,
        password: str,
    ) -> User:
        """
        验证用户凭证

        Args:
            username: 用户名或邮箱
            password: 密码

        Returns:
            验证成功的用户对象

        Raises:
            InvalidCredentialsException: 凭证无效时
        """
        # 尝试通过用户名查找
        user = await self.repo.get_by_username(username)

        # 如果没找到，尝试通过邮箱查找
        if not user:
            user = await self.repo.get_by_email(username)

        # 如果还是没找到，或密码错误，抛出异常
        if not user or not verify_password(password, user.hashed_password):
            raise InvalidCredentialsException()

        # 检查用户是否被禁用
        if not user.is_active:
            raise InvalidCredentialsException("User account is disabled")

        return user

    async def create_user(
        self,
        username: str,
        email: str,
        password: str,
        full_name: Optional[str] = None,
        role: UserRole = UserRole.SALES,
        **kwargs,
    ) -> User:
        """
        创建新用户

        Args:
            username: 用户名
            email: 邮箱地址
            password: 密码
            full_name: 全名
            role: 用户角色
            **kwargs: 其他字段

        Returns:
            创建的用户对象

        Raises:
            UserExistsException: 用户名或邮箱已存在时
        """
        # 检查用户名是否已存在
        existing_user = await self.repo.get_by_username(username)
        if existing_user:
            raise UserExistsException("username", username)

        # 检查邮箱是否已存在
        existing_email = await self.repo.get_by_email(email)
        if existing_email:
            raise UserExistsException("email", email)

        # 创建用户
        user = await self.repo.create(
            id=uuid.uuid4(),
            username=username,
            email=email,
            hashed_password=hash_password(password),
            full_name=full_name,
            role=role,
            is_active=True,
            **kwargs,
        )

        return user

    async def update_user(
        self,
        user_id: str,
        **kwargs,
    ) -> User:
        """
        更新用户信息

        Args:
            user_id: 用户 ID
            **kwargs: 要更新的字段

        Returns:
            更新后的用户对象

        Raises:
            UserNotFoundException: 用户不存在时
        """
        user = await self.get_user(user_id)

        # 如果更新邮箱，检查新邮箱是否已被其他用户使用
        if "email" in kwargs:
            existing_user = await self.repo.get_by_email(kwargs["email"])
            if existing_user and existing_user.id != user_id:
                raise UserExistsException("email", kwargs["email"])

        # 如果更新用户名，检查新用户名是否已被其他用户使用
        if "username" in kwargs:
            existing_user = await self.repo.get_by_username(kwargs["username"])
            if existing_user and existing_user.id != user_id:
                raise UserExistsException("username", kwargs["username"])

        # 更新密码
        if "password" in kwargs:
            kwargs["hashed_password"] = hash_password(kwargs.pop("password"))

        return await self.repo.update(user, **kwargs)

    async def delete_user(self, user_id: str) -> None:
        """
        删除用户

        Args:
            user_id: 用户 ID

        Raises:
            UserNotFoundException: 用户不存在时
        """
        user = await self.get_user(user_id)
        await self.repo.delete(user)

    async def list_users(
        self,
        skip: int = 0,
        limit: int = 100,
        role: Optional[UserRole] = None,
        active_only: bool = False,
    ) -> tuple[list[User], int]:
        """
        获取用户列表

        Args:
            skip: 跳过的记录数
            limit: 返回的记录数
            role: 筛选角色
            active_only: 仅返回活跃用户

        Returns:
            (用户列表, 总数)
        """
        if role:
            users = await self.repo.get_users_by_role(role, skip, limit)
            total = await self.repo.count_by_role(role)
        elif active_only:
            users = await self.repo.get_active_users(skip, limit)
            total = await self.repo.count_total()
        else:
            users = await self.repo.get_all(skip, limit)
            total = await self.repo.count_total()

        return users, total

    async def change_password(
        self,
        user_id: str,
        old_password: str,
        new_password: str,
    ) -> User:
        """
        修改用户密码

        Args:
            user_id: 用户 ID
            old_password: 旧密码
            new_password: 新密码

        Returns:
            更新后的用户对象

        Raises:
            UserNotFoundException: 用户不存在时
            InvalidCredentialsException: 旧密码错误时
        """
        user = await self.get_user(user_id)

        # 验证旧密码
        if not verify_password(old_password, user.hashed_password):
            raise InvalidCredentialsException("Old password is incorrect")

        # 更新密码
        user.hashed_password = hash_password(new_password)
        await self.session.flush()

        return user

    async def toggle_user_status(self, user_id: str) -> User:
        """
        切换用户激活状态

        Args:
            user_id: 用户 ID

        Returns:
            更新后的用户对象

        Raises:
            UserNotFoundException: 用户不存在时
        """
        user = await self.get_user(user_id)
        user.is_active = not user.is_active
        await self.session.flush()
        return user
