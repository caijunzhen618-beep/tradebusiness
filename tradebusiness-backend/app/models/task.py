"""
任务模型
定义任务（待办事项）相关表结构
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDMixin


class TaskStatus(str, Enum):
    """任务状态枚举"""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskPriority(str, Enum):
    """任务优先级枚举"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Task(Base, UUIDMixin, TimestampMixin):
    """
    任务模型
    """

    # 任务信息
    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    type: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )  # call, email, meeting, followup

    # 关联
    customer_id: Mapped[Optional[str]] = mapped_column(
        String(36),  # CHAR(36) 存储 UUID
        ForeignKey("customers.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    assigned_to: Mapped[Optional[str]] = mapped_column(
        String(36),  # CHAR(36) 存储 UUID
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    created_by: Mapped[Optional[str]] = mapped_column(
        String(36),  # CHAR(36) 存储 UUID
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # 状态
    status: Mapped[str] = mapped_column(
        String(20),
        default=TaskStatus.PENDING,
        nullable=False,
        index=True,
    )
    priority: Mapped[str] = mapped_column(
        String(20),
        default=TaskPriority.MEDIUM,
        nullable=False,
    )

    # 时间
    due_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
    )

    # 提醒
    reminder_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
    )
    is_reminded: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<Task(id={self.id}, title={self.title}, status={self.status})>"
