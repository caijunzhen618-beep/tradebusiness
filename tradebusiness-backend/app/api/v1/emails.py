"""
邮件管理 API
包含邮件发送、查询、模板管理等接口
"""

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.email import EmailDirection, EmailStatus
from app.models.user import User
from app.schemas.common import MessageResponse, PaginatedResponse
from app.services.email_service import EmailService

router = APIRouter()


@router.get("", response_model=PaginatedResponse[dict])
async def get_emails(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(20, ge=1, le=100, description="返回的记录数"),
    status: Optional[EmailStatus] = Query(None, description="状态筛选"),
    direction: Optional[EmailDirection] = Query(None, description="方向筛选"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取邮件列表

    支持分页、筛选和排序。
    """
    email_service = EmailService(db)

    # 获取邮件列表（这里简化处理，实际应该在 EmailService 中实现完整的列表查询）
    from sqlalchemy import func, select

    from app.models.email import Email

    # 构建查询
    stmt = select(Email).where(Email.sender_id == current_user.id)

    if status:
        stmt = stmt.where(Email.status == status)
    if direction:
        stmt = stmt.where(Email.direction == direction)
    if search:
        stmt = stmt.where(Email.subject.contains(search))

    # 获取总数
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_result = await db.execute(count_stmt)
    total = total_result.scalar() or 0

    # 分页
    stmt = stmt.order_by(Email.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(stmt)
    emails = result.scalars().all()

    # 转换为字典格式
    items = []
    for email in emails:
        items.append(
            {
                "id": str(email.id),
                "subject": email.subject,
                "body": email.body,
                "to_email": email.to_email,
                "to_name": email.to_name,
                "from_email": email.from_email,
                "from_name": email.from_name,
                "status": email.status.value,
                "direction": email.direction.value,
                "template_id": str(email.template_id) if email.template_id else None,
                "template_name": email.template_name,
                "sent_at": email.sent_at.isoformat() if email.sent_at else None,
                "opened_at": email.opened_at.isoformat() if email.opened_at else None,
                "replied_at": email.replied_at.isoformat() if email.replied_at else None,
                "created_at": email.created_at.isoformat() if email.created_at else None,
            }
        )

    return {
        "items": items,
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.get("/stats", response_model=dict)
async def get_email_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取邮件统计信息
    """
    email_service = EmailService(db)
    stats = await email_service.get_email_statistics()

    # 转换为前端期望的格式
    return {
        "total": stats.get("total", 0),
        "sent": stats.get("by_status", {}).get("sent", 0),
        "opened": stats.get("by_status", {}).get("opened", 0),
        "replied": stats.get("by_status", {}).get("replied", 0),
        "failed": stats.get("by_status", {}).get("failed", 0),
        "opened_count": stats.get("by_status", {}).get("opened", 0),
        "clicked": 0,  # 需要添加点击跟踪
        "by_template": {},
        "open_rate": 0.0,
        "click_rate": 0.0,
        "reply_rate": 0.0,
    }


@router.post("/draft", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_email_draft(
    email_data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    保存邮件草稿
    """
    email_service = EmailService(db)
    from app.config import settings

    email = await email_service.email_repo.create(
        id=uuid.uuid4(),
        customer_id=uuid.UUID(email_data["customer_id"]) if email_data.get("customer_id") else None,
        sender_id=current_user.id,
        subject=email_data.get("subject") or "(无主题)",
        body=email_data.get("body") or "",
        direction=EmailDirection.OUTGOING,
        status=EmailStatus.DRAFT,
        to_email=email_data["to_email"],
        to_name=email_data.get("to_name"),
        from_email=settings.SMTP_FROM,
        from_name=settings.SMTP_FROM_NAME,
        template_id=uuid.UUID(email_data["template_id"]) if email_data.get("template_id") else None,
        attachments=email_data.get("attachments") or [],
    )
    return _serialize_email(email)


@router.post("/send", response_model=dict, status_code=status.HTTP_201_CREATED)
async def send_email(
    email_data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    发送邮件

    支持直接发送或使用模板发送。
    """
    email_service = EmailService(db)

    try:
        # 如果使用模板
        if email_data.get("template_id"):
            template = await email_service.template_repo.get_by_id(email_data["template_id"])
            if not template:
                raise HTTPException(status_code=404, detail="Template not found")

            # 渲染模板
            from jinja2 import Template

            variables = email_data.get("template_variables", {})

            jinja_template = Template(template.subject)
            subject = jinja_template.render(**variables)

            jinja_template = Template(template.body)
            body = jinja_template.render(**variables)

            email = await email_service.send_email(
                to_email=email_data["to_email"],
                to_name=email_data.get("to_name"),
                subject=subject,
                body=body,
                customer_id=(
                    uuid.UUID(email_data["customer_id"]) if email_data.get("customer_id") else None
                ),
                sender_id=current_user.id,
                template_id=template.id,
                template_name=template.name,
            )
        else:
            # 直接发送
            email = await email_service.send_email(
                to_email=email_data["to_email"],
                to_name=email_data.get("to_name"),
                subject=email_data["subject"],
                body=email_data["body"],
                customer_id=(
                    uuid.UUID(email_data["customer_id"]) if email_data.get("customer_id") else None
                ),
                sender_id=current_user.id,
            )

        return {
            "id": str(email.id),
            "subject": email.subject,
            "status": email.status.value,
            "message": "Email queued successfully",
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/templates", response_model=list[dict])
async def get_email_templates(
    language: str = Query("zh", description="语言"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取邮件模板列表
    """
    email_service = EmailService(db)
    templates = await email_service.template_repo.get_active_templates()

    result = []
    for template in templates:
        result.append(
            {
                "id": str(template.id),
                "name": template.name,
                "subject": template.subject,
                "body": template.body,
                "category": template.category,
                "language": template.language,
                "variables": template.variables or {},
                "is_active": template.is_active,
            }
        )

    return result


@router.get("/templates/{template_id}", response_model=dict)
async def get_email_template(
    template_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取邮件模板详情
    """
    email_service = EmailService(db)
    template = await email_service.template_repo.get_by_id(template_id)

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    return _serialize_template(template)


@router.post("/templates", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_email_template(
    template_data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    创建邮件模板
    """
    email_service = EmailService(db)
    template = await email_service.create_template(
        name=template_data["name"],
        subject=template_data["subject"],
        body=template_data["body"],
        category=template_data.get("category"),
        language=template_data.get("language") or "zh",
        variables=template_data.get("variables") or {},
        created_by=current_user.id,
    )

    return _serialize_template(template)


@router.put("/templates/{template_id}", response_model=dict)
async def update_email_template(
    template_id: str,
    template_data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    更新邮件模板
    """
    allowed_fields = {
        "name",
        "subject",
        "body",
        "category",
        "language",
        "variables",
        "is_active",
    }
    update_data = {key: value for key, value in template_data.items() if key in allowed_fields}

    email_service = EmailService(db)
    template = await email_service.update_template(template_id, **update_data)

    return _serialize_template(template)


@router.delete("/templates/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_email_template(
    template_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    删除邮件模板
    """
    email_service = EmailService(db)
    await email_service.delete_template(template_id)


@router.post("/templates/{template_id}/preview", response_model=dict)
async def preview_email_template(
    template_id: str,
    variables: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    预览邮件模板渲染效果
    """
    email_service = EmailService(db)
    template = await email_service.template_repo.get_by_id(template_id)

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    from jinja2 import Template

    jinja_template = Template(template.subject)
    subject = jinja_template.render(**variables)

    jinja_template = Template(template.body)
    body = jinja_template.render(**variables)

    return {
        "subject": subject,
        "body": body,
    }


@router.get("/{email_id}", response_model=dict)
async def get_email(
    email_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取邮件详情
    """
    email_service = EmailService(db)
    email = await email_service.email_repo.get_by_id(email_id)
    if not email or str(email.sender_id) != str(current_user.id):
        raise HTTPException(status_code=404, detail="Email not found")

    return _serialize_email(email)


@router.post("/{email_id}/resend", response_model=dict)
async def resend_email(
    email_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    重新发送失败邮件
    """
    email_service = EmailService(db)
    email = await email_service.email_repo.get_by_id(email_id)
    if not email or str(email.sender_id) != str(current_user.id):
        raise HTTPException(status_code=404, detail="Email not found")
    if email.status != EmailStatus.FAILED:
        raise HTTPException(status_code=400, detail="Only failed emails can be resent")

    resent_email = await email_service.send_email(
        to_email=email.to_email,
        to_name=email.to_name,
        subject=email.subject,
        body=email.body,
        customer_id=uuid.UUID(str(email.customer_id)) if email.customer_id else None,
        sender_id=current_user.id,
        template_id=uuid.UUID(str(email.template_id)) if email.template_id else None,
        template_name=email.template_name,
    )
    return _serialize_email(resent_email)


@router.delete("/{email_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_email(
    email_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    删除邮件记录
    """
    email_service = EmailService(db)
    email = await email_service.email_repo.get_by_id(email_id)
    if not email or str(email.sender_id) != str(current_user.id):
        raise HTTPException(status_code=404, detail="Email not found")

    await email_service.email_repo.delete(email)


def _serialize_template(template) -> dict:
    """将邮件模板模型转换为前端响应字典。"""
    return {
        "id": str(template.id),
        "name": template.name,
        "subject": template.subject,
        "body": template.body,
        "category": template.category,
        "language": template.language,
        "variables": template.variables or {},
        "is_active": template.is_active,
        "created_by": str(template.created_by) if template.created_by else None,
        "created_at": template.created_at.isoformat() if template.created_at else None,
        "updated_at": template.updated_at.isoformat() if template.updated_at else None,
    }


def _serialize_email(email) -> dict:
    """将邮件模型转换为前端响应字典。"""
    return {
        "id": str(email.id),
        "customer_id": str(email.customer_id) if email.customer_id else None,
        "sender_id": str(email.sender_id) if email.sender_id else None,
        "subject": email.subject,
        "body": email.body,
        "direction": (
            email.direction.value if hasattr(email.direction, "value") else email.direction
        ),
        "status": email.status.value if hasattr(email.status, "value") else email.status,
        "to_email": email.to_email,
        "to_name": email.to_name,
        "from_email": email.from_email,
        "from_name": email.from_name,
        "template_id": str(email.template_id) if email.template_id else None,
        "template_name": email.template_name,
        "sent_at": email.sent_at.isoformat() if email.sent_at else None,
        "opened_at": email.opened_at.isoformat() if email.opened_at else None,
        "clicked_at": email.clicked_at.isoformat() if email.clicked_at else None,
        "replied_at": email.replied_at.isoformat() if email.replied_at else None,
        "error_message": email.error_message,
        "message_id": email.message_id,
        "thread_id": email.thread_id,
        "attachments": email.attachments or [],
        "created_at": email.created_at.isoformat() if email.created_at else None,
        "updated_at": email.updated_at.isoformat() if email.updated_at else None,
    }


@router.post("/{email_id}/retry", response_model=dict)
async def retry_email(
    email_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """重试发送失败邮件。"""
    from fastapi import HTTPException
    from sqlalchemy import select

    from app.models.email import Email

    result = await db.execute(
        select(Email).where(Email.id == email_id, Email.sender_id == current_user.id)
    )
    email = result.scalar_one_or_none()
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    if email.status not in {EmailStatus.FAILED, EmailStatus.DRAFT}:
        raise HTTPException(status_code=400, detail="Only failed or draft emails can be retried")
    sent = await EmailService(db).send_email(
        to_email=email.to_email,
        subject=email.subject,
        body=email.body,
        to_name=email.to_name,
        sender_id=current_user.id,
        template_name=email.template_name,
    )
    return {"id": str(sent.id), "status": sent.status.value}
