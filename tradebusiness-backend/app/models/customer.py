"""
客户模型
定义客户表结构和关系
"""

from datetime import date, datetime
from enum import Enum
from typing import Optional

from sqlalchemy import JSON, Boolean, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDMixin


class BusinessType(str, Enum):
    """业务类型枚举"""

    SEA = "sea"
    AIR = "air"
    LAND = "land"
    MULTIMODAL = "multimodal"


class CustomerStatus(str, Enum):
    """客户状态枚举"""

    POTENTIAL = "potential"  # 潜在客户
    CONTACTING = "contacting"  # 联系中
    COOPERATING = "cooperating"  # 合作中
    PAUSED = "paused"  # 暂停
    LOST = "lost"  # 流失


class Customer(Base, UUIDMixin, TimestampMixin):
    """
    客户模型

    代表货运代理公司的客户（其他货运公司、物流公司等）
    """

    # ==================== 公司信息 ====================
    company_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        index=True,
    )
    company_name_en: Mapped[Optional[str]] = mapped_column(
        String(200),
        nullable=True,
    )
    company_name_local: Mapped[Optional[str]] = mapped_column(
        String(200),
        nullable=True,
    )
    logo_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )
    website: Mapped[Optional[str]] = mapped_column(
        String(200),
        nullable=True,
    )
    established_year: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )
    registered_capital: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )
    company_size: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )

    # ==================== 业务信息 ====================
    business_type: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        index=True,
    )
    # MySQL 不支持 ARRAY，使用 JSON 存储列表
    main_ports: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
    )
    route_coverage: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
    )
    cargo_specialization: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
    )
    estimated_volume: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )

    # ==================== 联系信息 ====================
    country_code: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        index=True,
    )
    country: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )
    city: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )
    address: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    phone: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )
    email: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )
    whatsapp: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )
    wechat: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )
    linkedin_url: Mapped[Optional[str]] = mapped_column(
        String(200),
        nullable=True,
    )
    facebook_url: Mapped[Optional[str]] = mapped_column(
        String(200),
        nullable=True,
    )

    # ==================== 客户管理 ====================
    status: Mapped[str] = mapped_column(
        String(20),
        default=CustomerStatus.POTENTIAL,
        nullable=False,
        index=True,
    )
    assigned_to: Mapped[Optional[str]] = mapped_column(
        String(36),  # CHAR(36) 存储 UUID
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    priority: Mapped[int] = mapped_column(
        Integer,
        default=3,
        nullable=False,
    )  # 1-5, 1 highest
    source: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )  # 数据来源
    source_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )
    data_confidence: Mapped[Optional[float]] = mapped_column(
        Integer,
        nullable=True,
    )  # 数据可信度 0-100 (存储为整数)
    last_verified_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
    )

    # ==================== 标签和分类 ====================
    # MySQL 不支持 ARRAY，使用 JSON 存储列表
    tags: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
    )
    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    # ==================== 时间戳 ====================
    first_contact_date: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
    )
    cooperation_date: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
    )

    # ==================== 关系 ====================
    # assigned_user = relationship("User", back_populates="customers")

    def __repr__(self) -> str:
        return f"<Customer(id={self.id}, company={self.company_name}, country={self.country})>"

    @property
    def is_assigned(self) -> bool:
        """是否已分配"""
        return self.assigned_to is not None

    @property
    def business_type_display(self) -> str:
        """业务类型显示名称"""
        display_map = {
            BusinessType.SEA: "海运",
            BusinessType.AIR: "空运",
            BusinessType.LAND: "陆运",
            BusinessType.MULTIMODAL: "多式联运",
        }
        return display_map.get(self.business_type, self.business_type)

    @property
    def status_display(self) -> str:
        """状态显示名称"""
        display_map = {
            CustomerStatus.POTENTIAL: "潜在客户",
            CustomerStatus.CONTACTING: "联系中",
            CustomerStatus.COOPERATING: "合作中",
            CustomerStatus.PAUSED: "暂停",
            CustomerStatus.LOST: "流失",
        }
        return display_map.get(self.status, self.status)

    @property
    def main_ports_list(self) -> list:
        """获取港口列表（从 JSON 转换）"""
        if self.main_ports and isinstance(self.main_ports, dict):
            return list(self.main_ports.keys()) if self.main_ports else []
        return []

    @property
    def tags_list(self) -> list:
        """获取标签列表（从 JSON 转换）"""
        if self.tags and isinstance(self.tags, dict):
            return list(self.tags.keys()) if self.tags else []
        return []
