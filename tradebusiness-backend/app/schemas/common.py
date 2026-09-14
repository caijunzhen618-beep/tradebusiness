"""
通用 Pydantic Schemas
定义通用的请求和响应模式
"""

from typing import Any, Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class MessageResponse(BaseModel):
    """通用消息响应"""

    code: int = Field(200, description="状态码")
    message: str = Field(..., description="响应消息")
    data: Optional[Any] = Field(None, description="响应数据")


class ErrorDetail(BaseModel):
    """错误详情"""

    field: Optional[str] = Field(None, description="错误字段")
    message: str = Field(..., description="错误信息")


class ErrorResponse(BaseModel):
    """错误响应"""

    code: int = Field(..., description="错误码")
    message: str = Field(..., description="错误消息")
    errors: Optional[List[ErrorDetail]] = Field(None, description="详细错误列表")
    timestamp: str = Field(..., description="时间戳")


class PaginatedResponse(BaseModel, Generic[T]):
    """分页响应"""

    items: List[T] = Field(..., description="数据列表")
    total: int = Field(..., description="总数量")
    page: Optional[int] = Field(None, description="当前页码")
    page_size: Optional[int] = Field(None, description="每页数量")
    skip: Optional[int] = Field(None, description="跳过的记录数")
    limit: Optional[int] = Field(None, description="返回的记录数")
    pages: Optional[int] = Field(None, description="总页数")

    @classmethod
    def create(
        cls,
        items: List[T],
        total: int,
        page: int = None,
        page_size: int = None,
        skip: int = None,
        limit: int = None,
    ) -> "PaginatedResponse[T]":
        """
        创建分页响应

        支持两种分页格式:
        1. page/page_size (旧格式)
        2. skip/limit (新格式)

        Args:
            items: 数据列表
            total: 总数量
            page: 当前页码（旧格式）
            page_size: 每页数量（旧格式）
            skip: 跳过的记录数（新格式）
            limit: 返回的记录数（新格式）

        Returns:
            分页响应实例
        """
        # 处理新格式 (skip/limit)
        if skip is not None and limit is not None:
            return cls(
                items=items,
                total=total,
                skip=skip,
                limit=limit,
                page=None,
                page_size=None,
                pages=None,
            )

        # 处理旧格式 (page/page_size)
        if page is not None and page_size is not None:
            pages = (total + page_size - 1) // page_size if page_size > 0 else 0
            return cls(
                items=items,
                total=total,
                page=page,
                page_size=page_size,
                pages=pages,
                skip=None,
                limit=None,
            )

        # 如果都没有提供，尝试从数据推断
        if skip is None and limit is None:
            # 默认使用第一页，每页20条
            page = 1
            page_size = 20
            pages = (total + page_size - 1) // page_size if page_size > 0 else 0
            return cls(
                items=items,
                total=total,
                page=page,
                page_size=page_size,
                pages=pages,
                skip=None,
                limit=None,
            )

        raise ValueError("必须提供 page/page_size 或 skip/limit 参数")
