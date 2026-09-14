"""
AI 获客 Pydantic Schemas
定义获客任务、潜客、背调报告和开发信的请求与响应结构。
"""

from datetime import datetime
from typing import Any, Literal, Optional

from pydantic import BaseModel, EmailStr, Field, HttpUrl

from app.models.lead_generation import LeadStatus, LeadTaskStatus, SalesCopyChannel


class LeadSearchTaskBase(BaseModel):
    """获客任务基础 Schema。"""

    name: str = Field(..., min_length=1, max_length=200, description="任务名称")
    target_country: Optional[str] = Field(None, max_length=100, description="目标国家")
    target_industry: Optional[str] = Field(None, max_length=120, description="目标行业")
    product_keywords: list[str] = Field(default_factory=list, description="产品关键词")
    customer_profile: Optional[str] = Field(None, description="目标客户画像")
    exclude_keywords: list[str] = Field(default_factory=list, description="排除关键词")
    website_inputs: list[str] = Field(default_factory=list, description="手动输入的官网列表")


class LeadSearchTaskCreate(LeadSearchTaskBase):
    """创建获客任务 Schema。"""


class LeadSearchTaskResponse(LeadSearchTaskBase):
    """获客任务响应 Schema。"""

    id: str
    user_id: str
    status: LeadTaskStatus
    total_found: int
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class LeadBase(BaseModel):
    """潜客基础 Schema。"""

    company_name: str = Field(..., min_length=1, max_length=200, description="公司名称")
    website: Optional[HttpUrl | str] = Field(None, description="公司官网")
    country: Optional[str] = Field(None, max_length=100, description="国家")
    industry: Optional[str] = Field(None, max_length=120, description="行业")
    description: Optional[str] = Field(None, description="公司简介")
    source: Optional[str] = Field(None, max_length=100, description="来源")
    match_score: Optional[float] = Field(None, ge=0, le=100, description="匹配分")
    notes: Optional[str] = Field(None, description="备注")


class LeadCreate(LeadBase):
    """创建潜客 Schema。"""

    task_id: Optional[str] = Field(None, description="关联获客任务 ID")


class LeadUpdate(BaseModel):
    """更新潜客 Schema。"""

    company_name: Optional[str] = Field(None, min_length=1, max_length=200)
    website: Optional[HttpUrl | str] = None
    country: Optional[str] = Field(None, max_length=100)
    industry: Optional[str] = Field(None, max_length=120)
    description: Optional[str] = None
    source: Optional[str] = Field(None, max_length=100)
    match_score: Optional[float] = Field(None, ge=0, le=100)
    status: Optional[LeadStatus] = None
    do_not_contact: Optional[bool] = None
    do_not_contact_reason: Optional[str] = Field(None, max_length=300)
    notes: Optional[str] = None


class LeadResponse(LeadBase):
    """潜客响应 Schema。"""

    id: str
    task_id: Optional[str] = None
    user_id: str
    website: Optional[str] = None
    status: LeadStatus
    do_not_contact: bool = False
    do_not_contact_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class LeadContactCreate(BaseModel):
    """创建联系人 Schema。"""

    lead_id: str
    name: Optional[str] = Field(None, max_length=120)
    title: Optional[str] = Field(None, max_length=120)
    email: Optional[str] = Field(None, max_length=120)
    phone: Optional[str] = Field(None, max_length=60)
    linkedin_url: Optional[str] = Field(None, max_length=500)
    whatsapp: Optional[str] = Field(None, max_length=60)
    source: Optional[str] = Field(None, max_length=100)
    is_verified: bool = False


class LeadContactResponse(LeadContactCreate):
    """联系人响应 Schema。"""

    id: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CompanyResearchReportResponse(BaseModel):
    """企业背调报告响应 Schema。"""

    id: str
    lead_id: str
    summary: str
    business_model: Optional[str] = None
    products: Optional[str] = None
    target_markets: Optional[str] = None
    buying_signals: Optional[str] = None
    pain_points: Optional[str] = None
    recommended_angle: Optional[str] = None
    raw_sources: Optional[dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SalesCopyCreate(BaseModel):
    """生成开发信请求 Schema。"""

    channel: SalesCopyChannel = SalesCopyChannel.EMAIL
    language: str = Field("en", max_length=20, description="语言")
    tone: Optional[str] = Field("professional", max_length=50, description="语气")
    agent_id: Optional[str] = Field(None, description="销售智能体 ID")
    template_id: Optional[str] = Field(None, description="话术模板 ID")


class LeadEmailSendRequest(BaseModel):
    """人工确认后发送潜客开发信的请求。"""

    to_email: EmailStr
    to_name: Optional[str] = Field(None, max_length=120)
    subject: str = Field(..., min_length=1, max_length=300)
    body: str = Field(..., min_length=1, max_length=20000)


class LeadGenerationStatsResponse(BaseModel):
    """AI 获客统计响应。"""

    leads: int = 0
    sales_copies: int = 0
    followups: int = 0
    completed_followups: int = 0
    contacted: int = 0
    replied: int = 0
    reply_rate: float = 0.0
    channels: dict[str, int] = Field(default_factory=dict)
    countries: dict[str, int] = Field(default_factory=dict)
    industries: dict[str, int] = Field(default_factory=dict)
    statuses: dict[str, int] = Field(default_factory=dict)


class SalesCopyResponse(BaseModel):
    """开发信响应 Schema。"""

    id: str
    lead_id: str
    channel: SalesCopyChannel
    language: str
    subject: Optional[str] = None
    content: str
    tone: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class FollowupTaskCreate(BaseModel):
    lead_id: str
    channel: Literal["email", "whatsapp", "linkedin"] = "email"
    subject: Optional[str] = None
    content: str
    due_at: datetime


class FollowupTaskResponse(FollowupTaskCreate):
    id: str
    user_id: str
    status: Literal["pending", "completed", "failed", "cancelled"]
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}
