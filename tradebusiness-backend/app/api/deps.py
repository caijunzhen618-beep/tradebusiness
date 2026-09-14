"""
API 依赖注入
定义路由使用的依赖函数
"""

from typing import AsyncGenerator

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import InvalidTokenException, PermissionDeniedException
from app.core.security import decode_token
from app.db.session import get_async_session
from app.models.user import User
from app.repositories.user_repo import UserRepository
from app.services.user_service import UserService


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    获取数据库会话

    这是 FastAPI 依赖注入使用的生成器函数

    Yields:
        AsyncSession: 数据库会话
    """
    async for session in get_async_session():
        yield session


async def get_current_user(
    authorization: str = Header(None, description="Bearer Token"),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    获取当前登录用户

    Args:
        authorization: Authorization header (Bearer token)
        db: 数据库会话

    Returns:
        当前用户对象

    Raises:
        HTTPException: 认证失败时
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # 检查是否有Authorization头
    if not authorization:
        raise credentials_exception

    # 解析 Token
    try:
        if not authorization.startswith("Bearer "):
            raise credentials_exception

        token = authorization.split(" ")[1]
        payload = decode_token(token)

        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception

        token_type: str = payload.get("type", "access")
        if token_type != "access":
            raise credentials_exception

    except InvalidTokenException:
        raise credentials_exception
    except Exception:
        raise credentials_exception

    # 获取用户
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)

    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled",
        )

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    获取当前活跃用户

    Args:
        current_user: 当前用户

    Returns:
        当前活跃用户对象

    Raises:
        HTTPException: 用户未激活时
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled",
        )
    return current_user


async def get_current_admin_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    获取当前管理员用户

    Args:
        current_user: 当前用户

    Returns:
        当前管理员用户对象

    Raises:
        HTTPException: 用户不是管理员时
    """
    if not current_user.is_admin:
        raise PermissionDeniedException("Admin access required")
    return current_user


def get_user_service(
    db: AsyncSession = Depends(get_db),
) -> UserService:
    """
    获取用户服务实例

    Args:
        db: 数据库会话

    Returns:
        用户服务实例
    """
    return UserService(db)
