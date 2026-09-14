"""
邮件模型
定义邮件、邮件模板等相关表结构
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class EmailStatus(str, Enum):
    """邮件状态枚举"""

    DRAFT = "draft"
    QUEUED = "queued"
    SENT = "sent"
    FAILED = "failed"
    OPENED = "opened"
    REPLIED = "replied"


class EmailDirection(str, Enum):
    """邮件方向枚举"""

    OUTGOING = "outgoing"  # 发送
    INCOMING = "incoming"  # 接收


class Email(Base, UUIDMixin, TimestampMixin):
    """
    邮件模型
    """

    # 关联信息
    customer_id: Mapped[Optional[str]] = mapped_column(
        String(36),  # CHAR(36) 存储 UUID
        ForeignKey("customers.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    sender_id: Mapped[Optional[str]] = mapped_column(
        String(36),  # CHAR(36) 存储 UUID
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # 邮件信息
    subject: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )
    body: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    direction: Mapped[EmailDirection] = mapped_column(
        nullable=False,
        default=EmailDirection.OUTGOING,
    )
    status: Mapped[EmailStatus] = mapped_column(
        nullable=False,
        default=EmailStatus.DRAFT,
        index=True,
    )

    # 收发件人
    to_email: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    to_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )
    from_email: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    from_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )

    # 模板信息
    template_id: Mapped[Optional[str]] = mapped_column(
        String(36),  # CHAR(36) 存储 UUID
        ForeignKey("email_templates.id", ondelete="SET NULL"),
        nullable=True,
    )
    template_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )

    # 跟踪信息
    sent_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
    )
    opened_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
    )
    clicked_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
    )
    replied_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
    )

    # 错误信息
    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    # SMTP 信息
    message_id: Mapped[Optional[str]] = mapped_column(
        String(200),
        nullable=True,
    )
    thread_id: Mapped[Optional[str]] = mapped_column(
        String(200),
        nullable=True,
    )

    # 附件
    attachments: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
    )

    # 关系
    # customer = relationship("Customer", back_populates="emails")
    # sender = relationship("User", back_populates="sent_emails")
    # template = relationship("EmailTemplate", back_populates="emails")

    def __repr__(self) -> str:
        return f"<Email(id={self.id}, subject={self.subject}, status={self.status})>"


class EmailTemplate(Base, UUIDMixin, TimestampMixin):
    """
    邮件模板模型
    """

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
    )
    subject: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )
    body: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    category: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        index=True,
    )  # intro, followup, greeting, promotion
    language: Mapped[str] = mapped_column(
        String(10),
        default="zh",
        nullable=False,
    )
    variables: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
    )  # 可用变量列表
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    created_by: Mapped[Optional[str]] = mapped_column(
        String(36),  # CHAR(36) 存储 UUID
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # 关系
    # creator = relationship("User", back_populates="email_templates")
    # emails = relationship("Email", back_populates="template")

    def __repr__(self) -> str:
        return f"<EmailTemplate(id={self.id}, name={self.name})>"
