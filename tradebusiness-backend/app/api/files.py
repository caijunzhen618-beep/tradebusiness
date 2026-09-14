"""
文件上传 API 路由
处理文件上传、删除等操作
"""

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.services.file_service import FileService

router = APIRouter()


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    subfolder: str = "general",
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    上传文件

    - **file**: 上传的文件
    - **subfolder**: 子文件夹名称（可选）
    """
    file_service = FileService(db)
    try:
        result = await file_service.upload_file(file, subfolder=subfolder)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload/logo")
async def upload_logo(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    上传Logo图片

    - **file**: 图片文件（jpg, jpeg, png, gif, svg）
    - 最大: 5MB
    """
    file_service = FileService(db)
    try:
        result = await file_service.upload_logo(file)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload/attachment")
async def upload_attachment(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    上传邮件附件

    - **file**: 附件文件
    - 最大: 20MB
    """
    file_service = FileService(db)
    try:
        result = await file_service.upload_attachment(file)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload/import")
async def upload_import_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    上传批量导入文件

    - **file**: 导入文件（csv, xlsx, xls）
    - 最大: 50MB
    """
    file_service = FileService(db)
    try:
        result = await file_service.upload_import_file(file)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/files/{file_path:path}")
async def delete_file(
    file_path: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    删除文件

    - **file_path**: 文件相对路径
    """
    file_service = FileService(db)
    success = await file_service.delete_file(file_path)

    if not success:
        raise HTTPException(status_code=404, detail="File not found")

    return {"message": "File deleted successfully"}
