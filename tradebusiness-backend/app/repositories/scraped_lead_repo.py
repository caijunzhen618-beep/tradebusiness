"""
采集线索数据访问层
处理 scraped_leads 表的查询与状态更新
"""

from typing import Optional

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.scraped_lead import ScrapedLead
from app.repositories.base import BaseRepository


class ScrapedLeadRepository(BaseRepository[ScrapedLead]):
    """采集线索 Repository"""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(ScrapedLead, session)

    @staticmethod
    def build_filters(
        status: Optional[str] = None,
        data_source: Optional[str] = None,
        country_code: Optional[str] = None,
        scraping_task_id: Optional[str] = None,
    ) -> list[object]:
        """
        构建线索查询条件。

        Args:
            status: 状态筛选
            data_source: 数据源筛选
            country_code: 国家代码筛选
            scraping_task_id: 采集任务 ID 筛选

        Returns:
            SQLAlchemy 查询条件列表。
        """
        filters: list[object] = []
        if status:
            filters.append(ScrapedLead.status == status)
        if data_source:
            filters.append(ScrapedLead.data_source == data_source)
        if country_code:
            filters.append(ScrapedLead.country_code == country_code)
        if scraping_task_id:
            filters.append(ScrapedLead.scraping_task_id == scraping_task_id)
        return filters

    async def list_with_total(
        self,
        skip: int = 0,
        limit: int = 20,
        status: Optional[str] = None,
        data_source: Optional[str] = None,
        country_code: Optional[str] = None,
        scraping_task_id: Optional[str] = None,
    ) -> tuple[list[ScrapedLead], int]:
        """
        获取采集线索分页列表和总数。

        Args:
            skip: 分页偏移
            limit: 分页大小
            status: 状态筛选
            data_source: 数据源筛选
            country_code: 国家代码筛选
            scraping_task_id: 采集任务 ID 筛选

        Returns:
            线索列表和总数。
        """
        filters = self.build_filters(status, data_source, country_code, scraping_task_id)

        count_stmt = select(func.count(ScrapedLead.id))
        list_stmt = select(ScrapedLead).order_by(ScrapedLead.created_at.desc())
        if filters:
            where_clause = and_(*filters)
            count_stmt = count_stmt.where(where_clause)
            list_stmt = list_stmt.where(where_clause)

        total_result = await self.session.execute(count_stmt)
        total = total_result.scalar() or 0

        result = await self.session.execute(list_stmt.offset(skip).limit(limit))
        return list(result.scalars().all()), total

    async def get_statistics(self) -> dict[str, object]:
        """
        获取采集线索统计信息。

        Returns:
            按状态、数据源、国家等维度聚合后的统计信息。
        """
        status_stats = await self._count_by_field(ScrapedLead.status)
        source_stats = await self._count_by_field(ScrapedLead.data_source)

        country_stmt = (
            select(ScrapedLead.country, func.count(ScrapedLead.id).label("count"))
            .group_by(ScrapedLead.country)
            .order_by(func.count(ScrapedLead.id).desc())
            .limit(10)
        )
        country_result = await self.session.execute(country_stmt)
        country_stats = {row.country: row.count for row in country_result}

        total_result = await self.session.execute(select(func.count(ScrapedLead.id)))
        total_count = total_result.scalar() or 0

        today_result = await self.session.execute(
            select(func.count(ScrapedLead.id)).where(
                func.date(ScrapedLead.created_at) == func.current_date()
            )
        )
        today_count = today_result.scalar() or 0

        avg_result = await self.session.execute(select(func.avg(ScrapedLead.confidence_score)))
        avg_confidence = avg_result.scalar() or 0

        return {
            "total": total_count,
            "today": today_count,
            "by_status": {
                "pending": status_stats.get("pending", 0),
                "approved": status_stats.get("approved", 0),
                "rejected": status_stats.get("rejected", 0),
                "imported": status_stats.get("imported", 0),
            },
            "by_source": source_stats,
            "by_country": country_stats,
            "avg_confidence": round(float(avg_confidence), 2),
        }

    async def _count_by_field(self, field: object) -> dict[str, int]:
        """
        按指定字段统计线索数量。

        Args:
            field: SQLAlchemy 模型字段。

        Returns:
            字段值到数量的映射。
        """
        stmt = select(field, func.count(ScrapedLead.id).label("count")).group_by(field)
        result = await self.session.execute(stmt)
        return {row[0]: row.count for row in result}
