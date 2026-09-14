"""
认证相关 API
包含用户登录、注册、刷新 Token 等接口
"""

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, get_user_service
from app.config import settings
from app.core.audit import audit_event
from app.core.exceptions import InvalidCredentialsException
from app.core.security import create_access_token, create_refresh_token
from app.schemas.user import LoginRequest, LoginResponse, TokenResponse, UserCreate, UserResponse
from app.services.user_service import UserService

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    用户注册

    创建新用户账号。

    Args:
        user_data: 用户注册数据
        db: 数据库会话

    Returns:
        创建的用户信息

    Raises:
        400: 用户名或邮箱已存在
    """
    user_service = UserService(db)

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

    audit_event(
        "user_registered",
        user_id=str(user.id),
        resource_type="user",
        resource_id=str(user.id),
        metadata={"role": str(user.role)},
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


@router.post("/login", response_model=LoginResponse)
async def login(
    credentials: LoginRequest,
    user_service: UserService = Depends(get_user_service),
):
    """
    用户登录

    使用用户名/邮箱和密码登录。

    Args:
        credentials: 登录凭证（username, password）
        user_service: 用户服务

    Returns:
        登录响应（包含 Token 和用户信息）

    Raises:
        401: 用户名或密码错误
    """
    # 验证用户凭证
    try:
        user = await user_service.authenticate_user(
            username=credentials.username,
            password=credentials.password,
        )
    except InvalidCredentialsException:
        audit_event(
            "user_login_failed",
            user_id=None,
            resource_type="user",
            resource_id="unknown",
            metadata={"username": credentials.username},
        )
        raise

    # 创建 Token
    access_token = create_access_token(
        subject=str(user.id),
        expires_delta=timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    refresh_token = create_refresh_token(
        subject=str(user.id),
        expires_delta=timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS),
    )

    audit_event(
        "user_login_succeeded",
        user_id=str(user.id),
        resource_type="user",
        resource_id=str(user.id),
    )

    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse(
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
        ),
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_token: str,
    user_service: UserService = Depends(get_user_service),
):
    """
    刷新访问 Token

    使用刷新 Token 获取新的访问 Token。

    Args:
        refresh_token: 刷新 Token
        user_service: 用户服务

    Returns:
        新的 Token 对

    Raises:
        401: Token 无效或过期
    """
    from app.core.security import decode_token

    try:
        # 解码刷新 Token
        payload = decode_token(refresh_token)

        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )

        token_type: str = payload.get("type", "refresh")
        if token_type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )

        # 验证用户是否存在且活跃
        user = await user_service.get_user(user_id)
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is disabled",
            )

        # 创建新的 Token
        access_token = create_access_token(
            subject=str(user.id),
            expires_delta=timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
        )

        new_refresh_token = create_refresh_token(
            subject=str(user.id),
            expires_delta=timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS),
        )

        audit_event(
            "token_refreshed",
            user_id=str(user.id),
            resource_type="user",
            resource_id=str(user.id),
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )


@router.post("/logout")
async def logout():
    """
    用户登出

    在客户端删除 Token 即可（因为使用的是无状态 JWT）

    Returns:
        成功消息
    """
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user=Depends(get_current_user),
):
    """
    获取当前用户信息

    返回当前登录用户的详细信息。

    Args:
        current_user: 当前用户

    Returns:
        用户信息
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
