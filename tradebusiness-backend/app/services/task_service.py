"""
任务服务
处理任务相关的业务逻辑
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppException
from app.models.task import Task, TaskPriority, TaskStatus
from app.repositories.task_repo import TaskRepository


class TaskNotFoundException(AppException):
    """任务不存在异常"""

    def __init__(self, task_id: str):
        super().__init__(message=f"Task {task_id} not found", code="TASK_NOT_FOUND")


class TaskService:
    """任务服务"""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.task_repo = TaskRepository(session)

    async def get_task(self, task_id: str) -> Task:
        """
        获取任务详情

        Args:
            task_id: 任务ID

        Returns:
            任务对象

        Raises:
            TaskNotFoundException: 任务不存在
        """
        task = await self.task_repo.get_by_id(task_id)
        if not task:
            raise TaskNotFoundException(task_id)
        return task

    async def list_tasks(
        self,
        skip: int = 0,
        limit: int = 20,
        assigned_to: Optional[str] = None,
        status: Optional[TaskStatus] = None,
        priority: Optional[str] = None,
        customer_id: Optional[str] = None,
    ) -> tuple[List[Task], int]:
        """
        获取任务列表

        Args:
            skip: 跳过记录数
            limit: 返回记录数
            assigned_to: 分配给的用户ID
            status: 状态筛选
            priority: 优先级筛选
            customer_id: 客户ID筛选

        Returns:
            (任务列表, 总数)
        """

        # 构建查询条件
        conditions = []

        if assigned_to:
            conditions.append(Task.assigned_to == assigned_to)
        if status:
            conditions.append(Task.status == status)
        if priority:
            conditions.append(Task.priority == priority)
        if customer_id:
            conditions.append(Task.customer_id == customer_id)

        # 获取总数
        if conditions:
            count_stmt = select(func.count(Task.id)).where(and_(*conditions))
        else:
            count_stmt = select(func.count(Task.id))

        count_result = await self.session.execute(count_stmt)
        total = count_result.scalar() or 0

        # 获取分页数据
        stmt = select(Task)
        if conditions:
            stmt = stmt.where(and_(*conditions))

        stmt = stmt.order_by(Task.created_at.desc()).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        tasks = result.scalars().all()

        return list(tasks), total

    async def create_task(
        self,
        title: str,
        assigned_to: str,
        created_by: str,
        description: Optional[str] = None,
        type: Optional[str] = None,
        customer_id: Optional[str] = None,
        priority: str = TaskPriority.MEDIUM,
        due_date: Optional[datetime] = None,
        reminder_at: Optional[datetime] = None,
    ) -> Task:
        """
        创建任务

        Args:
            title: 任务标题
            assigned_to: 分配给的用户ID
            created_by: 创建者用户ID
            description: 任务描述
            type: 任务类型
            customer_id: 关联客户ID
            priority: 优先级
            due_date: 截止日期
            reminder_at: 提醒时间

        Returns:
            创建的任务对象
        """
        task = await self.task_repo.create(
            title=title,
            description=description,
            type=type,
            customer_id=customer_id,
            assigned_to=assigned_to,
            created_by=created_by,
            priority=priority,
            due_date=due_date,
            reminder_at=reminder_at,
            status=TaskStatus.PENDING,
            is_reminded=False,
        )

        return task

    async def update_task(self, task_id: str, **kwargs) -> Task:
        """
        更新任务

        Args:
            task_id: 任务ID
            **kwargs: 要更新的字段

        Returns:
            更新后的任务对象

        Raises:
            TaskNotFoundException: 任务不存在
        """
        task = await self.get_task(task_id)

        # 如果状态改为完成，记录完成时间
        if "status" in kwargs and kwargs["status"] == TaskStatus.COMPLETED:
            kwargs["completed_at"] = datetime.utcnow()

        updated_task = await self.task_repo.update(task, **kwargs)
        return updated_task

    async def delete_task(self, task_id: str) -> None:
        """
        删除任务

        Args:
            task_id: 任务ID

        Raises:
            TaskNotFoundException: 任务不存在
        """
        task = await self.get_task(task_id)
        await self.task_repo.delete(task)

    async def complete_task(self, task_id: str) -> Task:
        """
        完成任务

        Args:
            task_id: 任务ID

        Returns:
            更新后的任务对象

        Raises:
            TaskNotFoundException: 任务不存在
        """
        return await self.update_task(
            task_id,
            status=TaskStatus.COMPLETED,
            completed_at=datetime.utcnow(),
        )

    async def get_my_tasks(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 20,
        status: Optional[TaskStatus] = None,
    ) -> tuple[List[Task], int]:
        """
        获取分配给我的任务列表

        Args:
            user_id: 用户ID
            skip: 跳过记录数
            limit: 返回记录数
            status: 状态筛选

        Returns:
            (任务列表, 总数)
        """
        return await self.task_repo.get_by_assigned_user(
            user_id=user_id,
            skip=skip,
            limit=limit,
            status=status,
        )

    async def get_overdue_tasks(self) -> List[Task]:
        """
        获取所有逾期未完成的任务

        Returns:
            逾期任务列表
        """
        return await self.task_repo.get_overdue_tasks()

    async def get_my_overdue_tasks(self, user_id: str) -> List[Task]:
        """
        获取指定用户的逾期任务

        Args:
            user_id: 用户ID

        Returns:
            逾期任务列表
        """
        from sqlalchemy import and_

        now = datetime.utcnow()
        stmt = (
            select(Task)
            .where(
                and_(
                    Task.assigned_to == user_id,
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
        return await self.task_repo.get_upcoming_tasks(user_id, days)

    async def get_task_statistics(self, user_id: Optional[str] = None) -> dict:
        """
        获取任务统计信息

        Args:
            user_id: 用户ID（可选）

        Returns:
            统计数据字典
        """
        return await self.task_repo.get_task_statistics(user_id)

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
        return await self.task_repo.get_tasks_by_customer(
            customer_id=customer_id,
            skip=skip,
            limit=limit,
        )

    async def mark_task_as_reminded(self, task_id: str) -> None:
        """
        标记任务为已提醒

        Args:
            task_id: 任务ID

        Raises:
            TaskNotFoundException: 任务不存在
        """
        await self.task_repo.mark_as_reminded(task_id)
