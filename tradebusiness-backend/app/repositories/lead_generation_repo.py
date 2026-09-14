"""
AI 获客数据访问层
封装获客任务、潜客、联系人、背调报告和开发信的数据库操作。
"""

from typing import Optional

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.lead_generation import (
    CompanyResearchReport,
    Lead,
    LeadContact,
    LeadSearchTask,
    SalesCopy,
)
from app.repositories.base import BaseRepository


class LeadSearchTaskRepository(BaseRepository[LeadSearchTask]):
    """获客任务 Repository。"""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(LeadSearchTask, session)

    async def list_by_user(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 20,
        status: Optional[str] = None,
    ) -> tuple[list[LeadSearchTask], int]:
        """按用户分页查询获客任务。"""
        conditions = [LeadSearchTask.user_id == user_id]
        if status:
            conditions.append(LeadSearchTask.status == status)

        count_stmt = select(func.count()).select_from(LeadSearchTask).where(and_(*conditions))
        total = (await self.session.execute(count_stmt)).scalar() or 0

        stmt = (
            select(LeadSearchTask)
            .where(and_(*conditions))
            .order_by(LeadSearchTask.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all()), total

    async def get_owned(self, task_id: str, user_id: str) -> Optional[LeadSearchTask]:
        """获取当前用户拥有的获客任务。"""
        stmt = select(LeadSearchTask).where(
            LeadSearchTask.id == task_id,
            LeadSearchTask.user_id == user_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


class LeadRepository(BaseRepository[Lead]):
    """潜客 Repository。"""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Lead, session)

    async def list_by_user(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 20,
        task_id: Optional[str] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
    ) -> tuple[list[Lead], int]:
        """按用户分页查询潜客。"""
        conditions = [Lead.user_id == user_id]
        if task_id:
            conditions.append(Lead.task_id == task_id)
        if status:
            conditions.append(Lead.status == status)
        if search:
            pattern = f"%{search}%"
            conditions.append(
                or_(
                    Lead.company_name.ilike(pattern),
                    Lead.website.ilike(pattern),
                    Lead.country.ilike(pattern),
                    Lead.industry.ilike(pattern),
                )
            )

        count_stmt = select(func.count()).select_from(Lead).where(and_(*conditions))
        total = (await self.session.execute(count_stmt)).scalar() or 0

        stmt = (
            select(Lead)
            .where(and_(*conditions))
            .order_by(Lead.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all()), total

    async def get_owned(self, lead_id: str, user_id: str) -> Optional[Lead]:
        """获取当前用户拥有的潜客。"""
        stmt = select(Lead).where(Lead.id == lead_id, Lead.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_website(
        self,
        user_id: str,
        website: str,
        task_id: Optional[str] = None,
    ) -> Optional[Lead]:
        """按官网查询潜客，避免同一任务重复导入。"""
        conditions = [Lead.user_id == user_id, Lead.website == website]
        if task_id:
            conditions.append(Lead.task_id == task_id)
        stmt = select(Lead).where(and_(*conditions))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


class LeadContactRepository(BaseRepository[LeadContact]):
    """联系人 Repository。"""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(LeadContact, session)

    async def list_by_lead(self, lead_id: str) -> list[LeadContact]:
        """查询潜客联系人列表。"""
        stmt = (
            select(LeadContact)
            .where(LeadContact.lead_id == lead_id)
            .order_by(LeadContact.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class CompanyResearchReportRepository(BaseRepository[CompanyResearchReport]):
    """企业背调报告 Repository。"""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(CompanyResearchReport, session)

    async def get_latest_by_lead(self, lead_id: str) -> Optional[CompanyResearchReport]:
        """获取潜客最新背调报告。"""
        stmt = (
            select(CompanyResearchReport)
            .where(CompanyResearchReport.lead_id == lead_id)
            .order_by(CompanyResearchReport.created_at.desc())
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


class SalesCopyRepository(BaseRepository[SalesCopy]):
    """开发信 Repository。"""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(SalesCopy, session)

    async def list_by_lead(self, lead_id: str) -> list[SalesCopy]:
        """查询潜客开发信列表。"""
        stmt = (
            select(SalesCopy)
            .where(SalesCopy.lead_id == lead_id)
            .order_by(SalesCopy.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
