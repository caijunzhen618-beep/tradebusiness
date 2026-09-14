"""
采集线索服务
处理线索审核、导入、统计等业务逻辑
"""

from typing import Optional

from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppException
from app.core.logger import get_logger
from app.models.scraped_lead import ScrapedLead, ScrapedLeadStatus
from app.repositories.scraped_lead_repo import ScrapedLeadRepository
from app.schemas.scraped_lead import BulkApproveRequest, BulkImportRequest, DuplicateCheckResponse
from app.services.lead_importer import LeadImporter

logger = get_logger(__name__)


class ScrapedLeadNotFoundException(AppException):
    """采集线索不存在异常"""

    def __init__(self, lead_id: str) -> None:
        super().__init__(
            message=f"Scraped lead {lead_id} not found",
            code="SCRAPED_LEAD_NOT_FOUND",
            status_code=404,
        )


class InvalidScrapedLeadStatusException(AppException):
    """采集线索状态不允许执行当前操作"""

    def __init__(self, lead_id: str, current_status: str, action: str) -> None:
        super().__init__(
            message=f"Cannot {action} lead {lead_id} with status {current_status}",
            code="INVALID_SCRAPED_LEAD_STATUS",
            status_code=400,
        )


class ScrapedLeadService:
    """采集线索业务逻辑"""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = ScrapedLeadRepository(session)

    async def list_leads(
        self,
        skip: int = 0,
        limit: int = 20,
        status: Optional[str] = None,
        data_source: Optional[str] = None,
        country_code: Optional[str] = None,
        scraping_task_id: Optional[str] = None,
        include_stats: bool = False,
    ) -> dict[str, object]:
        """
        获取采集线索列表。

        Args:
            skip: 分页偏移
            limit: 分页大小
            status: 状态筛选
            data_source: 数据源筛选
            country_code: 国家代码筛选
            scraping_task_id: 采集任务 ID 筛选
            include_stats: 是否包含统计信息

        Returns:
            分页结果，按需包含统计信息。
        """
        leads, total = await self.repo.list_with_total(
            skip=skip,
            limit=limit,
            status=status,
            data_source=data_source,
            country_code=country_code,
            scraping_task_id=scraping_task_id,
        )
        result: dict[str, object] = {
            "items": [lead.to_dict() for lead in leads],
            "total": total,
            "skip": skip,
            "limit": limit,
        }
        if include_stats:
            result["stats"] = await self.get_statistics(include_country=False)
        return result

    async def get_statistics(self, include_country: bool = True) -> dict[str, object]:
        """
        获取采集线索统计信息。

        Args:
            include_country: 是否包含国家维度统计。

        Returns:
            统计信息。
        """
        stats = await self.repo.get_statistics()
        if not include_country:
            stats.pop("by_country", None)
        return stats

    async def get_lead(self, lead_id: str) -> ScrapedLead:
        """
        获取采集线索详情。

        Args:
            lead_id: 线索 ID。

        Returns:
            采集线索对象。

        Raises:
            ScrapedLeadNotFoundException: 线索不存在。
        """
        lead = await self.repo.get_by_id(lead_id)
        if not lead:
            raise ScrapedLeadNotFoundException(lead_id)
        return lead

    async def approve_lead(self, lead_id: str, reviewed_by: str) -> ScrapedLead:
        """
        审核通过线索。

        Args:
            lead_id: 线索 ID。
            reviewed_by: 审核人 ID。

        Returns:
            更新后的线索。
        """
        lead = await self.get_lead(lead_id)
        self._ensure_status(lead, ScrapedLeadStatus.PENDING, "approve")

        lead.status = ScrapedLeadStatus.APPROVED
        lead.reviewed_by = reviewed_by
        lead.reviewed_at = func.now()
        await self.session.flush()
        await self.session.refresh(lead)

        logger.info(f"Scraped lead {lead_id} approved by user {reviewed_by}")
        return lead

    async def reject_lead(
        self,
        lead_id: str,
        reviewed_by: str,
        reason: Optional[str] = None,
    ) -> ScrapedLead:
        """
        拒绝线索。

        Args:
            lead_id: 线索 ID。
            reviewed_by: 审核人 ID。
            reason: 拒绝原因。

        Returns:
            更新后的线索。
        """
        lead = await self.get_lead(lead_id)
        self._ensure_status(lead, ScrapedLeadStatus.PENDING, "reject")

        lead.status = ScrapedLeadStatus.REJECTED
        lead.reviewed_by = reviewed_by
        lead.reviewed_at = func.now()
        lead.rejection_reason = reason
        await self.session.flush()
        await self.session.refresh(lead)

        logger.info(f"Scraped lead {lead_id} rejected by user {reviewed_by}, reason: {reason}")
        return lead

    async def bulk_approve(
        self,
        request: BulkApproveRequest,
        reviewed_by: str,
    ) -> dict[str, object]:
        """
        批量审核线索。

        Args:
            request: 批量审核请求。
            reviewed_by: 审核人 ID。

        Returns:
            审核结果统计。
        """
        approved_count = 0
        rejected_count = 0
        errors: list[str] = []

        for lead_id in request.lead_ids:
            lead = await self.repo.get_by_id(lead_id)
            if not lead:
                errors.append(f"Lead {lead_id} not found")
                continue
            if lead.status != ScrapedLeadStatus.PENDING:
                errors.append(f"Lead {lead_id} is not in pending status")
                continue

            if request.approved:
                lead.status = ScrapedLeadStatus.APPROVED
                approved_count += 1
            else:
                lead.status = ScrapedLeadStatus.REJECTED
                lead.rejection_reason = request.rejection_reason
                rejected_count += 1
            lead.reviewed_by = reviewed_by
            lead.reviewed_at = func.now()

        await self.session.flush()
        logger.info(
            f"Bulk approve completed: approved={approved_count}, "
            f"rejected={rejected_count}, errors={len(errors)}"
        )
        return {
            "approved_count": approved_count,
            "rejected_count": rejected_count,
            "errors": errors,
        }

    async def import_leads(
        self,
        request: BulkImportRequest,
        imported_by: str,
    ) -> dict[str, object]:
        """
        批量导入已审核通过的线索到客户表。

        Args:
            request: 批量导入请求。
            imported_by: 导入操作人 ID。

        Returns:
            导入结果统计。
        """
        imported_count = 0
        duplicate_count = 0
        errors: list[str] = []

        for lead_id in request.lead_ids:
            try:
                lead = await self.repo.get_by_id(lead_id)
                if not lead:
                    errors.append(f"Lead {lead_id} not found")
                    continue
                if lead.status != ScrapedLeadStatus.APPROVED:
                    errors.append(f"Lead {lead_id} is not approved (current status: {lead.status})")
                    continue

                duplicate = await LeadImporter.check_duplicate(
                    self.session,
                    lead.company_name,
                    lead.email,
                )
                if duplicate:
                    duplicate_count += 1
                    lead.duplicate_of = str(duplicate.id)
                    lead.similarity_score = 70
                    continue

                customer = await LeadImporter.import_lead(self.session, lead.id, imported_by)
                if customer:
                    imported_count += 1
                    logger.info(f"Successfully imported lead {lead_id} as customer {customer.id}")
                else:
                    errors.append(f"Lead {lead_id} import returned None")
            except Exception as exc:
                errors.append(f"Error importing lead {lead_id}: {exc}")
                logger.error(f"Error importing lead {lead_id}: {exc}", exc_info=True)

        await self.session.flush()
        logger.info(
            f"Bulk import completed: imported={imported_count}, "
            f"duplicates={duplicate_count}, errors={len(errors)}"
        )
        return {
            "imported_count": imported_count,
            "duplicate_count": duplicate_count,
            "errors": errors,
        }

    async def check_duplicate(self, lead_id: str) -> DuplicateCheckResponse:
        """
        检查线索是否与现有客户重复。

        Args:
            lead_id: 线索 ID。

        Returns:
            重复检测结果。
        """
        lead = await self.get_lead(lead_id)
        duplicate = await LeadImporter.check_duplicate(
            self.session,
            lead.company_name,
            lead.email,
        )
        if duplicate:
            return DuplicateCheckResponse(
                is_duplicate=True,
                duplicate_lead_id=lead.id,
                similarity_score=70,
                existing_customer_id=str(duplicate.id),
            )
        return DuplicateCheckResponse(
            is_duplicate=False,
            duplicate_lead_id=None,
            similarity_score=None,
            existing_customer_id=None,
        )

    async def delete_lead(self, lead_id: str, deleted_by: str) -> None:
        """
        删除未导入的采集线索。

        Args:
            lead_id: 线索 ID。
            deleted_by: 删除操作人 ID。
        """
        lead = await self.get_lead(lead_id)
        if lead.status == ScrapedLeadStatus.IMPORTED:
            raise InvalidScrapedLeadStatusException(lead_id, lead.status, "delete")

        await self.repo.delete(lead)
        logger.info(f"Scraped lead {lead_id} deleted by user {deleted_by}")

    @staticmethod
    def _ensure_status(lead: ScrapedLead, expected_status: str, action: str) -> None:
        """
        校验线索状态是否允许执行当前动作。

        Args:
            lead: 采集线索。
            expected_status: 期望状态。
            action: 当前动作名称。
        """
        if lead.status != expected_status:
            raise InvalidScrapedLeadStatusException(lead.id, lead.status, action)
