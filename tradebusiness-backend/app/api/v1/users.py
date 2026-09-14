"""
用户管理 API
包含用户的 CRUD 操作
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_admin_user, get_current_user, get_db, get_user_service
from app.core.exceptions import InvalidCredentialsException, UserExistsException
from app.models.user import User, UserRole
from app.schemas.common import PaginatedResponse
from app.schemas.user import PasswordChange, UserCreate, UserResponse, UserUpdate
from app.services.user_service import UserService

router = APIRouter()


@router.get("", response_model=PaginatedResponse[UserResponse])
async def list_users(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(20, ge=1, le=100, description="返回的记录数"),
    role: Optional[UserRole] = Query(None, description="筛选角色"),
    active_only: bool = Query(False, description="仅返回活跃用户"),
    current_user: User = Depends(get_current_admin_user),
    user_service: UserService = Depends(get_user_service),
):
    """
    获取用户列表

    需要管理员权限。

    Args:
        skip: 分页偏移
        limit: 分页大小
        role: 角色筛选
        active_only: 仅活跃用户
        current_user: 当前用户（需管理员）
        user_service: 用户服务

    Returns:
        分页的用户列表
    """
    users, total = await user_service.list_users(
        skip=skip,
        limit=limit,
        role=role,
        active_only=active_only,
    )

    user_responses = [
        UserResponse(
            id=str(user.id),
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            is_active=user.is_active,
            is_superuser=user.is_superuser,
            phone=user.phone,
            avatar_url=user.avatar_url,
            hired_date=user.hired_date,
            resigned_date=user.resigned_date,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
        for user in users
    ]

    return {
        "items": user_responses,
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
):
    """
    获取当前登录用户信息

    Args:
        current_user: 当前用户

    Returns:
        当前用户详细信息
    """
    return UserResponse(
        id=str(current_user.id),
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        is_active=current_user.is_active,
        is_superuser=current_user.is_superuser,
        phone=current_user.phone,
        avatar_url=current_user.avatar_url,
        hired_date=current_user.hired_date,
        resigned_date=current_user.resigned_date,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    """
    获取用户详情

    Args:
        user_id: 用户 ID
        current_user: 当前用户
        user_service: 用户服务

    Returns:
        用户详细信息

    Raises:
        404: 用户不存在
    """
    # 非管理员只能查看自己的信息
    if not current_user.is_admin and str(current_user.id) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own profile",
        )

    user = await user_service.get_user(user_id)

    return UserResponse(
        id=str(user.id),
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        is_active=user.is_active,
        is_superuser=user.is_superuser,
        phone=user.phone,
        avatar_url=user.avatar_url,
        hired_date=user.hired_date,
        resigned_date=user.resigned_date,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(get_current_admin_user),
    user_service: UserService = Depends(get_user_service),
):
    """
    创建用户

    需要管理员权限。

    Args:
        user_data: 用户创建数据
        current_user: 当前用户（需管理员）
        user_service: 用户服务

    Returns:
        创建的用户信息

    Raises:
        400: 用户名或邮箱已存在
    """
    try:
        user = await user_service.create_user(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
            full_name=user_data.full_name,
            role=user_data.role,
            phone=user_data.phone,
            department=user_data.department,
            hired_date=user_data.hired_date,
        )
    except UserExistsException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    return UserResponse(
        id=str(user.id),
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        is_active=user.is_active,
        is_superuser=user.is_superuser,
        phone=user.phone,
        avatar_url=user.avatar_url,
        hired_date=user.hired_date,
        resigned_date=user.resigned_date,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    """
    更新用户信息

    Args:
        user_id: 用户 ID
        user_data: 更新数据
        current_user: 当前用户
        user_service: 用户服务

    Returns:
        更新后的用户信息

    Raises:
        403: 权限不足
        404: 用户不存在
    """
    # 非管理员只能更新自己的信息
    if not current_user.is_admin and str(current_user.id) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own profile",
        )

    # 非管理员不能修改角色
    if not current_user.is_admin and user_data.role is not None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can change user role",
        )

    user = await user_service.update_user(
        user_id,
        **user_data.model_dump(exclude_unset=True),
    )

    return UserResponse(
        id=str(user.id),
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        is_active=user.is_active,
        is_superuser=user.is_superuser,
        phone=user.phone,
        avatar_url=user.avatar_url,
        hired_date=user.hired_date,
        resigned_date=user.resigned_date,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


@router.post("/me/change-password", response_model=UserResponse)
async def change_my_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    """
    修改当前用户密码

    Args:
        password_data: 旧密码和新密码
        current_user: 当前用户
        user_service: 用户服务

    Returns:
        更新后的用户信息

    Raises:
        400: 旧密码错误或新密码不符合要求
    """
    try:
        user = await user_service.change_password(
            user_id=str(current_user.id),
            old_password=password_data.old_password,
            new_password=password_data.new_password,
        )
    except InvalidCredentialsException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message,
        )

    return UserResponse(
        id=str(user.id),
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        is_active=user.is_active,
        is_superuser=user.is_superuser,
        phone=user.phone,
        avatar_url=user.avatar_url,
        hired_date=user.hired_date,
        resigned_date=user.resigned_date,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    current_user: User = Depends(get_current_admin_user),
    user_service: UserService = Depends(get_user_service),
):
    """
    删除用户

    需要管理员权限。不能删除自己。

    Args:
        user_id: 用户 ID
        current_user: 当前用户（需管理员）
        user_service: 用户服务

    Raises:
        403: 尝试删除自己
        404: 用户不存在
    """
    if str(current_user.id) == user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete yourself",
        )

    await user_service.delete_user(user_id)


@router.post("/{user_id}/toggle-status", response_model=UserResponse)
async def toggle_user_status(
    user_id: str,
    current_user: User = Depends(get_current_admin_user),
    user_service: UserService = Depends(get_user_service),
):
    """
    切换用户激活状态

    需要管理员权限。

    Args:
        user_id: 用户 ID
        current_user: 当前用户（需管理员）
        user_service: 用户服务

    Returns:
        更新后的用户信息

    Raises:
        403: 尝试禁用自己
        404: 用户不存在
    """
    if str(current_user.id) == user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot disable yourself",
        )

    user = await user_service.toggle_user_status(user_id)

    return UserResponse(
        id=str(user.id),
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        is_active=user.is_active,
        is_superuser=user.is_superuser,
        phone=user.phone,
        avatar_url=user.avatar_url,
        hired_date=user.hired_date,
        resigned_date=user.resigned_date,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )
