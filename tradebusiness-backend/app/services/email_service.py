"""
邮件服务
处理邮件发送、模板管理等业务逻辑
"""

import smtplib
import uuid
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Optional

from jinja2 import Template
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.exceptions import EmailServiceException, EmailTemplateNotFoundException
from app.models.email import Email, EmailDirection, EmailStatus, EmailTemplate
from app.repositories.base import BaseRepository


class EmailRepository(BaseRepository[Email]):
    """邮件 Repository"""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Email, session)

    async def get_by_customer(
        self,
        customer_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Email]:
        from sqlalchemy import select

        stmt = (
            select(Email)
            .where(Email.customer_id == customer_id)
            .order_by(Email.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_status(
        self,
        status: EmailStatus,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Email]:
        from sqlalchemy import select

        stmt = (
            select(Email)
            .where(Email.status == status)
            .order_by(Email.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class EmailTemplateRepository(BaseRepository[EmailTemplate]):
    """邮件模板 Repository"""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(EmailTemplate, session)

    async def get_by_name(self, name: str) -> Optional[EmailTemplate]:
        from sqlalchemy import select

        stmt = select(EmailTemplate).where(EmailTemplate.name == name)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_active_templates(
        self,
        category: Optional[str] = None,
    ) -> list[EmailTemplate]:
        from sqlalchemy import select

        stmt = select(EmailTemplate).where(EmailTemplate.is_active == True)

        if category:
            stmt = stmt.where(EmailTemplate.category == category)

        stmt = stmt.order_by(EmailTemplate.name)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class EmailService:
    """邮件业务逻辑类"""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.email_repo = EmailRepository(session)
        self.template_repo = EmailTemplateRepository(session)

    async def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        to_name: Optional[str] = None,
        from_name: Optional[str] = None,
        customer_id: Optional[uuid.UUID] = None,
        sender_id: Optional[uuid.UUID] = None,
        template_id: Optional[uuid.UUID] = None,
        template_name: Optional[str] = None,
    ) -> Email:
        """
        发送邮件

        Args:
            to_email: 收件人邮箱
            subject: 邮件主题
            body: 邮件内容(HTML)
            to_name: 收件人名称
            from_name: 发件人名称
            customer_id: 客户ID
            sender_id: 发送者用户ID
            template_id: 使用的模板ID
            template_name: 使用的模板名称

        Returns:
            邮件对象
        """
        # 创建邮件记录
        email = await self.email_repo.create(
            id=uuid.uuid4(),
            customer_id=customer_id,
            sender_id=sender_id,
            subject=subject,
            body=body,
            direction=EmailDirection.OUTGOING,
            status=EmailStatus.QUEUED,
            to_email=to_email,
            to_name=to_name,
            from_email=settings.SMTP_FROM,
            from_name=from_name or settings.SMTP_FROM_NAME,
            template_id=template_id,
            template_name=template_name,
        )

        # 异步发送邮件(实际应该在 Celery 任务中)
        try:
            await self._send_smtp_email(
                to_email=to_email,
                to_name=to_name,
                subject=subject,
                body=body,
            )

            # 更新状态为已发送
            email.status = EmailStatus.SENT
            email.sent_at = datetime.utcnow()
            await self.session.flush()

        except Exception as e:
            # 发送失败
            email.status = EmailStatus.FAILED
            email.error_message = str(e)
            await self.session.flush()
            raise EmailServiceException(f"Failed to send email: {str(e)}")

        return email

    async def send_email_with_template(
        self,
        template_name: str,
        to_email: str,
        variables: dict,
        to_name: Optional[str] = None,
        customer_id: Optional[uuid.UUID] = None,
        sender_id: Optional[uuid.UUID] = None,
    ) -> Email:
        """
        使用模板发送邮件

        Args:
            template_name: 模板名称
            to_email: 收件人邮箱
            variables: 模板变量
            to_name: 收件人名称
            customer_id: 客户ID
            sender_id: 发送者用户ID

        Returns:
            邮件对象
        """
        # 获取模板
        template = await self.template_repo.get_by_name(template_name)
        if not template:
            raise EmailTemplateNotFoundException(template_name)

        if not template.is_active:
            raise EmailServiceException(f"Template {template_name} is not active")

        # 渲染模板
        jinja_template = Template(template.subject)
        subject = jinja_template.render(**variables)

        jinja_template = Template(template.body)
        body = jinja_template.render(**variables)

        # 发送邮件
        return await self.send_email(
            to_email=to_email,
            subject=subject,
            body=body,
            to_name=to_name,
            customer_id=customer_id,
            sender_id=sender_id,
            template_id=template.id,
            template_name=template.name,
        )

    async def batch_send_emails(
        self,
        recipients: List[dict],
        subject: str,
        body: str,
        sender_id: uuid.UUID,
    ) -> dict[str, any]:
        """
        批量发送邮件

        Args:
            recipients: 收件人列表 [{"email": "...", "name": "...", "customer_id": "..."}, ...]
            subject: 邮件主题
            body: 邮件内容
            sender_id: 发送者用户ID

        Returns:
            发送结果统计
        """
        sent = 0
        failed = 0
        errors = []

        for recipient in recipients:
            try:
                await self.send_email(
                    to_email=recipient["email"],
                    to_name=recipient.get("name"),
                    subject=subject,
                    body=body,
                    customer_id=recipient.get("customer_id"),
                    sender_id=sender_id,
                )
                sent += 1
            except Exception as e:
                failed += 1
                errors.append(
                    {
                        "email": recipient["email"],
                        "error": str(e),
                    }
                )

        return {
            "total": len(recipients),
            "sent": sent,
            "failed": failed,
            "errors": errors,
        }

    async def create_template(
        self,
        name: str,
        subject: str,
        body: str,
        category: Optional[str] = None,
        language: str = "zh",
        variables: Optional[dict] = None,
        created_by: Optional[uuid.UUID] = None,
    ) -> EmailTemplate:
        """
        创建邮件模板

        Args:
            name: 模板名称(唯一)
            subject: 邮件主题(支持 Jinja2 模板)
            body: 邮件内容(支持 Jinja2 模板)
            category: 分类
            language: 语言
            variables: 可用变量说明
            created_by: 创建者用户ID

        Returns:
            创建的模板对象
        """
        # 检查名称是否已存在
        existing = await self.template_repo.get_by_name(name)
        if existing:
            raise EmailServiceException(f"Template with name '{name}' already exists")

        return await self.template_repo.create(
            id=uuid.uuid4(),
            name=name,
            subject=subject,
            body=body,
            category=category,
            language=language,
            variables=variables or {},
            is_active=True,
            created_by=created_by,
        )

    async def update_template(
        self,
        template_id: str,
        **kwargs,
    ) -> EmailTemplate:
        """
        更新邮件模板

        Args:
            template_id: 模板ID
            **kwargs: 要更新的字段

        Returns:
            更新后的模板对象
        """
        template = await self.template_repo.get_by_id(template_id)
        if not template:
            raise EmailTemplateNotFoundException(template_id)

        return await self.template_repo.update(template, **kwargs)

    async def delete_template(self, template_id: str) -> None:
        """
        删除邮件模板

        Args:
            template_id: 模板ID
        """
        template = await self.template_repo.get_by_id(template_id)
        if not template:
            raise EmailTemplateNotFoundException(template_id)

        await self.template_repo.delete(template)

    async def get_emails_by_customer(
        self,
        customer_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Email], int]:
        """
        获取客户的邮件列表

        Args:
            customer_id: 客户ID
            skip: 分页偏移
            limit: 分页大小

        Returns:
            (邮件列表, 总数)
        """
        emails = await self.email_repo.get_by_customer(customer_id, skip, limit)
        total = len(emails)  # 简化，实际应该用 count
        return emails, total

    async def get_email_statistics(self) -> dict[str, any]:
        """
        获取邮件统计信息

        Returns:
            统计数据
        """
        from sqlalchemy import func, select

        # 总数统计
        total_stmt = select(func.count(Email.id))
        total_result = await self.session.execute(total_stmt)
        total = total_result.scalar() or 0

        # 按状态统计
        status_stmt = select(Email.status, func.count(Email.id)).group_by(Email.status)
        status_result = await self.session.execute(status_stmt)
        by_status = {row.status: row.count for row in status_result.all()}

        # 今日发送统计
        from datetime import date, timedelta

        today = date.today()
        today_start = datetime.combine(today, datetime.min.time())

        today_stmt = select(func.count(Email.id)).where(
            Email.created_at >= today_start,
            Email.direction == EmailDirection.OUTGOING,
        )
        today_result = await self.session.execute(today_stmt)
        today_sent = today_result.scalar() or 0

        return {"total": total, "by_status": by_status, "today_sent": today_sent}

    async def _send_smtp_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        to_name: Optional[str] = None,
    ) -> None:
        """
        通过 SMTP 发送邮件

        Args:
            to_email: 收件人邮箱
            subject: 邮件主题
            body: 邮件内容(HTML)
            to_name: 收件人名称
        """
        # 创建邮件
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM}>"
        msg["To"] = f"{to_name or ''} <{to_email}>" if to_name else to_email

        # 添加 HTML 内容
        html_part = MIMEText(body, "html", "utf-8")
        msg.attach(html_part)

        # 根据端口选择连接方式
        # 465端口使用SSL，587端口使用STARTTLS
        if settings.SMTP_PORT == 465:
            # 使用SSL连接(适用于465端口)
            with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)
        else:
            # 使用STARTTLS(适用于587端口)
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)
