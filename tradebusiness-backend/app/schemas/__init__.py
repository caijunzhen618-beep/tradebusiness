"""
Pydantic Schemas 模块
包含请求和响应的数据验证模式
"""

from app.schemas.common import ErrorDetail, ErrorResponse, MessageResponse, PaginatedResponse
from app.schemas.customer import (
    BusinessTypeEnum,
    CustomerBase,
    CustomerBatchImport,
    CustomerCreate,
    CustomerListParams,
    CustomerResponse,
    CustomerStatusEnum,
    CustomerUpdate,
)
from app.schemas.user import (
    LoginRequest,
    LoginResponse,
    TokenResponse,
    UserBase,
    UserCreate,
    UserInDB,
    UserResponse,
    UserUpdate,
)

__all__ = [
    # Common
    "ErrorDetail",
    "ErrorResponse",
    "MessageResponse",
    "PaginatedResponse",
    # User
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserInDB",
    "UserResponse",
    "LoginRequest",
    "LoginResponse",
    "TokenResponse",
    # Customer
    "CustomerBase",
    "CustomerCreate",
    "CustomerUpdate",
    "CustomerResponse",
    "CustomerListParams",
    "CustomerBatchImport",
    "BusinessTypeEnum",
    "CustomerStatusEnum",
]
