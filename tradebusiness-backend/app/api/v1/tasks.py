"""
任务管理 API
包含任务的 CRUD 操作
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_admin_user, get_current_user, get_db
from app.models.task import TaskStatus
from app.models.user import User
from app.schemas.common import MessageResponse, PaginatedResponse
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate
from app.services.task_service import TaskService

router = APIRouter()


@router.get("", response_model=PaginatedResponse[TaskResponse])
async def list_tasks(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(20, ge=1, le=100, description="返回的记录数"),
    status: Optional[TaskStatus] = Query(None, description="状态筛选"),
    priority: Optional[str] = Query(None, description="优先级筛选"),
    customer_id: Optional[str] = Query(None, description="客户ID筛选"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取任务列表

    支持分页和筛选。
    """
    task_service = TaskService(db)

    # 非管理员只能查看分配给自己的任务
    assigned_to = None
    if not current_user.is_admin:
        assigned_to = current_user.id

    tasks, total = await task_service.list_tasks(
        skip=skip,
        limit=limit,
        assigned_to=assigned_to,
        status=status,
        priority=priority,
        customer_id=customer_id,
    )

    task_responses = [
        TaskResponse(
            id=str(task.id),
            title=task.title,
            description=task.description,
            type=task.type,
            status=task.status.value if hasattr(task.status, "value") else task.status,
            priority=task.priority.value if hasattr(task.priority, "value") else task.priority,
            customer_id=str(task.customer_id) if task.customer_id else None,
            assigned_to=str(task.assigned_to) if task.assigned_to else None,
            created_by=str(task.created_by) if task.created_by else None,
            due_date=task.due_date,
            completed_at=task.completed_at,
            reminder_at=task.reminder_at,
            is_reminded=task.is_reminded,
            created_at=task.created_at,
            updated_at=task.updated_at,
        )
        for task in tasks
    ]

    return PaginatedResponse.create(
        items=task_responses,
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/my", response_model=PaginatedResponse[TaskResponse])
async def get_my_tasks(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(20, ge=1, le=100, description="返回的记录数"),
    status: Optional[TaskStatus] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取分配给我的任务列表
    """
    task_service = TaskService(db)

    tasks, total = await task_service.get_my_tasks(
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        status=status,
    )

    task_responses = [
        TaskResponse(
            id=str(task.id),
            title=task.title,
            description=task.description,
            type=task.type,
            status=task.status.value if hasattr(task.status, "value") else task.status,
            priority=task.priority.value if hasattr(task.priority, "value") else task.priority,
            customer_id=str(task.customer_id) if task.customer_id else None,
            assigned_to=str(task.assigned_to) if task.assigned_to else None,
            created_by=str(task.created_by) if task.created_by else None,
            due_date=task.due_date,
            completed_at=task.completed_at,
            reminder_at=task.reminder_at,
            is_reminded=task.is_reminded,
            created_at=task.created_at,
            updated_at=task.updated_at,
        )
        for task in tasks
    ]

    return PaginatedResponse.create(
        items=task_responses,
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/overdue", response_model=list[TaskResponse])
async def get_overdue_tasks(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取逾期任务

    非管理员只能查看自己的逾期任务。
    """
    task_service = TaskService(db)

    if current_user.is_admin:
        tasks = await task_service.get_overdue_tasks()
    else:
        tasks = await task_service.get_my_overdue_tasks(current_user.id)

    return [
        TaskResponse(
            id=str(task.id),
            title=task.title,
            description=task.description,
            type=task.type,
            status=task.status.value if hasattr(task.status, "value") else task.status,
            priority=task.priority.value if hasattr(task.priority, "value") else task.priority,
            customer_id=str(task.customer_id) if task.customer_id else None,
            assigned_to=str(task.assigned_to) if task.assigned_to else None,
            created_by=str(task.created_by) if task.created_by else None,
            due_date=task.due_date,
            completed_at=task.completed_at,
            reminder_at=task.reminder_at,
            is_reminded=task.is_reminded,
            created_at=task.created_at,
            updated_at=task.updated_at,
        )
        for task in tasks
    ]


@router.get("/upcoming", response_model=list[TaskResponse])
async def get_upcoming_tasks(
    days: int = Query(7, ge=1, le=30, description="天数"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取即将到期的任务
    """
    task_service = TaskService(db)

    tasks = await task_service.get_upcoming_tasks(current_user.id, days)

    return [
        TaskResponse(
            id=str(task.id),
            title=task.title,
            description=task.description,
            type=task.type,
            status=task.status.value if hasattr(task.status, "value") else task.status,
            priority=task.priority.value if hasattr(task.priority, "value") else task.priority,
            customer_id=str(task.customer_id) if task.customer_id else None,
            assigned_to=str(task.assigned_to) if task.assigned_to else None,
            created_by=str(task.created_by) if task.created_by else None,
            due_date=task.due_date,
            completed_at=task.completed_at,
            reminder_at=task.reminder_at,
            is_reminded=task.is_reminded,
            created_at=task.created_at,
            updated_at=task.updated_at,
        )
        for task in tasks
    ]


@router.get("/stats")
async def get_task_statistics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取任务统计信息
    """
    task_service = TaskService(db)

    user_id = None if current_user.is_admin else current_user.id
    stats = await task_service.get_task_statistics(user_id)

    return stats


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取任务详情
    """
    task_service = TaskService(db)
    task = await task_service.get_task(task_id)

    # 非管理员只能查看分配给自己的任务
    if not current_user.is_admin and task.assigned_to != current_user.id:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own tasks",
        )

    return TaskResponse(
        id=str(task.id),
        title=task.title,
        description=task.description,
        type=task.type,
        status=task.status.value if hasattr(task.status, "value") else task.status,
        priority=task.priority.value if hasattr(task.priority, "value") else task.priority,
        customer_id=str(task.customer_id) if task.customer_id else None,
        assigned_to=str(task.assigned_to) if task.assigned_to else None,
        created_by=str(task.created_by) if task.created_by else None,
        due_date=task.due_date,
        completed_at=task.completed_at,
        reminder_at=task.reminder_at,
        is_reminded=task.is_reminded,
        created_at=task.created_at,
        updated_at=task.updated_at,
    )


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    创建新任务
    """
    task_service = TaskService(db)

    # 非管理员只能创建分配给自己的任务
    assigned_to = task_data.assigned_to
    if not current_user.is_admin:
        assigned_to = current_user.id

    task = await task_service.create_task(
        title=task_data.title,
        description=task_data.description,
        type=task_data.type,
        customer_id=task_data.customer_id,
        assigned_to=assigned_to,
        created_by=current_user.id,
        priority=task_data.priority,
        due_date=task_data.due_date,
        reminder_at=task_data.reminder_at,
    )

    return TaskResponse(
        id=str(task.id),
        title=task.title,
        description=task.description,
        type=task.type,
        status=task.status.value if hasattr(task.status, "value") else task.status,
        priority=task.priority.value if hasattr(task.priority, "value") else task.priority,
        customer_id=str(task.customer_id) if task.customer_id else None,
        assigned_to=str(task.assigned_to) if task.assigned_to else None,
        created_by=str(task.created_by) if task.created_by else None,
        due_date=task.due_date,
        completed_at=task.completed_at,
        reminder_at=task.reminder_at,
        is_reminded=task.is_reminded,
        created_at=task.created_at,
        updated_at=task.updated_at,
    )


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str,
    task_data: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    更新任务
    """
    task_service = TaskService(db)
    task = await task_service.get_task(task_id)

    # 非管理员只能更新分配给自己的任务
    if not current_user.is_admin and task.assigned_to != current_user.id:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own tasks",
        )

    # 非管理员不能修改 assigned_to
    update_data = task_data.model_dump(exclude_unset=True)
    if not current_user.is_admin:
        update_data.pop("assigned_to", None)

    updated_task = await task_service.update_task(task_id, **update_data)

    return TaskResponse(
        id=str(updated_task.id),
        title=updated_task.title,
        description=updated_task.description,
        type=updated_task.type,
        status=(
            updated_task.status.value
            if hasattr(updated_task.status, "value")
            else updated_task.status
        ),
        priority=(
            updated_task.priority.value
            if hasattr(updated_task.priority, "value")
            else updated_task.priority
        ),
        customer_id=str(updated_task.customer_id) if updated_task.customer_id else None,
        assigned_to=str(updated_task.assigned_to) if updated_task.assigned_to else None,
        created_by=str(updated_task.created_by) if updated_task.created_by else None,
        due_date=updated_task.due_date,
        completed_at=updated_task.completed_at,
        reminder_at=updated_task.reminder_at,
        is_reminded=updated_task.is_reminded,
        created_at=updated_task.created_at,
        updated_at=updated_task.updated_at,
    )


@router.post("/{task_id}/complete", response_model=TaskResponse)
async def complete_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    完成任务
    """
    task_service = TaskService(db)
    task = await task_service.get_task(task_id)

    # 非管理员只能完成分配给自己的任务
    if not current_user.is_admin and task.assigned_to != current_user.id:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only complete your own tasks",
        )

    completed_task = await task_service.complete_task(task_id)

    return TaskResponse(
        id=str(completed_task.id),
        title=completed_task.title,
        description=completed_task.description,
        type=completed_task.type,
        status=(
            completed_task.status.value
            if hasattr(completed_task.status, "value")
            else completed_task.status
        ),
        priority=(
            completed_task.priority.value
            if hasattr(completed_task.priority, "value")
            else completed_task.priority
        ),
        customer_id=str(completed_task.customer_id) if completed_task.customer_id else None,
        assigned_to=str(completed_task.assigned_to) if completed_task.assigned_to else None,
        created_by=str(completed_task.created_by) if completed_task.created_by else None,
        due_date=completed_task.due_date,
        completed_at=completed_task.completed_at,
        reminder_at=completed_task.reminder_at,
        is_reminded=completed_task.is_reminded,
        created_at=completed_task.created_at,
        updated_at=completed_task.updated_at,
    )


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: str,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    删除任务

    需要管理员权限。
    """
    task_service = TaskService(db)
    await task_service.delete_task(task_id)
