"""
客户数据访问层
处理客户相关的数据库操作
"""

from typing import Optional

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.customer import Customer, CustomerStatus
from app.repositories.base import BaseRepository


class CustomerRepository(BaseRepository[Customer]):
    """客户 Repository"""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Customer, session)

    async def get_by_email(self, email: str) -> Optional[Customer]:
        """
        通过邮箱获取客户

        Args:
            email: 邮箱地址

        Returns:
            客户对象或 None
        """
        stmt = select(Customer).where(Customer.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_company_name(self, company_name: str) -> Optional[Customer]:
        """
        通过公司名获取客户

        Args:
            company_name: 公司名称

        Returns:
            客户对象或 None
        """
        stmt = select(Customer).where(Customer.company_name == company_name)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_assigned_customers(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Customer]:
        """
        获取分配给指定用户的客户列表

        Args:
            user_id: 用户 ID
            skip: 跳过的记录数
            limit: 返回的记录数

        Returns:
            客户列表
        """
        stmt = (
            select(Customer)
            .where(Customer.assigned_to == user_id)
            .order_by(Customer.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_unassigned_customers(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Customer]:
        """
        获取未分配的客户列表

        Args:
            skip: 跳过的记录数
            limit: 返回的记录数

        Returns:
            客户列表
        """
        stmt = (
            select(Customer)
            .where(Customer.assigned_to.is_(None))
            .order_by(Customer.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_country(
        self,
        country: str,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Customer]:
        """
        获取指定国家的客户列表

        Args:
            country: 国家名称
            skip: 跳过的记录数
            limit: 返回的记录数

        Returns:
            客户列表
        """
        stmt = (
            select(Customer)
            .where(Customer.country == country)
            .order_by(Customer.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_status(
        self,
        status: CustomerStatus,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Customer]:
        """
        获取指定状态的客户列表

        Args:
            status: 客户状态
            skip: 跳过的记录数
            limit: 返回的记录数

        Returns:
            客户列表
        """
        stmt = (
            select(Customer)
            .where(Customer.status == status)
            .order_by(Customer.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def search_customers(
        self,
        keyword: str,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Customer]:
        """
        搜索客户（按公司名、邮箱等）

        Args:
            keyword: 搜索关键词
            skip: 跳过的记录数
            limit: 返回的记录数

        Returns:
            客户列表
        """
        stmt = (
            select(Customer)
            .where(
                or_(
                    Customer.company_name.ilike(f"%{keyword}%"),
                    Customer.company_name_en.ilike(f"%{keyword}%"),
                    Customer.email.ilike(f"%{keyword}%"),
                    Customer.country.ilike(f"%{keyword}%"),
                )
            )
            .order_by(Customer.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def filter_customers(
        self,
        country: Optional[str] = None,
        status: Optional[CustomerStatus] = None,
        assigned_to: Optional[str] = None,
        priority: Optional[int] = None,
        tags: Optional[list[str]] = None,
        skip: int = 0,
        limit: int = 100,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> tuple[list[Customer], int]:
        """
        筛选客户列表

        Args:
            country: 国家筛选
            status: 状态筛选
            assigned_to: 分配给的用户ID筛选
            priority: 优先级筛选
            tags: 标签筛选
            skip: 跳过的记录数
            limit: 返回的记录数
            sort_by: 排序字段
            sort_order: 排序方向

        Returns:
            (客户列表, 总数)
        """
        # 构建查询条件
        conditions = []

        if country:
            conditions.append(Customer.country == country)

        if status:
            conditions.append(Customer.status == status)

        if assigned_to is not None:
            conditions.append(Customer.assigned_to == assigned_to)

        if priority is not None:
            conditions.append(Customer.priority == priority)

        # MySQL 不支持 overlap()，使用 JSON_CONTAINS 检查标签
        if tags:
            for tag in tags:
                # 检查 JSON 字段中是否包含指定标签
                conditions.append(func.json_contains(Customer.tags, f'"{tag}"}}'))

        # 构建基础查询
        stmt = select(Customer)

        if conditions:
            stmt = stmt.where(and_(*conditions))

        # 获取总数
        count_stmt = select(func.count()).select_from(Customer)
        if conditions:
            count_stmt = count_stmt.where(and_(*conditions))
        count_result = await self.session.execute(count_stmt)
        total = count_result.scalar() or 0

        # 排序
        sort_column = getattr(Customer, sort_by, Customer.created_at)
        if sort_order == "desc":
            stmt = stmt.order_by(sort_column.desc())
        else:
            stmt = stmt.order_by(sort_column.asc())

        # 分页
        stmt = stmt.offset(skip).limit(limit)

        result = await self.session.execute(stmt)
        customers = list(result.scalars().all())

        return customers, total

    async def get_african_countries(self) -> list[str]:
        """
        获取所有非洲国家的列表

        Returns:
            国家列表（不重复）
        """
        # 主要非洲国家列表
        african_countries = [
            "Nigeria",
            "South Africa",
            "Egypt",
            "Kenya",
            "Morocco",
            "Ghana",
            "Ethiopia",
            "Tanzania",
            "Ivory Coast",
            "Senegal",
            "Uganda",
            "Rwanda",
            "Cameroon",
            "Angola",
            "Mozambique",
            "Zambia",
            "Zimbabwe",
            "Namibia",
            "Botswana",
        ]

        stmt = (
            select(Customer.country)
            .where(Customer.country.in_(african_countries))
            .distinct()
            .order_by(Customer.country)
        )
        result = await self.session.execute(stmt)
        return [row[0] for row in result.all()]

    async def get_top_countries(self, limit: int = 10) -> list[tuple[str, int]]:
        """
        获取客户数量最多的国家

        Args:
            limit: 返回的国家数量

        Returns:
            [(国家名, 客户数), ...] 列表
        """
        stmt = (
            select(Customer.country, func.count(Customer.id).label("count"))
            .group_by(Customer.country)
            .order_by(func.count(Customer.id).desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return [(row.country, row.count) for row in result.all()]

    async def count_by_status(self) -> dict[str, int]:
        """
        统计各状态的客户数量

        Returns:
            {状态: 数量} 字典
        """
        stmt = select(Customer.status, func.count(Customer.id)).group_by(Customer.status)
        result = await self.session.execute(stmt)
        return {row.status: row.count for row in result.all()}

    async def count_by_country(self) -> dict[str, int]:
        """
        统计各国家的客户数量

        Returns:
            {国家: 数量} 字典
        """
        stmt = select(Customer.country, func.count(Customer.id)).group_by(Customer.country)
        result = await self.session.execute(stmt)
        return {row.country: row.count for row in result.all()}
