"""
数据采集任务模型
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import JSON, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDMixin


class TaskStatus(str, Enum):
    """任务状态枚举"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ScrapingTask(Base, TimestampMixin, UUIDMixin):
    """数据采集任务模型"""

    __tablename__ = "scraping_tasks"

    # 基本信息
    name: Mapped[str] = mapped_column(String(200), nullable=False, comment="任务名称")
    task_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="任务类型：google, kompass, yellow_pages, port_authorities",
    )
    status: Mapped[str] = mapped_column(
        String(20), default=TaskStatus.PENDING.value, nullable=False, comment="任务状态"
    )

    # 配置
    config: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict, comment="任务配置")
    keywords: Mapped[list] = mapped_column(JSON, nullable=False, default=list, comment="关键词列表")
    countries: Mapped[list] = mapped_column(
        JSON, nullable=False, default=list, comment="国家代码列表"
    )
    source_urls: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
        comment="采集数据来源地址列表",
    )

    # 进度统计
    progress_current: Mapped[int] = mapped_column(Integer, default=0, comment="当前执行步骤")
    progress_total: Mapped[int] = mapped_column(Integer, default=0, comment="总执行步骤")
    total_found: Mapped[int] = mapped_column(Integer, default=0, comment="发现数据总数")
    total_saved: Mapped[int] = mapped_column(Integer, default=0, comment="已保存数据数")
    status_message: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="当前状态说明"
    )
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="错误信息")
    last_run_summary: Mapped[Optional[dict]] = mapped_column(
        JSON, nullable=True, comment="最近一次执行摘要"
    )
    execution_log: Mapped[list] = mapped_column(
        JSON, nullable=False, default=list, comment="执行日志"
    )

    # 时间戳
    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="开始时间"
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="完成时间"
    )

    # 关联
    created_by: Mapped[str] = mapped_column(String(36), nullable=False, comment="创建者ID")

    def __repr__(self):
        return f"<ScrapingTask(id={self.id}, name={self.name}, status={self.status})>"
