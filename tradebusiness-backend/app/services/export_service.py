"""
数据导出服务
支持导出客户、邮件等数据为 Excel、CSV 格式
"""

import io
from datetime import datetime
from typing import List, Optional

import pandas as pd
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger import get_logger
from app.models.customer import Customer
from app.models.email import Email
from app.models.user import User

logger = get_logger(__name__)


class ExportService:
    """数据导出服务"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def export_customers(
        self,
        format: str = "xlsx",
        filters: Optional[dict] = None,
    ) -> bytes:
        """
        导出客户数据

        Args:
            format: 导出格式 (xlsx, csv)
            filters: 筛选条件

        Returns:
            文件内容（bytes）
        """
        try:
            # 查询客户数据
            stmt = select(Customer)
            result = await self.db.execute(stmt)
            customers = result.scalars().all()

            # 转换为字典列表
            data = []
            for customer in customers:
                data.append(
                    {
                        "ID": customer.id,
                        "公司名称": customer.company_name,
                        "英文名称": customer.company_name_en or "",
                        "国家": customer.country,
                        "城市": customer.city or "",
                        "邮箱": customer.email or "",
                        "电话": customer.phone or "",
                        "WhatsApp": customer.whatsapp or "",
                        "业务类型": self._get_business_type_text(customer.business_type),
                        "状态": self._get_status_text(customer.status),
                        "优先级": customer.priority,
                        "创建时间": (
                            customer.created_at.strftime("%Y-%m-%d %H:%M:%S")
                            if customer.created_at
                            else ""
                        ),
                        "更新时间": (
                            customer.updated_at.strftime("%Y-%m-%d %H:%M:%S")
                            if customer.updated_at
                            else ""
                        ),
                    }
                )

            # 创建 DataFrame
            df = pd.DataFrame(data)

            # 导出
            if format == "xlsx":
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine="openpyxl") as writer:
                    df.to_excel(writer, index=False, sheet_name="Customers")
                output.seek(0)
                return output.read()

            elif format == "csv":
                output = io.BytesIO()
                df.to_csv(output, index=False, encoding="utf-8-sig")
                output.seek(0)
                return output.read()

            else:
                raise HTTPException(status_code=400, detail=f"Unsupported format: {format}")

        except Exception as e:
            logger.error(f"Failed to export customers: {e}")
            raise HTTPException(status_code=500, detail="Failed to export customers")

    async def export_emails(
        self,
        format: str = "xlsx",
        filters: Optional[dict] = None,
    ) -> bytes:
        """
        导出邮件数据

        Args:
            format: 导出格式 (xlsx, csv)
            filters: 筛选条件

        Returns:
            文件内容（bytes）
        """
        try:
            # 查询邮件数据
            stmt = select(Email)
            result = await self.db.execute(stmt)
            emails = result.scalars().all()

            # 转换为字典列表
            data = []
            for email in emails:
                data.append(
                    {
                        "ID": email.id,
                        "主题": email.subject,
                        "收件人": email.to_email,
                        "发件人": email.from_email,
                        "方向": "发送" if email.direction == "outgoing" else "接收",
                        "状态": email.status,
                        "发送时间": (
                            email.sent_at.strftime("%Y-%m-%d %H:%M:%S") if email.sent_at else ""
                        ),
                        "打开时间": (
                            email.opened_at.strftime("%Y-%m-%d %H:%M:%S") if email.opened_at else ""
                        ),
                        "回复时间": (
                            email.replied_at.strftime("%Y-%m-%d %H:%M:%S")
                            if email.replied_at
                            else ""
                        ),
                        "创建时间": (
                            email.created_at.strftime("%Y-%m-%d %H:%M:%S")
                            if email.created_at
                            else ""
                        ),
                    }
                )

            # 创建 DataFrame
            df = pd.DataFrame(data)

            # 导出
            if format == "xlsx":
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine="openpyxl") as writer:
                    df.to_excel(writer, index=False, sheet_name="Emails")
                output.seek(0)
                return output.read()

            elif format == "csv":
                output = io.BytesIO()
                df.to_csv(output, index=False, encoding="utf-8-sig")
                output.seek(0)
                return output.read()

            else:
                raise HTTPException(status_code=400, detail=f"Unsupported format: {format}")

        except Exception as e:
            logger.error(f"Failed to export emails: {e}")
            raise HTTPException(status_code=500, detail="Failed to export emails")

    async def export_customer_stats(
        self,
        format: str = "xlsx",
    ) -> bytes:
        """
        导出客户统计报表

        Args:
            format: 导出格式 (xlsx, csv)

        Returns:
            文件内容（bytes）
        """
        try:
            # 查询客户数据
            stmt = select(Customer)
            result = await self.db.execute(stmt)
            customers = result.scalars().all()

            # 统计数据
            stats = {
                "总客户数": len(customers),
                "潜在客户": len([c for c in customers if c.status == "potential"]),
                "联系中": len([c for c in customers if c.status == "contacting"]),
                "合作中": len([c for c in customers if c.status == "cooperating"]),
                "暂停": len([c for c in customers if c.status == "paused"]),
                "流失": len([c for c in customers if c.status == "lost"]),
            }

            # 按国家统计
            country_stats = {}
            for customer in customers:
                if customer.country not in country_stats:
                    country_stats[customer.country] = 0
                country_stats[customer.country] += 1

            # 创建 DataFrame
            stats_data = [{"指标": key, "数量": value} for key, value in stats.items()]

            country_data = [
                {"国家": country, "客户数量": count}
                for country, count in sorted(
                    country_stats.items(), key=lambda x: x[1], reverse=True
                )
            ]

            # 导出
            if format == "xlsx":
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine="openpyxl") as writer:
                    # 总体统计
                    pd.DataFrame(stats_data).to_excel(writer, index=False, sheet_name="总体统计")
                    # 国家分布
                    pd.DataFrame(country_data).to_excel(writer, index=False, sheet_name="国家分布")
                output.seek(0)
                return output.read()

            elif format == "csv":
                # CSV 只导出总体统计
                output = io.BytesIO()
                pd.DataFrame(stats_data).to_csv(output, index=False, encoding="utf-8-sig")
                output.seek(0)
                return output.read()

            else:
                raise HTTPException(status_code=400, detail=f"Unsupported format: {format}")

        except Exception as e:
            logger.error(f"Failed to export customer stats: {e}")
            raise HTTPException(status_code=500, detail="Failed to export customer stats")

    def _get_business_type_text(self, business_type: Optional[str]) -> str:
        """获取业务类型文本"""
        type_map = {
            "sea": "海运",
            "air": "空运",
            "land": "陆运",
            "multimodal": "多式联运",
        }
        return type_map.get(business_type, business_type or "")

    def _get_status_text(self, status: str) -> str:
        """获取状态文本"""
        status_map = {
            "potential": "潜在客户",
            "contacting": "联系中",
            "cooperating": "合作中",
            "paused": "暂停",
            "lost": "流失",
        }
        return status_map.get(status, status)
