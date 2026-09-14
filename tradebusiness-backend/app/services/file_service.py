"""
文件上传服务
处理文件上传、存储和管理
"""

import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)


class FileService:
    """文件服务"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    async def upload_file(
        self,
        file: UploadFile,
        subfolder: str = "general",
        max_size: int = 10 * 1024 * 1024,  # 10MB
        allowed_extensions: Optional[list[str]] = None,
    ) -> dict:
        """
        上传文件

        Args:
            file: 上传的文件
            subfolder: 子文件夹名称
            max_size: 最大文件大小（字节）
            allowed_extensions: 允许的文件扩展名列表

        Returns:
            文件信息字典
        """
        # 验证文件
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")

        # 检查文件大小
        file.file.seek(0, 2)  # 移动到文件末尾
        file_size = file.file.tell()
        file.file.seek(0)  # 重置到文件开头

        if file_size > max_size:
            raise HTTPException(
                status_code=400,
                detail=f"File size exceeds maximum allowed size of {max_size} bytes",
            )

        # 检查文件扩展名
        file_ext = Path(file.filename).suffix.lower()
        if allowed_extensions and file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"File extension {file_ext} is not allowed. Allowed: {allowed_extensions}",
            )

        # 生成唯一文件名
        unique_filename = f"{uuid.uuid4()}{file_ext}"

        # 创建子文件夹
        safe_subfolder = self._sanitize_subfolder(subfolder)
        target_dir = self.upload_dir / safe_subfolder
        target_dir.mkdir(parents=True, exist_ok=True)

        # 保存文件
        file_path = target_dir / unique_filename

        try:
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)

            logger.info(f"File uploaded: {file_path}")

            return {
                "filename": file.filename,
                "unique_filename": unique_filename,
                "path": str(file_path.relative_to(self.upload_dir)),
                "url": f"/uploads/{safe_subfolder}/{unique_filename}",
                "size": file_size,
                "content_type": file.content_type,
                "uploaded_at": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Failed to upload file: {e}")
            # 删除部分上传的文件
            if file_path.exists():
                file_path.unlink()
            raise HTTPException(status_code=500, detail="Failed to upload file")

    async def upload_logo(
        self,
        file: UploadFile,
    ) -> dict:
        """
        上传Logo图片

        Args:
            file: 上传的图片文件

        Returns:
            文件信息字典
        """
        allowed_extensions = [".jpg", ".jpeg", ".png", ".gif", ".svg"]
        max_size = 5 * 1024 * 1024  # 5MB

        return await self.upload_file(
            file=file,
            subfolder="logos",
            max_size=max_size,
            allowed_extensions=allowed_extensions,
        )

    async def upload_attachment(
        self,
        file: UploadFile,
    ) -> dict:
        """
        上传邮件附件

        Args:
            file: 上传的文件

        Returns:
            文件信息字典
        """
        # 允许常见文档类型
        allowed_extensions = [
            ".pdf",
            ".doc",
            ".docx",
            ".xls",
            ".xlsx",
            ".ppt",
            ".pptx",
            ".jpg",
            ".jpeg",
            ".png",
            ".zip",
            ".rar",
        ]
        max_size = 20 * 1024 * 1024  # 20MB

        return await self.upload_file(
            file=file,
            subfolder="attachments",
            max_size=max_size,
            allowed_extensions=allowed_extensions,
        )

    async def upload_import_file(
        self,
        file: UploadFile,
    ) -> dict:
        """
        上传批量导入文件

        Args:
            file: 上传的文件

        Returns:
            文件信息字典
        """
        allowed_extensions = [".csv", ".xlsx", ".xls"]
        max_size = 50 * 1024 * 1024  # 50MB

        return await self.upload_file(
            file=file,
            subfolder="imports",
            max_size=max_size,
            allowed_extensions=allowed_extensions,
        )

    async def delete_file(self, file_path: str) -> bool:
        """
        删除文件

        Args:
            file_path: 文件相对路径

        Returns:
            是否删除成功
        """
        try:
            full_path = self._resolve_upload_path(file_path)

            if full_path.exists() and full_path.is_file():
                full_path.unlink()
                logger.info(f"File deleted: {full_path}")
                return True

            return False

        except Exception as e:
            logger.error(f"Failed to delete file: {e}")
            return False

    def _sanitize_subfolder(self, subfolder: str) -> str:
        """
        校验上传子目录，防止写入上传根目录以外的位置。

        Args:
            subfolder: 请求传入的子目录。

        Returns:
            规范化后的安全子目录。
        """
        normalized = Path(subfolder)
        if normalized.is_absolute() or ".." in normalized.parts:
            raise HTTPException(status_code=400, detail="Invalid upload subfolder")
        return normalized.as_posix().strip("/") or "general"

    def _resolve_upload_path(self, file_path: str) -> Path:
        """
        将相对路径解析为上传目录内的绝对路径。

        Args:
            file_path: 文件相对路径。

        Returns:
            上传目录内的绝对路径。

        Raises:
            HTTPException: 路径越界时抛出。
        """
        upload_root = self.upload_dir.resolve()
        resolved_path = (self.upload_dir / file_path).resolve()
        if upload_root != resolved_path and upload_root not in resolved_path.parents:
            raise HTTPException(status_code=400, detail="Invalid file path")
        return resolved_path

    def get_file_url(self, file_path: str) -> str:
        """
        获取文件访问URL

        Args:
            file_path: 文件相对路径

        Returns:
            文件URL
        """
        return f"/uploads/{file_path}"

    async def cleanup_old_files(
        self,
        days: int = 30,
        subfolder: Optional[str] = None,
    ) -> int:
        """
        清理旧文件

        Args:
            days: 文件年龄（天）
            subfolder: 子文件夹（可选）

        Returns:
            删除的文件数量
        """
        try:
            import time

            cutoff_time = time.time() - (days * 24 * 60 * 60)
            deleted_count = 0

            search_dir = self.upload_dir / subfolder if subfolder else self.upload_dir

            for file_path in search_dir.rglob("*"):
                if file_path.is_file():
                    file_mtime = file_path.stat().st_mtime
                    if file_mtime < cutoff_time:
                        file_path.unlink()
                        deleted_count += 1
                        logger.info(f"Deleted old file: {file_path}")

            return deleted_count

        except Exception as e:
            logger.error(f"Failed to cleanup old files: {e}")
            return 0
