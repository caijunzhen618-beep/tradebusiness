"""
AI 获客 API
提供获客任务、潜客、企业背调和开发信生成接口。
"""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.core.audit import audit_event
from app.models.lead_generation import FollowupTask
from app.models.user import User
from app.schemas.common import PaginatedResponse
from app.schemas.lead_generation import (
    CompanyResearchReportResponse,
    FollowupTaskCreate,
    FollowupTaskResponse,
    LeadContactCreate,
    LeadContactResponse,
    LeadCreate,
    LeadEmailSendRequest,
    LeadGenerationStatsResponse,
    LeadResponse,
    LeadSearchTaskCreate,
    LeadSearchTaskResponse,
    LeadUpdate,
    SalesCopyCreate,
    SalesCopyResponse,
)
from app.services.company_research_service import CompanyResearchService
from app.services.email_service import EmailService
from app.services.lead_generation_service import LeadGenerationService
from app.services.sales_copy_service import SalesCopyService

router = APIRouter()


@router.post(
    "/tasks",
    response_model=LeadSearchTaskResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_lead_task(
    task_data: LeadSearchTaskCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> LeadSearchTaskResponse:
    """创建 AI 获客任务。"""
    service = LeadGenerationService(db)
    task = await service.create_task(str(current_user.id), task_data.model_dump())
    return _task_to_response(task)


@router.get("/tasks", response_model=PaginatedResponse[LeadSearchTaskResponse])
async def list_lead_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[LeadSearchTaskResponse]:
    """获取当前用户的 AI 获客任务列表。"""
    service = LeadGenerationService(db)
    tasks, total = await service.list_tasks(str(current_user.id), skip, limit, status_filter)
    return PaginatedResponse.create(
        items=[_task_to_response(task) for task in tasks],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/tasks/{task_id}", response_model=LeadSearchTaskResponse)
async def get_lead_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> LeadSearchTaskResponse:
    """获取 AI 获客任务详情。"""
    service = LeadGenerationService(db)
    task = await service.get_task(task_id, str(current_user.id))
    return _task_to_response(task)


@router.post("/tasks/{task_id}/run", response_model=LeadSearchTaskResponse)
async def run_lead_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> LeadSearchTaskResponse:
    """运行 AI 获客任务。"""
    service = LeadGenerationService(db)
    task = await service.get_task(task_id, str(current_user.id))

    # 先将任务状态提交到数据库，避免 Celery worker 抢到尚未提交的任务。
    task.status = "running"
    task.error_message = None
    await db.commit()

    try:
        from app.tasks.automation_tasks import run_lead_search_task

        run_lead_search_task.delay(task_id, str(current_user.id))
    except Exception:
        # 本地未启动 Redis/Celery 时保留同步回退，开发环境仍可直接使用。
        task = await service.run_task(task_id, str(current_user.id))
    return _task_to_response(task)


@router.post("/tasks/{task_id}/cancel", response_model=LeadSearchTaskResponse)
async def cancel_lead_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> LeadSearchTaskResponse:
    """取消尚未完成的 AI 获客任务。"""
    service = LeadGenerationService(db)
    task = await service.cancel_task(task_id, str(current_user.id))
    return _task_to_response(task)


@router.post("/leads", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
async def create_lead(
    lead_data: LeadCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> LeadResponse:
    """手动创建潜客。"""
    service = LeadGenerationService(db)
    lead = await service.create_lead(str(current_user.id), lead_data.model_dump())
    return LeadResponse.model_validate(lead)


@router.get("/leads", response_model=PaginatedResponse[LeadResponse])
async def list_leads(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    task_id: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[LeadResponse]:
    """获取当前用户的 AI 潜客列表。"""
    service = LeadGenerationService(db)
    leads, total = await service.list_leads(
        user_id=str(current_user.id),
        skip=skip,
        limit=limit,
        task_id=task_id,
        status_filter=status_filter,
        search=search,
    )
    return PaginatedResponse.create(
        items=[LeadResponse.model_validate(lead) for lead in leads],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/leads/{lead_id}", response_model=LeadResponse)
async def get_lead(
    lead_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> LeadResponse:
    """获取 AI 潜客详情。"""
    service = LeadGenerationService(db)
    lead = await service.get_lead(lead_id, str(current_user.id))
    return LeadResponse.model_validate(lead)


@router.patch("/leads/{lead_id}", response_model=LeadResponse)
async def update_lead(
    lead_id: str,
    lead_data: LeadUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> LeadResponse:
    """更新 AI 潜客。"""
    service = LeadGenerationService(db)
    lead = await service.update_lead(
        lead_id,
        str(current_user.id),
        lead_data.model_dump(exclude_unset=True),
    )
    return LeadResponse.model_validate(lead)


@router.post(
    "/leads/{lead_id}/contacts",
    response_model=LeadContactResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_lead_contact(
    lead_id: str,
    contact_data: LeadContactCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> LeadContactResponse:
    """为潜客创建联系人。"""
    service = LeadGenerationService(db)
    contact = await service.create_contact(
        lead_id,
        str(current_user.id),
        contact_data.model_dump(exclude={"lead_id"}),
    )
    return LeadContactResponse.model_validate(contact)


@router.get("/leads/{lead_id}/contacts", response_model=list[LeadContactResponse])
async def list_lead_contacts(
    lead_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[LeadContactResponse]:
    """获取潜客联系人列表。"""
    service = LeadGenerationService(db)
    contacts = await service.list_contacts(lead_id, str(current_user.id))
    return [LeadContactResponse.model_validate(contact) for contact in contacts]


@router.post(
    "/leads/{lead_id}/research",
    response_model=CompanyResearchReportResponse,
    status_code=status.HTTP_201_CREATED,
)
async def generate_company_research(
    lead_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CompanyResearchReportResponse:
    """为潜客生成企业背调报告。"""
    service = CompanyResearchService(db)
    report = await service.generate_report(lead_id, str(current_user.id))
    return CompanyResearchReportResponse.model_validate(report)


@router.get("/leads/{lead_id}/research", response_model=CompanyResearchReportResponse | None)
async def get_company_research(
    lead_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CompanyResearchReportResponse | None:
    """获取潜客最新企业背调报告。"""
    service = CompanyResearchService(db)
    report = await service.get_latest_report(lead_id, str(current_user.id))
    return CompanyResearchReportResponse.model_validate(report) if report else None


@router.post(
    "/leads/{lead_id}/sales-copy",
    response_model=SalesCopyResponse,
    status_code=status.HTTP_201_CREATED,
)
async def generate_sales_copy(
    lead_id: str,
    copy_data: SalesCopyCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SalesCopyResponse:
    """为潜客生成开发信或渠道话术。"""
    service = SalesCopyService(db)
    sales_copy = await service.generate_sales_copy(
        lead_id=lead_id,
        user_id=str(current_user.id),
        channel=copy_data.channel.value,
        language=copy_data.language,
        tone=copy_data.tone,
        agent_id=copy_data.agent_id,
        template_id=copy_data.template_id,
    )
    return SalesCopyResponse.model_validate(sales_copy)


@router.get("/leads/{lead_id}/sales-copies", response_model=list[SalesCopyResponse])
async def list_sales_copies(
    lead_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[SalesCopyResponse]:
    """获取潜客开发信列表。"""
    service = SalesCopyService(db)
    copies = await service.list_sales_copies(lead_id, str(current_user.id))
    return [SalesCopyResponse.model_validate(item) for item in copies]


def _task_to_response(task) -> LeadSearchTaskResponse:
    """将获客任务模型转换为响应 Schema。"""
    return LeadSearchTaskResponse(
        id=task.id,
        user_id=task.user_id,
        name=task.name,
        target_country=task.target_country,
        target_industry=task.target_industry,
        product_keywords=(task.product_keywords or {}).get("items", []),
        customer_profile=task.customer_profile,
        exclude_keywords=(task.exclude_keywords or {}).get("items", []),
        website_inputs=(task.website_inputs or {}).get("items", []),
        status=task.status,
        total_found=task.total_found,
        error_message=task.error_message,
        created_at=task.created_at,
        updated_at=task.updated_at,
    )


@router.post(
    "/leads/{lead_id}/send-email", response_model=dict, status_code=status.HTTP_201_CREATED
)
async def send_lead_email(
    lead_id: str,
    email_data: LeadEmailSendRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """人工确认后发送潜客开发信并记录结果。"""
    service = LeadGenerationService(db)
    lead = await service.get_lead(lead_id, str(current_user.id))
    service.ensure_lead_contactable(lead)
    email = await EmailService(db).send_email(
        to_email=str(email_data.to_email),
        subject=email_data.subject,
        body=email_data.body,
        to_name=email_data.to_name,
        sender_id=current_user.id,
    )
    audit_event(
        "lead_email_sent",
        user_id=str(current_user.id),
        resource_type="lead",
        resource_id=str(lead.id),
        metadata={"recipient_domain": email_data.to_email.rsplit("@", 1)[-1]},
    )
    await service.update_lead(lead_id, str(current_user.id), {"status": "contacted"})
    return {"id": str(email.id), "status": email.status.value, "lead_id": lead.id}


@router.post("/followups", response_model=FollowupTaskResponse, status_code=status.HTTP_201_CREATED)
async def create_followup(
    data: FollowupTaskCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = LeadGenerationService(db)
    lead = await service.get_lead(data.lead_id, str(current_user.id))
    service.ensure_lead_contactable(lead)
    task = FollowupTask(user_id=str(current_user.id), **data.model_dump())
    db.add(task)
    await db.flush()
    return task


@router.get("/followups", response_model=list[FollowupTaskResponse])
async def list_followups(
    channel: Optional[str] = Query(None),
    lead_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from sqlalchemy import select

    filters = [FollowupTask.user_id == current_user.id]
    if channel:
        filters.append(FollowupTask.channel == channel)
    if lead_id:
        filters.append(FollowupTask.lead_id == lead_id)
    result = await db.execute(
        select(FollowupTask).where(*filters).order_by(FollowupTask.due_at.asc())
    )
    return list(result.scalars().all())


@router.patch("/followups/{followup_id}", response_model=FollowupTaskResponse)
async def update_followup(
    followup_id: str,
    status_value: str = Query(..., alias="status"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from fastapi import HTTPException
    from sqlalchemy import select

    result = await db.execute(
        select(FollowupTask).where(
            FollowupTask.id == followup_id, FollowupTask.user_id == current_user.id
        )
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Follow-up task not found")
    allowed_statuses = {"pending", "completed", "failed", "cancelled"}
    if status_value not in allowed_statuses:
        raise HTTPException(status_code=422, detail="Invalid follow-up status")
    if task.status == "completed" and status_value != "completed":
        raise HTTPException(status_code=409, detail="Completed follow-ups cannot be changed")
    task.status = status_value
    await db.flush()
    return task


@router.post("/followups/{followup_id}/retry", response_model=FollowupTaskResponse)
async def retry_followup(
    followup_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> FollowupTaskResponse:
    """将失败的邮件跟进重新加入待处理队列。"""
    from fastapi import HTTPException
    from sqlalchemy import select

    result = await db.execute(
        select(FollowupTask).where(
            FollowupTask.id == followup_id,
            FollowupTask.user_id == current_user.id,
        )
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Follow-up task not found")
    if task.status != "failed":
        raise HTTPException(status_code=409, detail="Only failed follow-ups can be retried")
    task.status = "pending"
    task.due_at = datetime.utcnow()
    await db.flush()
    return task


@router.get("/stats", response_model=LeadGenerationStatsResponse)
async def get_lead_generation_stats(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """获取 AI 获客与跟进统计。"""
    from sqlalchemy import func, select

    from app.models.lead_generation import Lead, SalesCopy

    lead_count = await db.scalar(
        select(func.count()).select_from(Lead).where(Lead.user_id == current_user.id)
    )
    copy_count = await db.scalar(
        select(func.count())
        .select_from(SalesCopy)
        .join(Lead, SalesCopy.lead_id == Lead.id)
        .where(Lead.user_id == current_user.id)
    )
    followup_count = await db.scalar(
        select(func.count())
        .select_from(FollowupTask)
        .where(FollowupTask.user_id == current_user.id)
    )
    completed_followups = await db.scalar(
        select(func.count())
        .select_from(FollowupTask)
        .where(FollowupTask.user_id == current_user.id, FollowupTask.status == "completed")
    )
    contacted_count = await db.scalar(
        select(func.count())
        .select_from(Lead)
        .where(Lead.user_id == current_user.id, Lead.status == "contacted")
    )
    replied_count = await db.scalar(
        select(func.count())
        .select_from(Lead)
        .where(Lead.user_id == current_user.id, Lead.status == "replied")
    )
    contacted_total = (contacted_count or 0) + (replied_count or 0)

    async def grouped_counts(column, *conditions):
        result = await db.execute(
            select(column, func.count())
            .where(*conditions, column.is_not(None))
            .group_by(column)
            .order_by(func.count().desc())
        )
        return {str(key): count for key, count in result.all() if key}

    return {
        "leads": lead_count or 0,
        "sales_copies": copy_count or 0,
        "followups": followup_count or 0,
        "completed_followups": completed_followups or 0,
        "contacted": contacted_total,
        "replied": replied_count or 0,
        "reply_rate": (
            round((replied_count or 0) / contacted_total * 100, 2) if contacted_total else 0.0
        ),
        "channels": await grouped_counts(
            FollowupTask.channel,
            FollowupTask.user_id == current_user.id,
        ),
        "countries": await grouped_counts(
            Lead.country,
            Lead.user_id == current_user.id,
        ),
        "industries": await grouped_counts(
            Lead.industry,
            Lead.user_id == current_user.id,
        ),
        "statuses": await grouped_counts(
            Lead.status,
            Lead.user_id == current_user.id,
        ),
    }
