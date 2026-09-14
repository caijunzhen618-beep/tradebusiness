"""
节假日模型
定义全球节假日数据
"""

import uuid
from datetime import date, datetime
from typing import Optional

from sqlalchemy import Boolean, Date, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDMixin


class Holiday(Base, UUIDMixin, TimestampMixin):
    """
    节假日模型
    """

    country_code: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    local_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )
    holiday_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
    )
    type: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
    )  # public, religious, observance
    is_recurring: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<Holiday({self.country_code}, {self.name}, {self.holiday_date})>"
