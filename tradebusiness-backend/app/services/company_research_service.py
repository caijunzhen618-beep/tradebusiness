"""
企业背调服务
负责基于潜客资料生成和保存企业背调报告。
"""

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.lead_generation import CompanyResearchReport, LeadStatus
from app.repositories.lead_generation_repo import CompanyResearchReportRepository, LeadRepository
from app.services.ai_provider_service import AIProviderService
from app.services.credit_service import CreditService
from app.services.website_crawler_service import WebsiteCrawlerService


class CompanyResearchService:
    """企业背调业务逻辑。"""

    def __init__(self, session: AsyncSession) -> None:
        self.lead_repo = LeadRepository(session)
        self.report_repo = CompanyResearchReportRepository(session)
        self.ai_provider = AIProviderService()
        self.crawler = WebsiteCrawlerService()

    async def generate_report(self, lead_id: str, user_id: str) -> CompanyResearchReport:
        """为潜客生成企业背调报告。"""
        lead = await self.lead_repo.get_owned(lead_id, user_id)
        if not lead:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")

        # 生成接口可能因用户重复点击或网络重试被调用多次。
        # 已有报告时直接复用，避免重复扣费和产生重复报告。
        existing_report = await self.report_repo.get_latest_by_lead(lead_id)
        if existing_report:
            return existing_report

        await CreditService(self.lead_repo.session).debit(
            user_id, 5, "company_research", f"企业背调：{lead.company_name}"
        )
        website_text = await self.crawler.fetch_homepage_text(lead.website)
        report_data = await self.ai_provider.generate_company_research(lead, website_text)
        report = await self.report_repo.create(lead_id=lead.id, **report_data)
        await self.lead_repo.update(lead, status=LeadStatus.RESEARCHED.value)
        return report

    async def get_latest_report(
        self,
        lead_id: str,
        user_id: str,
    ) -> CompanyResearchReport | None:
        """获取潜客最新企业背调报告。"""
        lead = await self.lead_repo.get_owned(lead_id, user_id)
        if not lead:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")
        return await self.report_repo.get_latest_by_lead(lead_id)
