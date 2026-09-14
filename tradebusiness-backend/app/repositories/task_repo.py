"""
任务数据访问层
处理任务的数据库操作
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import UUIDMixin
from app.models.task import Task, TaskPriority, TaskStatus
from app.repositories.base import BaseRepository


class TaskRepository(BaseRepository[Task]):
    """任务Repository"""

    def __init__(self, session: AsyncSession):
        super().__init__(Task, session)

    async def get_by_assigned_user(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 20,
        status: Optional[TaskStatus] = None,
    ) -> tuple[List[Task], int]:
        """
        获取分配给指定用户的任务列表

        Args:
            user_id: 用户ID
            skip: 跳过记录数
            limit: 返回记录数
            status: 状态筛选

        Returns:
            (任务列表, 总数)
        """
        # 构建查询条件
        conditions = [Task.assigned_to == user_id]

        if status:
            conditions.append(Task.status == status)

        # 获取总数
        count_stmt = select(Task).where(and_(*conditions))
        count_result = await self.session.execute(count_stmt)
        total = len(count_result.scalars().all())

        # 获取分页数据
        stmt = (
            select(Task)
            .where(and_(*conditions))
            .order_by(Task.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        tasks = result.scalars().all()

        return list(tasks), total

    async def get_overdue_tasks(self) -> List[Task]:
        """
        获取所有逾期未完成的任务

        Returns:
            逾期任务列表
        """
        now = datetime.utcnow()
        stmt = (
            select(Task)
            .where(
                and_(
                    Task.due_date < now,
                    Task.status.in_([TaskStatus.PENDING, TaskStatus.IN_PROGRESS]),
                )
            )
            .order_by(Task.due_date.asc())
        )

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_upcoming_tasks(self, user_id: str, days: int = 7) -> List[Task]:
        """
        获取指定用户在未来几天内到期的任务

        Args:
            user_id: 用户ID
            days: 天数

        Returns:
            即将到期的任务列表
        """
        from datetime import timedelta

        now = datetime.utcnow()
        future = now + timedelta(days=days)

        stmt = (
            select(Task)
            .where(
                and_(
                    Task.assigned_to == user_id,
                    Task.due_date >= now,
                    Task.due_date <= future,
                    Task.status.in_([TaskStatus.PENDING, TaskStatus.IN_PROGRESS]),
                )
            )
            .order_by(Task.due_date.asc())
        )

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_tasks_by_customer(
        self,
        customer_id: str,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[List[Task], int]:
        """
        获取关联到指定客户的任务

        Args:
            customer_id: 客户ID
            skip: 跳过记录数
            limit: 返回记录数

        Returns:
            (任务列表, 总数)
        """
        # 获取总数
        count_stmt = select(Task).where(Task.customer_id == customer_id)
        count_result = await self.session.execute(count_stmt)
        total = len(count_result.scalars().all())

        # 获取分页数据
        stmt = (
            select(Task)
            .where(Task.customer_id == customer_id)
            .order_by(Task.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        tasks = result.scalars().all()

        return list(tasks), total

    async def get_task_statistics(self, user_id: Optional[str] = None) -> dict:
        """
        获取任务统计信息

        Args:
            user_id: 用户ID（可选，如果提供则统计该用户的任务）

        Returns:
            统计数据字典
        """
        from sqlalchemy import case, func

        # 构建基础查询
        base_query = select(Task)
        if user_id:
            base_query = base_query.where(Task.assigned_to == user_id)

        # 总任务数
        total_stmt = select(func.count()).select_from(base_query.subquery())
        total_result = await self.session.execute(total_stmt)
        total = total_result.scalar() or 0

        # 按状态统计
        stmt = select(Task.status, func.count(Task.id)).group_by(Task.status)

        if user_id:
            stmt = stmt.where(Task.assigned_to == user_id)

        result = await self.session.execute(stmt)
        by_status = {status.value: count for status, count in result.all()}

        # 按优先级统计
        stmt = select(Task.priority, func.count(Task.id)).group_by(Task.priority)

        if user_id:
            stmt = stmt.where(Task.assigned_to == user_id)

        result = await self.session.execute(stmt)
        by_priority = {priority: count for priority, count in result.all()}

        # 逾期任务数
        overdue_stmt = select(func.count()).select_from(
            select(Task)
            .where(
                and_(
                    Task.due_date < datetime.utcnow(),
                    Task.status.in_([TaskStatus.PENDING, TaskStatus.IN_PROGRESS]),
                )
            )
            .subquery()
        )

        if user_id:
            overdue_stmt = select(func.count()).select_from(
                select(Task)
                .where(
                    and_(
                        Task.assigned_to == user_id,
                        Task.due_date < datetime.utcnow(),
                        Task.status.in_([TaskStatus.PENDING, TaskStatus.IN_PROGRESS]),
                    )
                )
                .subquery()
            )

        overdue_result = await self.session.execute(overdue_stmt)
        overdue = overdue_result.scalar() or 0

        return {
            "total": total,
            "by_status": by_status,
            "by_priority": by_priority,
            "overdue": overdue,
        }

    async def mark_as_reminded(self, task_id: str) -> None:
        """
        标记任务为已提醒

        Args:
            task_id: 任务ID
        """
        task = await self.get_by_id(task_id)
        if task:
            task.is_reminded = True
            await self.session.flush()
