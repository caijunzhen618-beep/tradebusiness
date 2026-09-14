"""
Repository 基类
定义所有 Repository 的通用方法
"""

from typing import Generic, Optional, Type, TypeVar

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    """
    Repository 基类

    提供通用的 CRUD 操作
    """

    def __init__(self, model: Type[ModelType], session: AsyncSession) -> None:
        """
        初始化 Repository

        Args:
            model: SQLAlchemy 模型类
            session: 数据库会话
        """
        self.model = model
        self.session = session

    async def get_by_id(self, id: str) -> Optional[ModelType]:
        """
        通过 ID 获取单个对象

        Args:
            id: 对象 ID

        Returns:
            模型对象或 None
        """
        from sqlalchemy import select

        stmt = select(self.model).where(self.model.id == id)  # type: ignore
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> list[ModelType]:
        """
        获取所有对象（分页）

        Args:
            skip: 跳过的记录数
            limit: 返回的记录数

        Returns:
            模型对象列表
        """
        from sqlalchemy import select

        stmt = (
            select(self.model)
            .order_by(self.model.created_at.desc())  # type: ignore
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, **kwargs) -> ModelType:
        """
        创建新对象

        Args:
            **kwargs: 模型字段值

        Returns:
            创建的模型对象
        """
        obj = self.model(**kwargs)  # type: ignore
        self.session.add(obj)
        await self.session.flush()
        return obj

    async def update(self, obj: ModelType, **kwargs) -> ModelType:
        """
        更新对象

        Args:
            obj: 要更新的模型对象
            **kwargs: 要更新的字段和值

        Returns:
            更新后的模型对象
        """
        for key, value in kwargs.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        await self.session.flush()
        return obj

    async def delete(self, obj: ModelType) -> None:
        """
        删除对象

        Args:
            obj: 要删除的模型对象
        """
        await self.session.delete(obj)
        await self.session.flush()

    async def count(self) -> int:
        """
        统计对象总数

        Returns:
            总数
        """
        from sqlalchemy import func

        stmt = select(func.count()).select_from(self.model)
        result = await self.session.execute(stmt)
        return result.scalar() or 0

    async def exists(self, id: str) -> bool:
        """
        检查指定 ID 的对象是否存在

        Args:
            id: 对象 ID

        Returns:
            是否存在
        """
        from sqlalchemy import select

        stmt = select(self.model).where(self.model.id == id)  # type: ignore
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None
