"""
开发信生成服务
负责基于潜客和企业背调生成渠道话术。
"""

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.lead_generation import LeadStatus, SalesCopy
from app.repositories.lead_generation_repo import (
    CompanyResearchReportRepository,
    LeadRepository,
    SalesCopyRepository,
)
from app.repositories.sales_agent_repo import PromptTemplateRepository, SalesAgentRepository
from app.services.ai_provider_service import AIProviderService
from app.services.credit_service import CreditService


class SalesCopyService:
    """开发信业务逻辑。"""

    def __init__(self, session: AsyncSession) -> None:
        self.lead_repo = LeadRepository(session)
        self.report_repo = CompanyResearchReportRepository(session)
        self.copy_repo = SalesCopyRepository(session)
        self.ai_provider = AIProviderService()
        self.agent_repo = SalesAgentRepository(session)

    async def generate_sales_copy(
        self,
        lead_id: str,
        user_id: str,
        channel: str,
        language: str,
        tone: str | None,
        agent_id: str | None = None,
        template_id: str | None = None,
    ) -> SalesCopy:
        """生成并保存开发信。"""
        lead = await self.lead_repo.get_owned(lead_id, user_id)
        if not lead:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")

        await CreditService(self.lead_repo.session).debit(
            user_id, 2, "sales_copy", f"开发信生成：{lead.company_name}"
        )
        report = await self.report_repo.get_latest_by_lead(lead_id)
        agent = await self.agent_repo.get_owned(agent_id, user_id) if agent_id else None
        knowledge_context = (
            await self.agent_repo.get_context_text(
                agent.id, [lead.company_name, lead.country or "", lead.industry or ""]
            )
            if agent
            else ""
        )
        template = (
            await PromptTemplateRepository(self.copy_repo.session).get_owned(template_id, agent.id)
            if template_id and agent
            else None
        )
        copy_data = await self.ai_provider.generate_sales_copy(
            lead=lead,
            channel=channel,
            language=language,
            tone=tone,
            research_summary=report.summary if report else None,
            agent_context=agent.to_dict() if agent else None,
            knowledge_context=knowledge_context,
            template_context=template.prompt_text if template else "",
        )
        sales_copy = await self.copy_repo.create(
            lead_id=lead.id,
            channel=channel,
            language=language,
            **copy_data,
        )
        await self.lead_repo.update(lead, status=LeadStatus.COPY_GENERATED.value)
        return sales_copy

    async def list_sales_copies(self, lead_id: str, user_id: str) -> list[SalesCopy]:
        """查询潜客所有开发信。"""
        lead = await self.lead_repo.get_owned(lead_id, user_id)
        if not lead:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")
        return await self.copy_repo.list_by_lead(lead_id)
