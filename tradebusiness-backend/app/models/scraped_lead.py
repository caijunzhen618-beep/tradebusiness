"""
采集线索（临时数据）模型
存储从不同数据源采集的原始数据
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import JSON, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDMixin


class ScrapedLeadStatus:
    """线索状态"""

    PENDING = "pending"  # 待审核
    APPROVED = "approved"  # 已批准
    REJECTED = "rejected"  # 已拒绝
    IMPORTED = "imported"  # 已导入customers表


class ScrapedLead(Base, TimestampMixin, UUIDMixin):
    """
    采集线索表
    临时存储从各种数据源采集的数据，经过审核后导入customers表
    """

    __tablename__ = "scraped_leads"

    # 原始数据
    raw_data: Mapped[dict] = mapped_column(JSON, nullable=False, comment="原始采集数据（JSON格式）")
    data_source: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="数据源：google/directory/specific_site"
    )
    source_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, comment="来源URL")

    # 标准化后的数据
    company_name: Mapped[str] = mapped_column(String(200), nullable=False, comment="公司名称")
    company_name_en: Mapped[Optional[str]] = mapped_column(
        String(200), nullable=True, comment="英文名称"
    )
    country: Mapped[str] = mapped_column(String(100), nullable=False, comment="国家")
    country_code: Mapped[str] = mapped_column(String(3), nullable=False, comment="国家代码")
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, comment="城市")

    # 联系信息
    email: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, comment="邮箱")
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, comment="电话")
    whatsapp: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, comment="WhatsApp")
    website: Mapped[Optional[str]] = mapped_column(String(200), nullable=True, comment="网站")

    # 业务信息
    business_type: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="业务类型"
    )
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="公司描述")
    confidence_score: Mapped[int] = mapped_column(
        Integer, default=50, comment="数据可信度（0-100）"
    )

    # 审核状态
    status: Mapped[str] = mapped_column(
        String(20), default=ScrapedLeadStatus.PENDING, nullable=False, comment="审核状态"
    )
    reviewed_by: Mapped[Optional[str]] = mapped_column(
        String(36), nullable=True, comment="审核人ID"
    )
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="审核时间"
    )
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="拒绝原因")

    # 导入信息
    imported_to_customer_id: Mapped[Optional[str]] = mapped_column(
        String(36), nullable=True, comment="导入后的customer记录ID"
    )
    imported_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="导入时间"
    )

    # 关联
    scraping_task_id: Mapped[str] = mapped_column(
        String(36), nullable=False, comment="关联的采集任务ID"
    )
    matched_by: Mapped[Optional[str]] = mapped_column(
        String(36), nullable=True, comment="匹配/导入操作人ID"
    )

    # 重复检测
    duplicate_of: Mapped[Optional[str]] = mapped_column(
        String(36), nullable=True, comment="重复的scraped_lead ID"
    )
    similarity_score: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, comment="与重复记录的相似度（0-100）"
    )

    def __repr__(self):
        return f"<ScrapedLead(id={self.id}, company={self.company_name}, status={self.status})>"
