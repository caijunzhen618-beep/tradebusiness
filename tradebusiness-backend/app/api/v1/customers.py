"""
客户管理 API
包含客户的 CRUD 操作
"""

import uuid
from typing import Optional

from fastapi import APIRouter, Body, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_admin_user, get_current_user, get_db
from app.models.customer import CustomerStatus
from app.models.user import User
from app.schemas.common import MessageResponse, PaginatedResponse
from app.schemas.customer import (
    CustomerBatchImport,
    CustomerCreate,
    CustomerListParams,
    CustomerResponse,
    CustomerUpdate,
)
from app.services.customer_service import CustomerService

router = APIRouter()


@router.get("", response_model=PaginatedResponse[CustomerResponse])
async def list_customers(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(20, ge=1, le=100, description="返回的记录数"),
    country: Optional[str] = Query(None, description="国家筛选"),
    status: Optional[CustomerStatus] = Query(None, description="状态筛选"),
    business_type: Optional[str] = Query(None, description="业务类型筛选"),
    assigned_to: Optional[str] = Query(None, description="分配给的用户ID"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    priority: Optional[int] = Query(None, ge=1, le=5, description="优先级筛选"),
    tags: Optional[list[str]] = Query(None, description="标签筛选"),
    sort_by: str = Query("created_at", description="排序字段"),
    sort_order: str = Query("desc", description="排序方向"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取客户列表

    支持分页、筛选和排序。

    Args:
        skip: 跳过的记录数
        limit: 返回的记录数
        country: 国家筛选
        status: 状态筛选
        business_type: 业务类型筛选
        assigned_to: 分配给的用户ID
        search: 搜索关键词
        priority: 优先级筛选
        tags: 标签筛选
        sort_by: 排序字段
        sort_order: 排序方向（asc/desc）
        current_user: 当前用户
        db: 数据库会话

    Returns:
        分页的客户列表
    """
    customer_service = CustomerService(db)

    # 非管理员只能查看分配给自己的客户
    assigned_to_uuid = None
    if not current_user.is_admin:
        assigned_to_uuid = current_user.id
    elif assigned_to:
        assigned_to_uuid = uuid.UUID(assigned_to) if assigned_to else None

    customers, total = await customer_service.list_customers(
        skip=skip,
        limit=limit,
        country=country,
        status=status,
        assigned_to=assigned_to_uuid,
        priority=priority,
        tags=tags,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    customer_responses = [
        CustomerResponse(
            id=str(customer.id),
            company_name=customer.company_name,
            company_name_en=customer.company_name_en,
            company_name_local=customer.company_name_local,
            logo_url=customer.logo_url,
            website=customer.website,
            established_year=customer.established_year,
            registered_capital=customer.registered_capital,
            company_size=customer.company_size,
            business_type=customer.business_type,
            main_ports=customer.main_ports,
            route_coverage=customer.route_coverage,
            cargo_specialization=customer.cargo_specialization,
            estimated_volume=customer.estimated_volume,
            country_code=customer.country_code,
            country=customer.country,
            city=customer.city,
            address=customer.address,
            phone=customer.phone,
            email=customer.email,
            whatsapp=customer.whatsapp,
            wechat=customer.wechat,
            linkedin_url=customer.linkedin_url,
            facebook_url=customer.facebook_url,
            status=customer.status,
            priority=customer.priority,
            assigned_to=str(customer.assigned_to) if customer.assigned_to else None,
            source=customer.source,
            source_url=customer.source_url,
            data_confidence=float(customer.data_confidence) if customer.data_confidence else None,
            last_verified_at=customer.last_verified_at,
            tags=customer.tags,
            notes=customer.notes,
            first_contact_date=customer.first_contact_date,
            cooperation_date=customer.cooperation_date,
            created_at=customer.created_at,
            updated_at=customer.updated_at,
        )
        for customer in customers
    ]

    return PaginatedResponse.create(
        items=customer_responses,
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/stats")
async def get_customer_statistics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取客户统计信息

    Args:
        current_user: 当前用户
        db: 数据库会话

    Returns:
        统计数据
    """
    customer_service = CustomerService(db)
    stats = await customer_service.get_statistics()
    return stats


@router.get("/my", response_model=PaginatedResponse[CustomerResponse])
async def get_my_customers(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[CustomerStatus] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取分配给我的客户列表

    Args:
        skip: 跳过的记录数
        limit: 返回的记录数
        status: 状态筛选
        current_user: 当前用户
        db: 数据库会话

    Returns:
        分页的客户列表
    """
    customer_service = CustomerService(db)

    customers, total = await customer_service.list_customers(
        skip=skip,
        limit=limit,
        status=status,
        assigned_to=current_user.id,
    )

    customer_responses = [
        CustomerResponse(
            id=str(customer.id),
            company_name=customer.company_name,
            company_name_en=customer.company_name_en,
            company_name_local=customer.company_name_local,
            logo_url=customer.logo_url,
            website=customer.website,
            established_year=customer.established_year,
            registered_capital=customer.registered_capital,
            company_size=customer.company_size,
            business_type=customer.business_type,
            main_ports=customer.main_ports,
            route_coverage=customer.route_coverage,
            cargo_specialization=customer.cargo_specialization,
            estimated_volume=customer.estimated_volume,
            country_code=customer.country_code,
            country=customer.country,
            city=customer.city,
            address=customer.address,
            phone=customer.phone,
            email=customer.email,
            whatsapp=customer.whatsapp,
            wechat=customer.wechat,
            linkedin_url=customer.linkedin_url,
            facebook_url=customer.facebook_url,
            status=customer.status,
            priority=customer.priority,
            assigned_to=str(customer.assigned_to) if customer.assigned_to else None,
            source=customer.source,
            source_url=customer.source_url,
            data_confidence=float(customer.data_confidence) if customer.data_confidence else None,
            last_verified_at=customer.last_verified_at,
            tags=customer.tags,
            notes=customer.notes,
            first_contact_date=customer.first_contact_date,
            cooperation_date=customer.cooperation_date,
            created_at=customer.created_at,
            updated_at=customer.updated_at,
        )
        for customer in customers
    ]

    return PaginatedResponse.create(
        items=customer_responses,
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/unassigned", response_model=PaginatedResponse[CustomerResponse])
async def get_unassigned_customers(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取未分配的客户列表

    Args:
        skip: 跳过的记录数
        limit: 返回的记录数
        current_user: 当前用户
        db: 数据库会话

    Returns:
        分页的客户列表
    """
    customer_service = CustomerService(db)

    customers, total = await customer_service.list_customers(
        skip=skip,
        limit=limit,
        assigned_to=None,
    )

    customer_responses = [
        CustomerResponse(
            id=str(customer.id),
            company_name=customer.company_name,
            company_name_en=customer.company_name_en,
            company_name_local=customer.company_name_local,
            logo_url=customer.logo_url,
            website=customer.website,
            established_year=customer.established_year,
            registered_capital=customer.registered_capital,
            company_size=customer.company_size,
            business_type=customer.business_type,
            main_ports=customer.main_ports,
            route_coverage=customer.route_coverage,
            cargo_specialization=customer.cargo_specialization,
            estimated_volume=customer.estimated_volume,
            country_code=customer.country_code,
            country=customer.country,
            city=customer.city,
            address=customer.address,
            phone=customer.phone,
            email=customer.email,
            whatsapp=customer.whatsapp,
            wechat=customer.wechat,
            linkedin_url=customer.linkedin_url,
            facebook_url=customer.facebook_url,
            status=customer.status,
            priority=customer.priority,
            assigned_to=str(customer.assigned_to) if customer.assigned_to else None,
            source=customer.source,
            source_url=customer.source_url,
            data_confidence=float(customer.data_confidence) if customer.data_confidence else None,
            last_verified_at=customer.last_verified_at,
            tags=customer.tags,
            notes=customer.notes,
            first_contact_date=customer.first_contact_date,
            cooperation_date=customer.cooperation_date,
            created_at=customer.created_at,
            updated_at=customer.updated_at,
        )
        for customer in customers
    ]

    return PaginatedResponse.create(
        items=customer_responses,
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取客户详情

    Args:
        customer_id: 客户 ID
        current_user: 当前用户
        db: 数据库会话

    Returns:
        客户详细信息

    Raises:
        403: 权限不足
        404: 客户不存在
    """
    customer_service = CustomerService(db)
    customer = await customer_service.get_customer(customer_id)

    # 非管理员只能查看分配给自己的客户
    if not current_user.is_admin and customer.assigned_to != current_user.id:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own customers",
        )

    return CustomerResponse(
        id=str(customer.id),
        company_name=customer.company_name,
        company_name_en=customer.company_name_en,
        company_name_local=customer.company_name_local,
        logo_url=customer.logo_url,
        website=customer.website,
        established_year=customer.established_year,
        registered_capital=customer.registered_capital,
        company_size=customer.company_size,
        business_type=customer.business_type,
        main_ports=customer.main_ports,
        route_coverage=customer.route_coverage,
        cargo_specialization=customer.cargo_specialization,
        estimated_volume=customer.estimated_volume,
        country_code=customer.country_code,
        country=customer.country,
        city=customer.city,
        address=customer.address,
        phone=customer.phone,
        email=customer.email,
        whatsapp=customer.whatsapp,
        wechat=customer.wechat,
        linkedin_url=customer.linkedin_url,
        facebook_url=customer.facebook_url,
        status=customer.status,
        priority=customer.priority,
        assigned_to=str(customer.assigned_to) if customer.assigned_to else None,
        source=customer.source,
        source_url=customer.source_url,
        data_confidence=float(customer.data_confidence) if customer.data_confidence else None,
        last_verified_at=customer.last_verified_at,
        tags=customer.tags,
        notes=customer.notes,
        first_contact_date=customer.first_contact_date,
        cooperation_date=customer.cooperation_date,
        created_at=customer.created_at,
        updated_at=customer.updated_at,
    )


@router.post("", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
async def create_customer(
    customer_data: CustomerCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    创建新客户

    Args:
        customer_data: 客户创建数据
        current_user: 当前用户
        db: 数据库会话

    Returns:
        创建的客户信息

    Raises:
        400: 客户已存在
    """
    customer_service = CustomerService(db)

    # 如果不是管理员且没有指定 assigned_to，自动分配给自己
    create_data = customer_data.model_dump()
    if not current_user.is_admin and not create_data.get("assigned_to"):
        create_data["assigned_to"] = current_user.id

    customer = await customer_service.create_customer(**create_data)

    return CustomerResponse(
        id=str(customer.id),
        company_name=customer.company_name,
        company_name_en=customer.company_name_en,
        company_name_local=customer.company_name_local,
        logo_url=customer.logo_url,
        website=customer.website,
        established_year=customer.established_year,
        registered_capital=customer.registered_capital,
        company_size=customer.company_size,
        business_type=customer.business_type,
        main_ports=customer.main_ports,
        route_coverage=customer.route_coverage,
        cargo_specialization=customer.cargo_specialization,
        estimated_volume=customer.estimated_volume,
        country_code=customer.country_code,
        country=customer.country,
        city=customer.city,
        address=customer.address,
        phone=customer.phone,
        email=customer.email,
        whatsapp=customer.whatsapp,
        wechat=customer.wechat,
        linkedin_url=customer.linkedin_url,
        facebook_url=customer.facebook_url,
        status=customer.status,
        priority=customer.priority,
        assigned_to=str(customer.assigned_to) if customer.assigned_to else None,
        source=customer.source,
        source_url=customer.source_url,
        data_confidence=float(customer.data_confidence) if customer.data_confidence else None,
        last_verified_at=customer.last_verified_at,
        tags=customer.tags,
        notes=customer.notes,
        first_contact_date=customer.first_contact_date,
        cooperation_date=customer.cooperation_date,
        created_at=customer.created_at,
        updated_at=customer.updated_at,
    )


@router.put("/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: str,
    customer_data: CustomerUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    更新客户信息

    Args:
        customer_id: 客户 ID
        customer_data: 更新数据
        current_user: 当前用户
        db: 数据库会话

    Returns:
        更新后的客户信息

    Raises:
        403: 权限不足
        404: 客户不存在
    """
    customer_service = CustomerService(db)
    customer = await customer_service.get_customer(customer_id)

    # 非管理员只能更新分配给自己的客户
    if not current_user.is_admin and customer.assigned_to != current_user.id:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own customers",
        )

    # 非管理员不能修改 assigned_to 和 status
    update_data = customer_data.model_dump(exclude_unset=True)
    if not current_user.is_admin:
        update_data.pop("assigned_to", None)
        # 业务员可以修改状态，但不能从合作改为其他状态
        if "status" in update_data:
            from fastapi import HTTPException

            if customer.status == CustomerStatus.COOPERATING:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Cannot change status from cooperating",
                )

    customer = await customer_service.update_customer(customer_id, **update_data)

    return CustomerResponse(
        id=str(customer.id),
        company_name=customer.company_name,
        company_name_en=customer.company_name_en,
        company_name_local=customer.company_name_local,
        logo_url=customer.logo_url,
        website=customer.website,
        established_year=customer.established_year,
        registered_capital=customer.registered_capital,
        company_size=customer.company_size,
        business_type=customer.business_type,
        main_ports=customer.main_ports,
        route_coverage=customer.route_coverage,
        cargo_specialization=customer.cargo_specialization,
        estimated_volume=customer.estimated_volume,
        country_code=customer.country_code,
        country=customer.country,
        city=customer.city,
        address=customer.address,
        phone=customer.phone,
        email=customer.email,
        whatsapp=customer.whatsapp,
        wechat=customer.wechat,
        linkedin_url=customer.linkedin_url,
        facebook_url=customer.facebook_url,
        status=customer.status,
        priority=customer.priority,
        assigned_to=str(customer.assigned_to) if customer.assigned_to else None,
        source=customer.source,
        source_url=customer.source_url,
        data_confidence=float(customer.data_confidence) if customer.data_confidence else None,
        last_verified_at=customer.last_verified_at,
        tags=customer.tags,
        notes=customer.notes,
        first_contact_date=customer.first_contact_date,
        cooperation_date=customer.cooperation_date,
        created_at=customer.created_at,
        updated_at=customer.updated_at,
    )


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_customer(
    customer_id: str,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    删除客户

    需要管理员权限。

    Args:
        customer_id: 客户 ID
        current_user: 当前用户（需管理员）
        db: 数据库会话

    Raises:
        404: 客户不存在
    """
    customer_service = CustomerService(db)
    await customer_service.delete_customer(customer_id)


@router.post("/{customer_id}/assign", response_model=CustomerResponse)
async def assign_customer(
    customer_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    分配客户给自己

    将未分配的客户分配给当前用户。

    Args:
        customer_id: 客户 ID
        current_user: 当前用户
        db: 数据库会话

    Returns:
        更新后的客户信息

    Raises:
        404: 客户不存在
        400: 客户已分配
    """
    customer_service = CustomerService(db)
    customer = await customer_service.assign_customer(customer_id, current_user.id)

    return CustomerResponse(
        id=str(customer.id),
        company_name=customer.company_name,
        company_name_en=customer.company_name_en,
        company_name_local=customer.company_name_local,
        logo_url=customer.logo_url,
        website=customer.website,
        established_year=customer.established_year,
        registered_capital=customer.registered_capital,
        company_size=customer.company_size,
        business_type=customer.business_type,
        main_ports=customer.main_ports,
        route_coverage=customer.route_coverage,
        cargo_specialization=customer.cargo_specialization,
        estimated_volume=customer.estimated_volume,
        country_code=customer.country_code,
        country=customer.country,
        city=customer.city,
        address=customer.address,
        phone=customer.phone,
        email=customer.email,
        whatsapp=customer.whatsapp,
        wechat=customer.wechat,
        linkedin_url=customer.linkedin_url,
        facebook_url=customer.facebook_url,
        status=customer.status,
        priority=customer.priority,
        assigned_to=str(customer.assigned_to) if customer.assigned_to else None,
        source=customer.source,
        source_url=customer.source_url,
        data_confidence=float(customer.data_confidence) if customer.data_confidence else None,
        last_verified_at=customer.last_verified_at,
        tags=customer.tags,
        notes=customer.notes,
        first_contact_date=customer.first_contact_date,
        cooperation_date=customer.cooperation_date,
        created_at=customer.created_at,
        updated_at=customer.updated_at,
    )


@router.post("/{customer_id}/unassign", response_model=CustomerResponse)
async def unassign_customer(
    customer_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    取消客户分配

    管理员可以取消任意客户分配；普通用户只能取消自己名下客户。
    """
    customer_service = CustomerService(db)
    customer = await customer_service.get_customer(customer_id)

    if not current_user.is_admin and customer.assigned_to != current_user.id:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only unassign your own customers",
        )

    customer = await customer_service.unassign_customer(customer_id)
    return _customer_to_response(customer)


@router.post("/{customer_id}/status", response_model=CustomerResponse)
async def update_customer_status(
    customer_id: str,
    new_status: CustomerStatus = Body(..., embed=True),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    更新客户状态

    Args:
        customer_id: 客户 ID
        new_status: 新状态
        current_user: 当前用户
        db: 数据库会话

    Returns:
        更新后的客户信息

    Raises:
        403: 权限不足
        404: 客户不存在
    """
    customer_service = CustomerService(db)
    customer = await customer_service.get_customer(customer_id)

    # 非管理员只能更新分配给自己的客户
    if not current_user.is_admin and customer.assigned_to != current_user.id:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own customers",
        )

    customer = await customer_service.update_customer_status(customer_id, new_status)

    return CustomerResponse(
        id=str(customer.id),
        company_name=customer.company_name,
        company_name_en=customer.company_name_en,
        company_name_local=customer.company_name_local,
        logo_url=customer.logo_url,
        website=customer.website,
        established_year=customer.established_year,
        registered_capital=customer.registered_capital,
        company_size=customer.company_size,
        business_type=customer.business_type,
        main_ports=customer.main_ports,
        route_coverage=customer.route_coverage,
        cargo_specialization=customer.cargo_specialization,
        estimated_volume=customer.estimated_volume,
        country_code=customer.country_code,
        country=customer.country,
        city=customer.city,
        address=customer.address,
        phone=customer.phone,
        email=customer.email,
        whatsapp=customer.whatsapp,
        wechat=customer.wechat,
        linkedin_url=customer.linkedin_url,
        facebook_url=customer.facebook_url,
        status=customer.status,
        priority=customer.priority,
        assigned_to=str(customer.assigned_to) if customer.assigned_to else None,
        source=customer.source,
        source_url=customer.source_url,
        data_confidence=float(customer.data_confidence) if customer.data_confidence else None,
        last_verified_at=customer.last_verified_at,
        tags=customer.tags,
        notes=customer.notes,
        first_contact_date=customer.first_contact_date,
        cooperation_date=customer.cooperation_date,
        created_at=customer.created_at,
        updated_at=customer.updated_at,
    )


@router.post("/batch", response_model=MessageResponse)
async def batch_import_customers(
    import_data: CustomerBatchImport,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    批量导入客户

    Args:
        import_data: 导入数据
        current_user: 当前用户
        db: 数据库会话

    Returns:
        导入结果统计
    """
    customer_service = CustomerService(db)

    # 如果不是管理员，自动将所有客户分配给自己
    customers_data = [c.model_dump() for c in import_data.customers]
    if not current_user.is_admin:
        for data in customers_data:
            if not data.get("assigned_to"):
                data["assigned_to"] = current_user.id

    result = await customer_service.batch_import_customers(
        customers_data,
        import_data.overwrite,
    )

    return MessageResponse(
        code=200,
        message=f"导入完成：成功 {result['created']} 条，更新 {result['updated']} 条，失败 {result['failed']} 条",
        data=result,
    )


def _customer_to_response(customer) -> CustomerResponse:
    """将客户模型转换为响应 Schema。"""
    return CustomerResponse(
        id=str(customer.id),
        company_name=customer.company_name,
        company_name_en=customer.company_name_en,
        company_name_local=customer.company_name_local,
        logo_url=customer.logo_url,
        website=customer.website,
        established_year=customer.established_year,
        registered_capital=customer.registered_capital,
        company_size=customer.company_size,
        business_type=customer.business_type,
        main_ports=customer.main_ports,
        route_coverage=customer.route_coverage,
        cargo_specialization=customer.cargo_specialization,
        estimated_volume=customer.estimated_volume,
        country_code=customer.country_code,
        country=customer.country,
        city=customer.city,
        address=customer.address,
        phone=customer.phone,
        email=customer.email,
        whatsapp=customer.whatsapp,
        wechat=customer.wechat,
        linkedin_url=customer.linkedin_url,
        facebook_url=customer.facebook_url,
        status=customer.status,
        priority=customer.priority,
        assigned_to=str(customer.assigned_to) if customer.assigned_to else None,
        source=customer.source,
        source_url=customer.source_url,
        data_confidence=float(customer.data_confidence) if customer.data_confidence else None,
        last_verified_at=customer.last_verified_at,
        tags=customer.tags,
        notes=customer.notes,
        first_contact_date=customer.first_contact_date,
        cooperation_date=customer.cooperation_date,
        created_at=customer.created_at,
        updated_at=customer.updated_at,
    )
