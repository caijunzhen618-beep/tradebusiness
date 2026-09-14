"""
客户业务逻辑层
处理客户相关的业务逻辑
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    CustomerNotFoundException,
    DuplicateCustomerException,
    InvalidEmailException,
)
from app.models.customer import Customer, CustomerStatus
from app.repositories.customer_repo import CustomerRepository


class CustomerService:
    """客户业务逻辑类"""

    def __init__(self, session: AsyncSession) -> None:
        """
        初始化客户服务

        Args:
            session: 数据库会话
        """
        self.session = session
        self.repo = CustomerRepository(session)

    async def get_customer(self, customer_id: str) -> Customer:
        """
        获取客户信息

        Args:
            customer_id: 客户 ID

        Returns:
            客户对象

        Raises:
            CustomerNotFoundException: 客户不存在时
        """
        customer = await self.repo.get_by_id(customer_id)
        if not customer:
            raise CustomerNotFoundException(customer_id)
        return customer

    async def get_customer_by_email(self, email: str) -> Optional[Customer]:
        """
        通过邮箱获取客户

        Args:
            email: 邮箱地址

        Returns:
            客户对象或 None
        """
        return await self.repo.get_by_email(email)

    async def create_customer(
        self,
        **kwargs,
    ) -> Customer:
        """
        创建新客户

        Args:
            **kwargs: 客户字段值

        Returns:
            创建的客户对象

        Raises:
            DuplicateCustomerException: 客户已存在时
        """
        # 检查邮箱是否已存在
        email = kwargs.get("email")
        if email:
            existing = await self.repo.get_by_email(email)
            if existing:
                raise DuplicateCustomerException("email", email)

        # 检查公司名是否已存在
        company_name = kwargs.get("company_name")
        if company_name:
            existing = await self.repo.get_by_company_name(company_name)
            if existing:
                raise DuplicateCustomerException("company_name", company_name)

        # 创建客户
        customer = await self.repo.create(
            id=uuid.uuid4(),
            **kwargs,
        )

        return customer

    async def update_customer(
        self,
        customer_id: str,
        **kwargs,
    ) -> Customer:
        """
        更新客户信息

        Args:
            customer_id: 客户 ID
            **kwargs: 要更新的字段

        Returns:
            更新后的客户对象

        Raises:
            CustomerNotFoundException: 客户不存在时
            DuplicateCustomerException: 更新导致冲突时
        """
        customer = await self.get_customer(customer_id)

        # 如果更新邮箱，检查新邮箱是否已被其他客户使用
        if "email" in kwargs and kwargs["email"]:
            existing = await self.repo.get_by_email(kwargs["email"])
            if existing and existing.id != customer.id:
                raise DuplicateCustomerException("email", kwargs["email"])

        # 如果更新公司名，检查新公司名是否已被其他客户使用
        if "company_name" in kwargs and kwargs["company_name"]:
            existing = await self.repo.get_by_company_name(kwargs["company_name"])
            if existing and existing.id != customer.id:
                raise DuplicateCustomerException("company_name", kwargs["company_name"])

        # 更新验证时间
        if any(k in kwargs for k in ["email", "phone", "website"]):
            kwargs["last_verified_at"] = datetime.utcnow()

        return await self.repo.update(customer, **kwargs)

    async def delete_customer(self, customer_id: str) -> None:
        """
        删除客户

        Args:
            customer_id: 客户 ID

        Raises:
            CustomerNotFoundException: 客户不存在时
        """
        customer = await self.get_customer(customer_id)
        await self.repo.delete(customer)

    async def assign_customer(
        self,
        customer_id: str,
        user_id: uuid.UUID,
    ) -> Customer:
        """
        分配客户给用户

        Args:
            customer_id: 客户 ID
            user_id: 用户 ID

        Returns:
            更新后的客户对象

        Raises:
            CustomerNotFoundException: 客户不存在时
        """
        customer = await self.get_customer(customer_id)
        customer.assigned_to = user_id
        await self.session.flush()
        return customer

    async def unassign_customer(self, customer_id: str) -> Customer:
        """
        取消客户分配

        Args:
            customer_id: 客户 ID

        Returns:
            更新后的客户对象

        Raises:
            CustomerNotFoundException: 客户不存在时
        """
        customer = await self.get_customer(customer_id)
        customer.assigned_to = None
        await self.session.flush()
        return customer

    async def update_customer_status(
        self,
        customer_id: str,
        status: CustomerStatus,
    ) -> Customer:
        """
        更新客户状态

        Args:
            customer_id: 客户 ID
            status: 新状态

        Returns:
            更新后的客户对象

        Raises:
            CustomerNotFoundException: 客户不存在时
        """
        customer = await self.get_customer(customer_id)

        # 如果状态变为合作中，记录合作日期
        if status == CustomerStatus.COOPERATING and not customer.cooperation_date:
            from datetime import date

            customer.cooperation_date = date.today()

        # 如果状态变为联系中，记录首次联系日期
        if status == CustomerStatus.CONTACTING and not customer.first_contact_date:
            from datetime import date

            customer.first_contact_date = date.today()

        customer.status = status
        await self.session.flush()

        return customer

    async def batch_import_customers(
        self,
        customers_data: list[dict],
        overwrite: bool = False,
    ) -> dict[str, any]:
        """
        批量导入客户

        Args:
            customers_data: 客户数据列表
            overwrite: 是否覆盖已存在的客户

        Returns:
            导入结果统计
        """
        created = 0
        updated = 0
        failed = 0
        errors = []

        for data in customers_data:
            try:
                # 检查客户是否已存在（基于邮箱）
                email = data.get("email")
                if email:
                    existing = await self.repo.get_by_email(email)
                    if existing:
                        if overwrite:
                            # 更新已存在的客户
                            await self.update_customer(str(existing.id), **data)
                            updated += 1
                        else:
                            # 跳过已存在的客户
                            errors.append(
                                {
                                    "company": data.get("company_name"),
                                    "reason": "Customer already exists",
                                }
                            )
                            failed += 1
                        continue

                # 创建新客户
                await self.create_customer(**data)
                created += 1

            except Exception as e:
                failed += 1
                errors.append(
                    {
                        "company": data.get("company_name"),
                        "reason": str(e),
                    }
                )

        return {
            "total": len(customers_data),
            "created": created,
            "updated": updated,
            "failed": failed,
            "errors": errors,
        }

    async def list_customers(
        self,
        skip: int = 0,
        limit: int = 100,
        country: Optional[str] = None,
        status: Optional[CustomerStatus] = None,
        assigned_to: Optional[uuid.UUID] = None,
        priority: Optional[int] = None,
        tags: Optional[list[str]] = None,
        search: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> tuple[list[Customer], int]:
        """
        获取客户列表（支持筛选）

        Args:
            skip: 分页偏移
            limit: 分页大小
            country: 国家筛选
            status: 状态筛选
            assigned_to: 分配给的用户ID
            priority: 优先级筛选
            tags: 标签筛选
            search: 搜索关键词
            sort_by: 排序字段
            sort_order: 排序方向

        Returns:
            (客户列表, 总数)
        """
        # 如果有搜索关键词，使用搜索
        if search:
            customers = await self.repo.search_customers(search, skip, limit)
            total = len(customers)  # 搜索结果总数（简化处理）
            return customers, total

        # 否则使用筛选
        return await self.repo.filter_customers(
            country=country,
            status=status,
            assigned_to=assigned_to,
            priority=priority,
            tags=tags,
            skip=skip,
            limit=limit,
            sort_by=sort_by,
            sort_order=sort_order,
        )

    async def get_statistics(self) -> dict[str, any]:
        """
        获取客户统计信息

        Returns:
            统计数据字典
        """
        total = await self.repo.count()
        status_counts = await self.repo.count_by_status()
        country_counts = await self.repo.count_by_country()
        top_countries = await self.repo.get_top_countries(10)

        return {
            "total": total,
            "by_status": status_counts,
            "by_country": country_counts,
            "top_countries": top_countries,
        }
