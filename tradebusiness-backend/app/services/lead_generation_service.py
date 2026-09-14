"""
AI 获客业务服务
负责获客任务、手动导入潜客和潜客管理。
"""

from urllib.parse import urlparse

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.audit import audit_event
from app.models.lead_generation import Lead, LeadContact, LeadSearchTask, LeadTaskStatus
from app.repositories.lead_generation_repo import (
    LeadContactRepository,
    LeadRepository,
    LeadSearchTaskRepository,
)


class LeadGenerationService:
    """AI 获客业务逻辑。"""

    def __init__(self, session: AsyncSession) -> None:
        self.task_repo = LeadSearchTaskRepository(session)
        self.lead_repo = LeadRepository(session)
        self.contact_repo = LeadContactRepository(session)

    async def create_task(self, user_id: str, data: dict) -> LeadSearchTask:
        """创建获客任务。"""
        task_data = data.copy()
        task_data["product_keywords"] = self._list_to_json_map(
            task_data.get("product_keywords", [])
        )
        task_data["exclude_keywords"] = self._list_to_json_map(
            task_data.get("exclude_keywords", [])
        )
        task_data["website_inputs"] = {
            "items": [
                self._normalize_url(url) for url in task_data.get("website_inputs", []) if url
            ]
        }
        return await self.task_repo.create(user_id=user_id, **task_data)

    async def list_tasks(
        self,
        user_id: str,
        skip: int,
        limit: int,
        status_filter: str | None = None,
    ) -> tuple[list[LeadSearchTask], int]:
        """分页查询获客任务。"""
        return await self.task_repo.list_by_user(user_id, skip, limit, status_filter)

    async def get_task(self, task_id: str, user_id: str) -> LeadSearchTask:
        """获取获客任务详情。"""
        task = await self.task_repo.get_owned(task_id, user_id)
        if not task:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        return task

    async def run_task(self, task_id: str, user_id: str) -> LeadSearchTask:
        """
        运行获客任务。

        第一阶段将官网输入转为潜客记录；真实搜索 API 后续接入。
        """
        task = await self.get_task(task_id, user_id)
        if task.status == LeadTaskStatus.CANCELLED.value:
            return task
        await self.task_repo.update(task, status=LeadTaskStatus.RUNNING.value, error_message=None)

        try:
            websites = (task.website_inputs or {}).get("items", [])
            created_count = 0
            for website in websites:
                current_status = await self.task_repo.session.scalar(
                    select(LeadSearchTask.status).where(LeadSearchTask.id == task.id)
                )
                if current_status == LeadTaskStatus.CANCELLED.value:
                    cancelled_task = await self.task_repo.get_owned(task_id, user_id)
                    return cancelled_task or task
                normalized_url = self._normalize_url(website)
                existing = await self.lead_repo.get_by_website(user_id, normalized_url, task.id)
                if existing:
                    continue

                company_name = self._guess_company_name(normalized_url)
                await self.lead_repo.create(
                    task_id=task.id,
                    user_id=user_id,
                    company_name=company_name,
                    website=normalized_url,
                    country=task.target_country,
                    industry=task.target_industry,
                    description=task.customer_profile,
                    source="manual_website",
                    match_score=60.0,
                )
                created_count += 1

            await self.task_repo.update(
                task,
                status=LeadTaskStatus.COMPLETED.value,
                total_found=created_count,
            )
        except Exception as exc:
            await self.task_repo.update(
                task,
                status=LeadTaskStatus.FAILED.value,
                error_message=str(exc),
            )
            raise

        return task

    async def cancel_task(self, task_id: str, user_id: str) -> LeadSearchTask:
        """取消尚未完成的获客任务。"""
        task = await self.get_task(task_id, user_id)
        if task.status not in {
            LeadTaskStatus.PENDING.value,
            LeadTaskStatus.RUNNING.value,
        }:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Only pending or running tasks can be cancelled",
            )
        return await self.task_repo.update(
            task,
            status=LeadTaskStatus.CANCELLED.value,
            error_message="Task cancelled by user",
        )

    async def create_lead(self, user_id: str, data: dict) -> Lead:
        """手动创建潜客。"""
        lead_data = data.copy()
        if lead_data.get("task_id"):
            await self.get_task(lead_data["task_id"], user_id)
        if lead_data.get("website"):
            lead_data["website"] = self._normalize_url(str(lead_data["website"]))
        return await self.lead_repo.create(user_id=user_id, **lead_data)

    async def list_leads(
        self,
        user_id: str,
        skip: int,
        limit: int,
        task_id: str | None = None,
        status_filter: str | None = None,
        search: str | None = None,
    ) -> tuple[list[Lead], int]:
        """分页查询潜客。"""
        return await self.lead_repo.list_by_user(
            user_id=user_id,
            skip=skip,
            limit=limit,
            task_id=task_id,
            status=status_filter,
            search=search,
        )

    async def get_lead(self, lead_id: str, user_id: str) -> Lead:
        """获取潜客详情。"""
        lead = await self.lead_repo.get_owned(lead_id, user_id)
        if not lead:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")
        return lead

    @staticmethod
    def ensure_lead_contactable(lead: Lead) -> None:
        """阻止无效潜客进入发送或跟进流程。"""
        if lead.status == "invalid":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Invalid leads cannot be contacted",
            )
        if getattr(lead, "do_not_contact", False):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This lead has opted out of contact",
            )

    async def update_lead(self, lead_id: str, user_id: str, data: dict) -> Lead:
        """更新潜客。"""
        lead = await self.get_lead(lead_id, user_id)
        update_data = data.copy()
        if update_data.get("website"):
            update_data["website"] = self._normalize_url(str(update_data["website"]))
        updated = await self.lead_repo.update(lead, **update_data)
        if "do_not_contact" in update_data:
            audit_event(
                "lead_contact_preference_changed",
                user_id=user_id,
                resource_type="lead",
                resource_id=str(lead.id),
                metadata={
                    "do_not_contact": bool(update_data["do_not_contact"]),
                    "reason": update_data.get("do_not_contact_reason"),
                },
            )
        return updated

    async def create_contact(
        self,
        lead_id: str,
        user_id: str,
        data: dict,
    ) -> LeadContact:
        """为潜客创建联系人。"""
        await self.get_lead(lead_id, user_id)
        contact_data = data.copy()
        contact_data["lead_id"] = lead_id
        return await self.contact_repo.create(**contact_data)

    async def list_contacts(self, lead_id: str, user_id: str) -> list[LeadContact]:
        """查询潜客联系人列表。"""
        await self.get_lead(lead_id, user_id)
        return await self.contact_repo.list_by_lead(lead_id)

    @staticmethod
    def _list_to_json_map(values: list[str]) -> dict:
        """将列表转为 JSON 对象，兼容 MySQL JSON 查询。"""
        return {"items": [value for value in values if value]}

    @staticmethod
    def _normalize_url(url: str) -> str:
        """标准化官网地址。"""
        clean_url = url.strip()
        if not clean_url:
            return clean_url
        if not clean_url.startswith(("http://", "https://")):
            clean_url = f"https://{clean_url}"
        return clean_url.rstrip("/")

    @staticmethod
    def _guess_company_name(website: str) -> str:
        """根据官网域名推断公司名称。"""
        parsed = urlparse(website)
        host = parsed.netloc or parsed.path
        parts = host.replace("www.", "").split(".")
        return parts[0].replace("-", " ").replace("_", " ").title() if parts else website
