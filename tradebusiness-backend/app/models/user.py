"""
用户模型
定义用户表结构和关系
"""

import uuid
from datetime import date
from enum import Enum
from typing import Optional

from sqlalchemy import Boolean, Date, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class UserRole(str, Enum):
    """用户角色枚举"""

    ADMIN = "admin"  # 管理员
    SALES = "sales"  # 业务员


class User(Base, UUIDMixin, TimestampMixin):
    """
    用户模型

    代表系统中的用户，包括管理员和业务员
    """

    # ==================== 基本信息 ====================
    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False,
    )
    email: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True,
        nullable=False,
    )
    hashed_password: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )
    full_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )

    # ==================== 角色和权限 ====================
    role: Mapped[str] = mapped_column(
        String(20),
        default=UserRole.SALES,
        nullable=False,
        index=True,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
    )
    is_superuser: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    # ==================== 联系信息 ====================
    phone: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
    )
    avatar_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )

    # ==================== 工作信息 ====================
    department: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )
    hired_date: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
    )
    resigned_date: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
    )

    # ==================== 备注 ====================
    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    # ==================== 关系 ====================
    # 客户关系（如果一个客户分配给某个用户）
    # customers = relationship("Customer", back_populates="assigned_user")

    def __repr__(self) -> str:
        return (
            f"<User(id={self.id}, username={self.username}, email={self.email}, role={self.role})>"
        )

    @property
    def is_admin(self) -> bool:
        """是否为管理员"""
        return self.role == UserRole.ADMIN or self.is_superuser

    @property
    def is_sales(self) -> bool:
        """是否为业务员"""
        return self.role == UserRole.SALES
