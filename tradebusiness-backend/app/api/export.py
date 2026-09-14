"""数据导出 API 路由。"""

from datetime import datetime

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.services.export_service import ExportService

router = APIRouter()


@router.get("/export/customers")
async def export_customers(
    format: str = Query("xlsx", description="导出格式: xlsx 或 csv"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    导出客户数据

    - **format**: 导出格式 (xlsx, csv)
    - 返回文件下载
    """
    export_service = ExportService(db)

    try:
        data = await export_service.export_customers(format=format)

        filename = f"customers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format}"

        media_type = (
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            if format == "xlsx"
            else "text/csv"
        )

        return Response(
            content=data,
            media_type=media_type,
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )

    except Exception as e:
        return Response(content=f"导出失败: {str(e)}", status_code=500, media_type="text/plain")


@router.get("/export/emails")
async def export_emails(
    format: str = Query("xlsx", description="导出格式: xlsx 或 csv"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    导出邮件数据

    - **format**: 导出格式 (xlsx, csv)
    - 返回文件下载
    """
    export_service = ExportService(db)

    try:
        data = await export_service.export_emails(format=format)

        filename = f"emails_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format}"

        media_type = (
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            if format == "xlsx"
            else "text/csv"
        )

        return Response(
            content=data,
            media_type=media_type,
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )

    except Exception as e:
        return Response(content=f"导出失败: {str(e)}", status_code=500, media_type="text/plain")


@router.get("/export/stats")
async def export_stats(
    format: str = Query("xlsx", description="导出格式: xlsx 或 csv"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    导出客户统计报表

    - **format**: 导出格式 (xlsx, csv)
    - 返回文件下载
    """
    export_service = ExportService(db)

    try:
        data = await export_service.export_customer_stats(format=format)

        filename = f"customer_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format}"

        media_type = (
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            if format == "xlsx"
            else "text/csv"
        )

        return Response(
            content=data,
            media_type=media_type,
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )

    except Exception as e:
        return Response(content=f"导出失败: {str(e)}", status_code=500, media_type="text/plain")
