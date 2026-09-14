"""
数据库模型基类
定义所有模型的基础字段和通用方法
"""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column


class Base(DeclarativeBase):
    """
    SQLAlchemy 声明式基类

    所有 ORM 模型的基类，提供：
    - 自动生成表名（类名转蛇形命名）
    - 通用的 CRUD 方法接口
    """

    @declared_attr.directive
    def __tablename__(cls) -> str:
        """自动生成表名：将类名从 PascalCase 转为 snake_case"""
        name = cls.__name__
        # 使用简单算法转换大小写
        result = [name[0].lower()]
        for char in name[1:]:
            if char.isupper():
                result.extend(["_", char.lower()])
            else:
                result.append(char)
        return "".join(result) + "s"  # 添加 's' 使表名变为复数

    def to_dict(self) -> dict[str, Any]:
        """
        将模型转换为字典

        Returns:
            模型数据的字典表示
        """
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def update(self, **kwargs: Any) -> None:
        """
        更新模型属性

        Args:
            **kwargs: 要更新的字段和值
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)


class TimestampMixin:
    """
    时间戳混入类

    为模型添加 created_at 和 updated_at 字段
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class UUIDMixin:
    """
    UUID 混入类

    为模型添加字符串类型的 UUID id 字段
    MySQL 使用 CHAR(36) 存储 UUID 字符串
    """

    id: Mapped[str] = mapped_column(
        String(36),  # CHAR(36) 存储 UUID 字符串
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        nullable=False,
    )
