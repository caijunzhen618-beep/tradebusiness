"""
数据导入服务
将审核通过的采集数据导入到customers表
"""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger import get_logger
from app.models.customer import Customer
from app.models.scraped_lead import ScrapedLead

logger = get_logger(__name__)


class LeadImporter:
    """
    线索导入服务
    将scraped_leads表的数据导入到customers表
    """

    @staticmethod
    async def check_duplicate(
        session: AsyncSession, company_name: str, email: Optional[str] = None
    ) -> Optional[Customer]:
        """
        检查是否已存在重复客户

        Args:
            session: 数据库会话
            company_name: 公司名称
            email: 邮箱

        Returns:
            如果存在重复，返回该客户；否则返回None
        """
        conditions = [Customer.company_name == company_name]

        if email:
            conditions.append(Customer.email == email)

        result = await session.execute(select(Customer).where(and_(*conditions)))
        return result.scalar_one_or_none()

    @staticmethod
    def map_to_customer(lead: ScrapedLead, created_by: str) -> Dict[str, Any]:
        """
        将ScrapedLead映射为Customer数据

        Args:
            lead: 采集线索对象
            created_by: 创建者ID

        Returns:
            Customer数据字典
        """
        return {
            "id": str(uuid.uuid4()),
            "company_name": lead.company_name,
            "company_name_en": lead.company_name_en,
            "logo_url": None,
            "website": lead.website,
            # 地理位置
            "country_code": lead.country_code,
            "country": lead.country,
            "city": lead.city,
            "address": None,
            # 联系方式
            "phone": lead.phone,
            "email": lead.email,
            "whatsapp": lead.whatsapp,
            # 社交媒体
            "linkedin_url": None,
            "facebook_url": None,
            # 客户管理
            "status": "potential",  # 新导入的客户默认为潜在客户
            "assigned_to": None,  # 导入的数据暂不分配，由管理员后续分配
            "priority": 3,  # 默认中等优先级
            "source": f"数据采集: {lead.data_source}",
            "source_url": lead.source_url,
            "data_confidence": lead.confidence_score,
            # 标签和备注
            "tags": {tag: True for tag in ["scraped", lead.data_source]},
            "notes": f"通过数据采集导入\n来源: {lead.data_source}\n采集时间: {lead.created_at}\n任务ID: {lead.scraping_task_id}",
        }

    @staticmethod
    async def import_lead(
        session: AsyncSession, lead_id: str, imported_by: str
    ) -> Optional[Customer]:
        """
        导入单个线索到customers表

        Args:
            session: 数据库会话
            lead_id: 线索ID
            imported_by: 导入操作人ID

        Returns:
            导入的Customer对象，失败返回None
        """
        # 获取线索
        result = await session.execute(select(ScrapedLead).where(ScrapedLead.id == lead_id))
        lead = result.scalar_one_or_none()

        if not lead:
            logger.error(f"Lead {lead_id} not found")
            return None

        # Debug logging
        logger.info(f"Processing lead {lead_id}: status={lead.status}, company={lead.company_name}")

        if lead.status != "approved":
            logger.error(f"Lead {lead_id} is not approved (status: {lead.status})")
            return None

        if lead.imported_to_customer_id:
            logger.warning(
                f"Lead {lead_id} already imported to customer {lead.imported_to_customer_id}"
            )
            return None

        # 检查重复
        duplicate = await LeadImporter.check_duplicate(session, lead.company_name, lead.email)

        if duplicate:
            logger.info(f"Duplicate customer found: {duplicate.id}, updating scraped data")
            # 更新现有客户信息
            duplicate.source = f"数据采集: {lead.data_source}"
            duplicate.data_confidence = lead.confidence_score
            # 合并标签（dict格式）
            existing_tags = duplicate.tags or {}
            new_tags = {tag: True for tag in ["scraped", lead.data_source]}
            duplicate.tags = {**existing_tags, **new_tags}
            duplicate.notes = (
                duplicate.notes or ""
            ) + f"\n\n补充信息:\n{LeadImporter.map_to_customer(lead, imported_by)['notes']}"
            duplicate.updated_at = datetime.utcnow()
            await session.flush()

            # 标记线索已导入
            lead.imported_to_customer_id = str(duplicate.id)
            lead.imported_at = datetime.utcnow()
            lead.status = "imported"
            await session.flush()

            return duplicate

        # 创建新客户
        customer_data = LeadImporter.map_to_customer(lead, imported_by)
        logger.info(
            f"Creating customer with data: company={customer_data['company_name']}, email={customer_data.get('email')}"
        )
        customer = Customer(**customer_data)

        try:
            session.add(customer)
            await session.flush()
            logger.info(f"Customer created and flushed: {customer.id}")

            # 标记线索已导入
            lead.imported_to_customer_id = str(customer.id)
            lead.imported_at = datetime.utcnow()
            lead.status = "imported"
            lead.matched_by = imported_by
            await session.flush()

            logger.info(f"Successfully imported lead {lead_id} as customer {customer.id}")
            return customer

        except Exception as e:
            logger.error(f"Failed to import lead {lead_id}: {e}")
            import traceback

            logger.error(f"Traceback: {traceback.format_exc()}")
            await session.rollback()
            return None

    @staticmethod
    async def batch_import(
        session: AsyncSession, lead_ids: List[str], imported_by: str
    ) -> Dict[str, Any]:
        """
        批量导入线索

        Args:
            session: 数据库会话
            lead_ids: 线索ID列表
            imported_by: 导入操作人ID

        Returns:
            导入结果统计
        """
        results = {"success": [], "failed": [], "duplicates": []}

        for lead_id in lead_ids:
            try:
                customer = await LeadImporter.import_lead(session, lead_id, imported_by)
                if customer:
                    results["success"].append(
                        {
                            "lead_id": lead_id,
                            "customer_id": customer.id,
                            "company_name": customer.company_name,
                        }
                    )
                else:
                    results["failed"].append(lead_id)

            except Exception as e:
                logger.error(f"Failed to import lead {lead_id}: {e}")
                results["failed"].append(lead_id)

        return results
