"""
Celery 任务模块
包含所有异步任务的定义
"""

import asyncio
import uuid
from datetime import date, datetime, timedelta
from typing import List, Optional

from celery import Celery
from celery.schedules import crontab
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.logger import get_logger
from app.db.session import async_session_maker, engine
from app.models.customer import Customer
from app.models.email import EmailTemplate
from app.models.holiday import Holiday
from app.models.lead_generation import FollowupTask, Lead, LeadContact
from app.services.email_service import EmailService

logger = get_logger(__name__)

# 创建 Celery 应用
celery_app = Celery(
    "tradebusiness",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

# Celery 配置
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 分钟
    task_soft_time_limit=25 * 60,  # 25 分钟
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)


@celery_app.task(name="run-lead-search")
def run_lead_search_task(task_id: str, user_id: str) -> dict:
    """异步执行 AI 获客任务。"""

    async def _run() -> dict:
        from app.services.lead_generation_service import LeadGenerationService

        async with get_db_session() as session:
            task = await LeadGenerationService(session).run_task(task_id, user_id)
            await session.commit()
            return {
                "task_id": str(task.id),
                "status": task.status,
                "total_found": task.total_found,
            }

    return run_async_task(_run)


# 定时任务配置
celery_app.conf.beat_schedule = {
    # 每天凌晨检查并发送节假日问候
    "send-holiday-greetings": {
        "task": "send-holiday-greetings",
        "schedule": crontab(hour=0, minute=0),  # 每天凌晨
    },
    # 每小时检查并发送跟进提醒
    "send-followup-reminders": {
        "task": "send-followup-reminders",
        "schedule": crontab(minute=0),  # 每小时
    },
    "send-due-lead-followups": {
        "task": "send-due-lead-followups",
        "schedule": crontab(minute="*/5"),
    },
    # 每天凌晨清理过期任务
    "cleanup-old-tasks": {
        "task": "cleanup-old-notifications",
        "schedule": crontab(hour=1, minute=0),  # 每天凌晨1点
    },
}


@celery_app.task(name="send-due-lead-followups")
def send_due_lead_followups_task() -> dict:
    """发送已到期的潜客邮件跟进任务。"""

    async def _send_due() -> dict:
        from sqlalchemy import select

        sent = 0
        failed = 0
        async with get_db_session() as session:
            result = await session.execute(
                select(FollowupTask)
                .where(
                    FollowupTask.status == "pending",
                    FollowupTask.due_at <= datetime.utcnow(),
                    FollowupTask.channel == "email",
                )
                .order_by(FollowupTask.due_at.asc())
                .limit(100)
            )
            for followup in result.scalars().all():
                contact_result = await session.execute(
                    select(LeadContact)
                    .join(Lead, Lead.id == LeadContact.lead_id)
                    .where(
                        Lead.id == followup.lead_id,
                        Lead.user_id == followup.user_id,
                        Lead.status != "invalid",
                        Lead.do_not_contact.is_(False),
                        LeadContact.email.is_not(None),
                    )
                    .order_by(LeadContact.is_verified.desc())
                    .limit(1)
                )
                contact = contact_result.scalar_one_or_none()
                if not contact or not contact.email:
                    followup.status = "failed"
                    failed += 1
                    continue
                try:
                    await EmailService(session).send_email(
                        to_email=contact.email,
                        to_name=contact.name,
                        subject=followup.subject or "Following up on our conversation",
                        body=followup.content,
                        sender_id=followup.user_id,
                    )
                    followup.status = "completed"
                    sent += 1
                except Exception as exc:  # noqa: BLE001
                    logger.error("Lead follow-up %s failed: %s", followup.id, exc)
                    followup.status = "failed"
                    failed += 1
            await session.commit()
        return {"sent": sent, "failed": failed}

    return run_async_task(_send_due)


def get_db_session() -> AsyncSession:
    """获取数据库会话"""
    return async_session_maker()


def run_async_task(task_factory):
    """在 Celery 的新事件循环中运行任务并隔离 aiomysql 连接池。"""

    async def _run() -> object:
        await engine.dispose()
        try:
            return await task_factory()
        finally:
            await engine.dispose()

    return asyncio.run(_run())


@celery_app.task(name="send-email")
def send_email_task(
    to_email: str,
    subject: str,
    body: str,
    customer_id: Optional[str] = None,
    sender_id: Optional[str] = None,
):
    """
    异步发送邮件任务

    Args:
        to_email: 收件人邮箱
        subject: 邮件主题
        body: 邮件内容
        customer_id: 客户ID
        sender_id: 发送者ID
    """
    import asyncio

    async def _send():
        async with get_db_session() as session:
            email_service = EmailService(session)
            await email_service.send_email(
                to_email=to_email,
                subject=subject,
                body=body,
                customer_id=uuid.UUID(customer_id) if customer_id else None,
                sender_id=uuid.UUID(sender_id) if sender_id else None,
            )
            logger.info(f"Email sent to {to_email}")

    run_async_task(_send)


@celery_app.task(name="send-bulk-emails")
def send_bulk_emails_task(
    recipients: List[dict],
    subject: str,
    body: str,
    sender_id: str,
):
    """
    异步批量发送邮件任务

    Args:
        recipients: 收件人列表
        subject: 邮件主题
        body: 邮件内容
        sender_id: 发送者ID
    """
    import asyncio

    async def _send_bulk():
        async with get_db_session() as session:
            email_service = EmailService(session)
            result = await email_service.batch_send_emails(
                recipients=recipients,
                subject=subject,
                body=body,
                sender_id=uuid.UUID(sender_id),
            )
            logger.info(f"Bulk email sent: {result}")
            return result

    return run_async_task(_send_bulk)


@celery_app.task(name="scrape-customers")
def scrape_customers_task(
    scraper_type: str,
    config: dict,
):
    """
    异步数据采集任务

    Args:
        scraper_type: 爬虫类型
        config: 爬虫配置
    """
    import asyncio

    async def _scrape():
        from app.scrapers import GoogleSearchScraper

        scraper_config = {
            "timeout": 30,
            "delay_min": 1,
            "delay_max": 3,
        }
        scraper_config.update(config)

        async with GoogleSearchScraper(scraper_config) as scraper:
            results = await scraper.scrape(**config)
            logger.info(f"Scraped {len(results)} customers using {scraper_type}")
            return results

    return run_async_task(_scrape)


@celery_app.task(name="send-automated-followup")
def send_automated_followup_task(
    customer_id: str,
    template_name: str,
    variables: dict,
    sender_id: str,
):
    """
    自动跟进任务

    Args:
        customer_id: 客户ID
        template_name: 邮件模板名称
        variables: 模板变量
        sender_id: 发送者ID
    """
    import asyncio

    async def _send_followup():
        async with get_db_session() as session:
            email_service = EmailService(session)

            # 获取客户信息
            from app.repositories.customer_repo import CustomerRepository

            customer_repo = CustomerRepository(session)
            customer = await customer_repo.get_by_id(customer_id)

            if not customer:
                logger.error(f"Customer {customer_id} not found")
                return

            # 发送邮件
            await email_service.send_email_with_template(
                template_name=template_name,
                to_email=customer.email,
                variables=variables,
                to_name=customer.company_name,
                customer_id=customer.id,
                sender_id=uuid.UUID(sender_id),
            )

            logger.info(f"Automated followup sent to {customer.company_name}")

    run_async_task(_send_followup)


# 自动化任务
@celery_app.task(name="send-holiday-greetings")
def send_holiday_greetings():
    """
    节假日自动问候任务

    每天检查并在节假日当天发送问候邮件
    """
    import asyncio

    async def _send_greetings():
        async with get_db_session() as session:
            email_service = EmailService(session)
            from sqlalchemy import select

            from app.models.customer import Customer

            # 获取今天的节假日
            today = date.today()

            # 查询今天是否是节假日
            # 这里简化处理，实际应该从 holiday 表查询
            holiday_countries = _get_holiday_countries(today)

            if not holiday_countries:
                logger.info("No holidays today")
                return

            # 为每个国家获取客户并发送问候
            for country in holiday_countries:
                # 获取该国的客户
                stmt = select(Customer).where(
                    Customer.country == country,
                    Customer.status == "cooperating",  # 只给合作客户发送
                )
                result = await session.execute(stmt)
                customers = result.scalars().all()

                # 发送问候邮件
                for customer in customers:
                    if customer.email:
                        try:
                            await email_service.send_email_with_template(
                                template_name="holiday_greeting",
                                to_email=customer.email,
                                variables={
                                    "company_name": customer.company_name,
                                    "contact_name": customer.company_name,
                                    "holiday": f"{country} 节",
                                },
                                to_name=customer.company_name,
                                customer_id=customer.id,
                            )
                            logger.info(f"Holiday greeting sent to {customer.company_name}")
                        except Exception as e:
                            logger.error(f"Failed to send holiday greeting: {str(e)}")

    run_async_task(_send_greetings)


def _get_holiday_countries(today: date) -> List[str]:
    """
    获取今天过节的国家列表

    Args:
        today: 今天日期

    Returns:
        国家列表
    """
    # 简化版本，实际应该从数据库查询
    # 这里列举一些主要节假日
    holidays = {
        (1, 1): ["Nigeria", "South Africa", "Kenya", "Ghana"],  # 新年
        (5, 1): ["Nigeria", "Ghana", "Kenya"],  # 劳动节
        (12, 25): ["Nigeria", "South Africa", "Egypt", "Kenya"],  # 圣诞节
        # 可以添加更多节假日
    }

    return holidays.get((today.month, today.day), [])


@celery_app.task(name="send-followup-reminders")
def send_followup_reminders():
    """
    发送跟进提醒任务

    每小时检查需要跟进的客户并发送提醒
    """
    import asyncio

    async def _send_reminders():
        async with get_db_session() as session:
            from sqlalchemy import select

            from app.core.notifications import notify_task_reminder
            from app.repositories.customer_repo import CustomerRepository

            customer_repo = CustomerRepository(session)

            # 查找3天内没有联系的合作客户
            three_days_ago = datetime.utcnow() - timedelta(days=3)

            stmt = select(Customer).where(
                Customer.status == "cooperating",
                Customer.updated_at < three_days_ago,
            )
            result = await session.execute(stmt)
            customers = result.scalars().all()

            for customer in customers:
                if customer.assigned_to:
                    # 发送提醒给业务员
                    await notify_task_reminder(
                        user_id=str(customer.assigned_to),
                        task_data={
                            "type": "followup",
                            "customer_id": str(customer.id),
                            "company_name": customer.company_name,
                            "days_since_contact": (datetime.utcnow() - customer.updated_at).days,
                        },
                    )

    run_async_task(_send_reminders)


# 清理任务
@celery_app.task(name="cleanup-old-notifications")
def cleanup_old_notifications():
    """
    清理旧的通知记录
    """
    import asyncio

    async def _cleanup():
        async with get_db_session() as session:
            # 删除30天前的通知记录
            from sqlalchemy import delete

            from app.models.notification import Notification

            thirty_days_ago = datetime.utcnow() - timedelta(days=30)

            stmt = delete(Notification).where(Notification.created_at < thirty_days_ago)
            await session.execute(stmt)
            await session.commit()

            logger.info("Old notifications cleaned up")

    run_async_task(_cleanup)
