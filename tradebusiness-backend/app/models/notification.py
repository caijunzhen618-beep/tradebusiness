"""
通知数据模型
定义系统通知的数据结构
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDMixin


class Notification(Base, UUIDMixin, TimestampMixin):
    """
    通知模型

    存储系统通知，用于应用内通知中心
    """

    # 用户关联
    user_id: Mapped[str] = mapped_column(
        String(36),  # CHAR(36) 存储 UUID
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # 通知内容
    type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )  # new_email, new_message, task_reminder, etc.

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    message: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
    )

    # 额外数据（JSON格式）
    data: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
    )  # {"customer_id": "...", "email_id": "..."}

    # 阅读状态
    is_read: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
    )

    read_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
    )

    # 过期时间
    expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
    )

    def __repr__(self) -> str:
        return f"<Notification(id={self.id}, type={self.type}, user_id={self.user_id})>"
