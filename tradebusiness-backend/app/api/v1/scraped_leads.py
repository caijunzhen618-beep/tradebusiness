"""
采集线索管理 API
提供采集线索的审核、导入等功能
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_admin_user, get_db
from app.models.user import User
from app.schemas.common import MessageResponse
from app.schemas.scraped_lead import (
    BulkApproveRequest,
    BulkImportRequest,
    DuplicateCheckResponse,
    ScrapedLeadResponse,
)
from app.services.scraped_lead_service import ScrapedLeadService

router = APIRouter()


def get_scraped_lead_service(
    db: AsyncSession = Depends(get_db),
) -> ScrapedLeadService:
    """
    获取采集线索服务实例。

    Args:
        db: 数据库会话。

    Returns:
        采集线索服务实例。
    """
    return ScrapedLeadService(db)


@router.get("", response_model=dict)
async def list_scraped_leads(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(20, ge=1, le=100, description="返回的记录数"),
    status: Optional[str] = Query(None, description="状态筛选"),
    data_source: Optional[str] = Query(None, description="数据源筛选"),
    country_code: Optional[str] = Query(None, description="国家代码筛选"),
    scraping_task_id: Optional[str] = Query(None, description="采集任务ID筛选"),
    stats: bool = Query(False, description="是否返回统计数据"),
    service: ScrapedLeadService = Depends(get_scraped_lead_service),
    _current_user: User = Depends(get_current_admin_user),
):
    """
    获取采集线索列表

    支持按状态、数据源、国家、任务ID筛选

    Args:
        skip: 分页偏移
        limit: 分页大小
        status: 状态筛选 (pending/approved/rejected/imported)
        data_source: 数据源筛选
        country_code: 国家代码筛选
        scraping_task_id: 采集任务ID筛选
        current_user: 当前用户
        db: 数据库会话

    Returns:
        线索列表
    """
    return await service.list_leads(
        skip=skip,
        limit=limit,
        status=status,
        data_source=data_source,
        country_code=country_code,
        scraping_task_id=scraping_task_id,
        include_stats=stats,
    )


@router.get("/statistics")
async def get_leads_statistics(
    service: ScrapedLeadService = Depends(get_scraped_lead_service),
    _current_user: User = Depends(get_current_admin_user),
):
    """
    获取采集线索统计信息

    Args:
        current_user: 当前用户
        db: 数据库会话

    Returns:
        统计数据
    """
    return await service.get_statistics()


@router.get("/overview")
async def get_leads_overview(
    service: ScrapedLeadService = Depends(get_scraped_lead_service),
    _current_user: User = Depends(get_current_admin_user),
):
    """
    获取采集线索统计概览

    Args:
        current_user: 当前用户
        db: 数据库会话

    Returns:
        统计数据
    """
    return await service.get_statistics()


@router.get("/{lead_id}", response_model=ScrapedLeadResponse)
async def get_scraped_lead(
    lead_id: str,
    service: ScrapedLeadService = Depends(get_scraped_lead_service),
    _current_user: User = Depends(get_current_admin_user),
):
    """
    获取采集线索详情

    Args:
        lead_id: 线索ID
        current_user: 当前用户
        db: 数据库会话

    Returns:
        线索详情
    """
    lead = await service.get_lead(lead_id)
    return lead.to_dict()


@router.post("/{lead_id}/approve", response_model=ScrapedLeadResponse)
async def approve_scraped_lead(
    lead_id: str,
    service: ScrapedLeadService = Depends(get_scraped_lead_service),
    current_user: User = Depends(get_current_admin_user),
):
    """
    审核通过采集线索

    Args:
        lead_id: 线索ID
        current_user: 当前用户
        db: 数据库会话

    Returns:
        更新后的线索
    """
    lead = await service.approve_lead(lead_id, str(current_user.id))
    return lead.to_dict()


@router.post("/{lead_id}/reject", response_model=ScrapedLeadResponse)
async def reject_scraped_lead(
    lead_id: str,
    reason: Optional[str] = Query(None, description="拒绝原因"),
    service: ScrapedLeadService = Depends(get_scraped_lead_service),
    current_user: User = Depends(get_current_admin_user),
):
    """
    拒绝采集线索

    Args:
        lead_id: 线索ID
        reason: 拒绝原因
        current_user: 当前用户
        db: 数据库会话

    Returns:
        更新后的线索
    """
    lead = await service.reject_lead(lead_id, str(current_user.id), reason)
    return lead.to_dict()


@router.post("/bulk-approve", response_model=dict)
async def bulk_approve_leads(
    request: BulkApproveRequest,
    service: ScrapedLeadService = Depends(get_scraped_lead_service),
    current_user: User = Depends(get_current_admin_user),
):
    """
    批量审核采集线索

    Args:
        request: 批量审核请求
        current_user: 当前用户
        db: 数据库会话

    Returns:
        审核结果统计
    """
    return await service.bulk_approve(request, str(current_user.id))


@router.post("/import", response_model=dict)
async def import_leads_to_customers(
    request: BulkImportRequest,
    service: ScrapedLeadService = Depends(get_scraped_lead_service),
    current_user: User = Depends(get_current_admin_user),
):
    """
    批量导入审核通过的线索到客户表

    Args:
        request: 批量导入请求
        current_user: 当前用户
        db: 数据库会话

    Returns:
        导入结果统计
    """
    return await service.import_leads(request, str(current_user.id))


@router.get("/{lead_id}/duplicate-check", response_model=DuplicateCheckResponse)
async def check_duplicate(
    lead_id: str,
    service: ScrapedLeadService = Depends(get_scraped_lead_service),
    _current_user: User = Depends(get_current_admin_user),
):
    """
    检查采集线索是否与现有客户重复

    Args:
        lead_id: 线索ID
        current_user: 当前用户
        db: 数据库会话

    Returns:
        重复检测结果
    """
    return await service.check_duplicate(lead_id)


@router.delete("/{lead_id}", response_model=MessageResponse)
async def delete_scraped_lead(
    lead_id: str,
    service: ScrapedLeadService = Depends(get_scraped_lead_service),
    current_user: User = Depends(get_current_admin_user),
):
    """
    删除采集线索

    仅可删除已拒绝或已导入的线索

    Args:
        lead_id: 线索ID
        current_user: 当前用户
        db: 数据库会话

    Returns:
        删除结果
    """
    await service.delete_lead(lead_id, str(current_user.id))
    return MessageResponse(message="Scraped lead deleted successfully")
