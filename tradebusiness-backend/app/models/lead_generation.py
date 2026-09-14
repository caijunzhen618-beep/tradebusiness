"""
AI 获客模型
定义获客任务、潜客、联系人、企业背调和开发信的数据结构。
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDMixin


class LeadTaskStatus(str, Enum):
    """获客任务状态。"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class LeadStatus(str, Enum):
    """潜客状态。"""

    NEW = "new"
    RESEARCHED = "researched"
    COPY_GENERATED = "copy_generated"
    CONTACTED = "contacted"
    REPLIED = "replied"
    INVALID = "invalid"


class SalesCopyChannel(str, Enum):
    """开发话术渠道。"""

    EMAIL = "email"
    WHATSAPP = "whatsapp"
    LINKEDIN = "linkedin"


class LeadSearchTask(Base, UUIDMixin, TimestampMixin):
    """AI 获客搜索任务。"""

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    target_country: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    target_industry: Mapped[Optional[str]] = mapped_column(String(120), nullable=True, index=True)
    product_keywords: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    customer_profile: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    exclude_keywords: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    website_inputs: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(
        String(20),
        default=LeadTaskStatus.PENDING.value,
        nullable=False,
        index=True,
    )
    total_found: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class Lead(Base, UUIDMixin, TimestampMixin):
    """AI 获客潜客公司。"""

    task_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("lead_search_tasks.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    company_name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    website: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, index=True)
    country: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    industry: Mapped[Optional[str]] = mapped_column(String(120), nullable=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    match_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(
        String(30),
        default=LeadStatus.NEW.value,
        nullable=False,
        index=True,
    )
    do_not_contact: Mapped[bool] = mapped_column(default=False, nullable=False, index=True)
    do_not_contact_reason: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class LeadContact(Base, UUIDMixin, TimestampMixin):
    """潜客联系人。"""

    lead_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("leads.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    title: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(120), nullable=True, index=True)
    phone: Mapped[Optional[str]] = mapped_column(String(60), nullable=True)
    linkedin_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    whatsapp: Mapped[Optional[str]] = mapped_column(String(60), nullable=True)
    source: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_verified: Mapped[bool] = mapped_column(default=False, nullable=False)


class CompanyResearchReport(Base, UUIDMixin, TimestampMixin):
    """企业背调报告。"""

    lead_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("leads.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    business_model: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    products: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    target_markets: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    buying_signals: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    pain_points: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    recommended_angle: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    raw_sources: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)


class SalesCopy(Base, UUIDMixin, TimestampMixin):
    """AI 生成的开发信和渠道话术。"""

    __tablename__ = "sales_copies"

    lead_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("leads.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    channel: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    language: Mapped[str] = mapped_column(String(20), default="en", nullable=False)
    subject: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    tone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="draft", nullable=False)


class FollowupTask(Base, UUIDMixin, TimestampMixin):
    """潜客后续跟进任务。"""

    lead_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("leads.id", ondelete="CASCADE"), index=True
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    channel: Mapped[str] = mapped_column(String(30), default="email", nullable=False)
    subject: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    due_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(30), default="pending", nullable=False, index=True)
