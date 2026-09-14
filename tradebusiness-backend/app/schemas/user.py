"""
用户相关的 Pydantic Schemas
定义用户创建、更新、响应等数据结构
"""

from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models.user import UserRole


class UserBase(BaseModel):
    """用户基础 Schema"""

    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱地址")
    full_name: Optional[str] = Field(None, max_length=100, description="全名")
    phone: Optional[str] = Field(None, max_length=20, description="电话号码")
    department: Optional[str] = Field(None, max_length=100, description="部门")


class UserCreate(UserBase):
    """创建用户 Schema"""

    password: str = Field(..., min_length=8, max_length=100, description="密码")
    role: UserRole = Field(default=UserRole.SALES, description="用户角色")
    hired_date: Optional[date] = Field(None, description="入职日期")

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """验证用户名"""
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError("Username can only contain letters, numbers, underscores and hyphens")
        return v.lower()

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """验证密码强度"""
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserUpdate(BaseModel):
    """更新用户 Schema（所有字段可选）"""

    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    department: Optional[str] = Field(None, max_length=100)
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    avatar_url: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = None


class PasswordChange(BaseModel):
    """修改密码 Schema"""

    old_password: str = Field(..., min_length=1, max_length=100, description="旧密码")
    new_password: str = Field(..., min_length=8, max_length=100, description="新密码")

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        """验证新密码强度"""
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserInDB(UserBase):
    """数据库中的用户 Schema（包含密码哈希）"""

    model_config = ConfigDict(from_attributes=True)

    id: str
    hashed_password: str
    role: UserRole
    is_active: bool
    is_superuser: bool
    avatar_url: Optional[str] = None
    hired_date: Optional[date] = None
    resigned_date: Optional[date] = None
    notes: Optional[str] = None


class UserResponse(UserBase):
    """用户响应 Schema"""

    model_config = ConfigDict(from_attributes=True)

    id: str
    role: UserRole
    is_active: bool
    is_superuser: bool
    avatar_url: Optional[str] = None
    hired_date: Optional[date] = None
    resigned_date: Optional[date] = None


class LoginRequest(BaseModel):
    """登录请求 Schema"""

    username: str = Field(..., description="用户名或邮箱")
    password: str = Field(..., description="密码")


class LoginResponse(BaseModel):
    """登录响应 Schema"""

    access_token: str = Field(..., description="访问令牌")
    refresh_token: str = Field(..., description="刷新令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
    expires_in: int = Field(..., description="过期时间（秒）")
    user: UserResponse = Field(..., description="用户信息")


class TokenResponse(BaseModel):
    """Token 响应 Schema"""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
