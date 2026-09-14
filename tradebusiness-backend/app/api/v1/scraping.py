"""
数据采集 API
管理爬虫任务的创建和监控
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_admin_user, get_db
from app.models.user import User
from app.schemas.common import MessageResponse
from app.schemas.scraping import ScrapingTaskCreate, ScrapingTaskResponse
from app.scrapers.task_manager import ScrapingTaskManager

router = APIRouter()


@router.post(
    "/tasks",
    response_model=ScrapingTaskResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_scraping_task(
    task_data: ScrapingTaskCreate,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    创建爬虫任务

    需要管理员权限。

    Args:
        task_data: 任务创建数据
        current_user: 当前用户
        db: 数据库会话

    Returns:
        创建的任务信息
    """
    task_manager = ScrapingTaskManager(db)

    task = await task_manager.create_task(
        name=task_data.name,
        task_type=task_data.task_type,
        config=task_data.config,
        keywords=task_data.keywords,
        countries=task_data.countries,
        source_urls=task_data.source_urls,
        created_by=current_user.id,
    )

    return task


@router.get("/tasks")
async def list_scraping_tasks(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(20, ge=1, le=100, description="返回的记录数"),
    status: Optional[str] = Query(None, description="状态筛选"),
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取爬虫任务列表

    需要管理员权限。

    Args:
        skip: 分页偏移
        limit: 分页大小
        status: 状态筛选
        current_user: 当前用户
        db: 数据库会话

    Returns:
        任务列表
    """
    task_manager = ScrapingTaskManager(db)

    tasks, total = await task_manager.list_tasks(skip=skip, limit=limit, status=status)

    return {
        "items": tasks,
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.get("/tasks/{task_id}")
async def get_scraping_task(
    task_id: str,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取爬虫任务详情

    Args:
        task_id: 任务ID
        current_user: 当前用户
        db: 数据库会话

    Returns:
        任务详情
    """
    task_manager = ScrapingTaskManager(db)

    task = await task_manager.get_task(task_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    return task


@router.post("/tasks/{task_id}/start")
async def start_scraping_task(
    task_id: str,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    启动爬虫任务

    Args:
        task_id: 任务ID
        current_user: 当前用户
        db: 数据库会话

    Returns:
        启动结果
    """
    task_manager = ScrapingTaskManager(db)

    try:
        await task_manager.start_task(task_id)
        return {
            "message": f"Task {task_id} started successfully",
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/tasks/{task_id}/cancel")
async def cancel_scraping_task(
    task_id: str,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    取消爬虫任务

    Args:
        task_id: 任务ID
        current_user: 当前用户
        db: 数据库会话

    Returns:
        取消结果
    """
    task_manager = ScrapingTaskManager(db)

    await task_manager.cancel_task(task_id)

    return {
        "message": f"Task {task_id} cancelled successfully",
    }


@router.delete("/tasks/{task_id}", response_model=MessageResponse)
async def delete_scraping_task(
    task_id: str,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    删除爬虫任务

    Args:
        task_id: 任务ID
        current_user: 当前用户
        db: 数据库会话

    Returns:
        删除结果
    """
    task_manager = ScrapingTaskManager(db)

    try:
        await task_manager.delete_task(task_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    return MessageResponse(message=f"Task {task_id} deleted successfully")


@router.get("/sources")
async def get_scraping_sources():
    """
    获取可用的数据源列表

    Returns:
        数据源列表
    """
    sources = {
        "google": {
            "name": "Google搜索",
            "description": "通过Google搜索发现货运公司",
            "type": "search",
            "supported_countries": ["all"],
            "config_schema": {
                "keywords": "array of strings",
                "max_results": "integer (default: 100)",
            },
        },
        "kompass": {
            "name": "Kompass 商业目录",
            "description": "非洲商业目录",
            "type": "directory",
            "supported_countries": [
                "Nigeria",
                "South Africa",
                "Kenya",
                "Egypt",
                "Morocco",
                "Ghana",
                "Ethiopia",
                "Tanzania",
                "Ivory Coast",
                "Senegal",
            ],
            "config_schema": {
                "country": "string",
                "category": "string (optional)",
            },
        },
        "yellow_pages": {
            "name": "Yellow Pages",
            "description": "非洲黄页目录",
            "type": "directory",
            "supported_countries": [
                "Nigeria",
                "South Africa",
                "Kenya",
                "Egypt",
            ],
            "config_schema": {
                "country": "string",
                "category": "string (optional)",
            },
        },
        "port_authorities": {
            "name": "港口官网",
            "description": "从港口官方网站获取注册公司信息",
            "type": "specific_site",
            "supported_countries": [
                "Nigeria",
                "South Africa",
                "Kenya",
                "Egypt",
                "Morocco",
                "Ivory Coast",
                "Senegal",
                "Djibouti",
            ],
            "config_schema": {
                "port_code": "string",
            },
        },
    }

    return sources


@router.post("/test-proxy")
async def test_proxy(
    proxy_url: str,
    current_user: User = Depends(get_current_admin_user),
):
    """
    测试代理连接

    Args:
        proxy_url: 代理URL
        current_user: 当前用户

    Returns:
        测试结果
    """
    import asyncio

    import aiohttp

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://httpbin.org/ip",
                proxy=proxy_url,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as response:
                data = await response.json()

                return {
                    "success": True,
                    "proxy_ip": data.get("origin"),
                    "message": "Proxy is working",
                }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Proxy test failed",
        }
