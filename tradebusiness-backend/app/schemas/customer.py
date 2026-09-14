"""
客户相关的 Pydantic Schemas
定义客户创建、更新、响应等数据结构
"""

from datetime import date, datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models.customer import BusinessType, CustomerStatus


class BusinessTypeEnum(str, Enum):
    """业务类型枚举"""

    SEA = "sea"
    AIR = "air"
    LAND = "land"
    MULTIMODAL = "multimodal"


class CustomerStatusEnum(str, Enum):
    """客户状态枚举"""

    POTENTIAL = "potential"
    CONTACTING = "contacting"
    COOPERATING = "cooperating"
    PAUSED = "paused"
    LOST = "lost"


class CustomerBase(BaseModel):
    """客户基础 Schema"""

    # 公司信息
    company_name: str = Field(..., min_length=2, max_length=200, description="公司名称")
    company_name_en: Optional[str] = Field(None, max_length=200, description="公司英文名")
    company_name_local: Optional[str] = Field(None, max_length=200, description="公司本地语言名称")
    website: Optional[str] = Field(None, max_length=200, description="公司网站")
    established_year: Optional[int] = Field(None, ge=1800, le=2100, description="成立年份")
    registered_capital: Optional[str] = Field(None, max_length=50, description="注册资本")
    company_size: Optional[int] = Field(None, ge=1, description="公司规模（员工数）")

    # 业务信息
    business_type: Optional[BusinessTypeEnum] = Field(None, description="业务类型")
    main_ports: Optional[List[str]] = Field(None, description="主要港口/机场")
    route_coverage: Optional[List[str]] = Field(None, description="航线覆盖")
    cargo_specialization: Optional[List[str]] = Field(None, description="货物类型专长")
    estimated_volume: Optional[int] = Field(None, ge=0, description="年货量估算")

    # 联系信息
    country_code: str = Field(..., min_length=2, max_length=3, description="国家代码")
    country: str = Field(..., min_length=2, max_length=100, description="国家")
    city: Optional[str] = Field(None, max_length=100, description="城市")
    address: Optional[str] = Field(None, description="地址")
    phone: Optional[str] = Field(None, max_length=50, description="电话")
    email: Optional[EmailStr] = Field(None, description="邮箱")
    whatsapp: Optional[str] = Field(None, max_length=50, description="WhatsApp")
    wechat: Optional[str] = Field(None, max_length=50, description="微信")
    linkedin_url: Optional[str] = Field(None, max_length=200, description="LinkedIn")
    facebook_url: Optional[str] = Field(None, max_length=200, description="Facebook")

    @field_validator("company_name")
    @classmethod
    def validate_company_name(cls, v: str) -> str:
        """验证公司名称"""
        return v.strip()

    @field_validator("country")
    @classmethod
    def validate_country(cls, v: str) -> str:
        """验证国家名称"""
        return v.strip()

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        """验证邮箱格式"""
        if v:
            return v.lower().strip()
        return v


class CustomerCreate(CustomerBase):
    """创建客户 Schema"""

    status: CustomerStatusEnum = Field(default=CustomerStatusEnum.POTENTIAL, description="客户状态")
    priority: int = Field(default=3, ge=1, le=5, description="优先级（1-5，1最高）")
    assigned_to: Optional[str] = Field(None, description="分配给的用户ID")
    source: Optional[str] = Field(None, max_length=100, description="数据来源")
    source_url: Optional[str] = Field(None, max_length=500, description="来源URL")
    tags: Optional[List[str]] = Field(None, description="标签")
    notes: Optional[str] = Field(None, description="备注")


class CustomerUpdate(BaseModel):
    """更新客户 Schema（所有字段可选）"""

    company_name: Optional[str] = Field(None, min_length=2, max_length=200)
    company_name_en: Optional[str] = Field(None, max_length=200)
    company_name_local: Optional[str] = Field(None, max_length=200)
    logo_url: Optional[str] = Field(None, max_length=500)
    website: Optional[str] = Field(None, max_length=200)
    established_year: Optional[int] = Field(None, ge=1800, le=2100)
    registered_capital: Optional[str] = Field(None, max_length=50)
    company_size: Optional[int] = Field(None, ge=1)

    business_type: Optional[BusinessTypeEnum] = None
    main_ports: Optional[List[str]] = None
    route_coverage: Optional[List[str]] = None
    cargo_specialization: Optional[List[str]] = None
    estimated_volume: Optional[int] = Field(None, ge=0)

    country_code: Optional[str] = Field(None, min_length=2, max_length=3)
    country: Optional[str] = Field(None, min_length=2, max_length=100)
    city: Optional[str] = Field(None, max_length=100)
    address: Optional[str] = None
    phone: Optional[str] = Field(None, max_length=50)
    email: Optional[EmailStr] = None
    whatsapp: Optional[str] = Field(None, max_length=50)
    wechat: Optional[str] = Field(None, max_length=50)
    linkedin_url: Optional[str] = Field(None, max_length=200)
    facebook_url: Optional[str] = Field(None, max_length=200)

    status: Optional[CustomerStatusEnum] = None
    priority: Optional[int] = Field(None, ge=1, le=5)
    assigned_to: Optional[str] = None
    source: Optional[str] = Field(None, max_length=100)
    source_url: Optional[str] = Field(None, max_length=500)
    tags: Optional[List[str]] = None
    notes: Optional[str] = None
    first_contact_date: Optional[date] = None
    cooperation_date: Optional[date] = None


class CustomerResponse(CustomerBase):
    """客户响应 Schema"""

    model_config = ConfigDict(from_attributes=True)

    id: str
    logo_url: Optional[str] = None
    status: CustomerStatusEnum
    priority: int
    assigned_to: Optional[str] = None
    source: Optional[str] = None
    source_url: Optional[str] = None
    data_confidence: Optional[float] = None
    last_verified_at: Optional[datetime] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None
    first_contact_date: Optional[date] = None
    cooperation_date: Optional[date] = None
    created_at: datetime
    updated_at: datetime


class CustomerListParams(BaseModel):
    """客户列表查询参数"""

    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(20, ge=1, le=100, description="每页数量")
    country: Optional[str] = Field(None, description="国家筛选")
    status: Optional[CustomerStatusEnum] = Field(None, description="状态筛选")
    business_type: Optional[BusinessTypeEnum] = Field(None, description="业务类型筛选")
    assigned_to: Optional[str] = Field(None, description="分配给的用户ID")
    search: Optional[str] = Field(None, description="搜索关键词（公司名、邮箱）")
    priority: Optional[int] = Field(None, ge=1, le=5, description="优先级筛选")
    tags: Optional[List[str]] = Field(None, description="标签筛选")
    sort_by: Optional[str] = Field("created_at", description="排序字段")
    sort_order: Optional[str] = Field("desc", description="排序方向（asc/desc）")


class CustomerBatchImport(BaseModel):
    """客户批量导入 Schema"""

    customers: List[CustomerCreate] = Field(
        ..., max_length=1000, description="客户列表（最多1000条）"
    )
    overwrite: bool = Field(False, description="是否覆盖已存在的客户（基于邮箱）")
