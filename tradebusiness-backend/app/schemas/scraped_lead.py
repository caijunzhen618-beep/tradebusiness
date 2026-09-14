"""
采集线索相关的 Pydantic 模型
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class ScrapedLeadCreate(BaseModel):
    """创建采集线索的请求模型（内部使用）"""

    model_config = ConfigDict(from_attributes=True)

    raw_data: Dict[str, Any]
    data_source: str
    source_url: Optional[str] = None
    company_name: str
    company_name_en: Optional[str] = None
    country: str
    country_code: str
    city: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    whatsapp: Optional[str] = None
    website: Optional[str] = None
    business_type: Optional[str] = None
    description: Optional[str] = None
    confidence_score: int = 50
    scraping_task_id: str


class ScrapedLeadUpdate(BaseModel):
    """更新采集线索的请求模型"""

    model_config = ConfigDict(from_attributes=True)

    status: Optional[str] = None
    reviewed_by: Optional[str] = None
    rejection_reason: Optional[str] = None


class ScrapedLeadResponse(BaseModel):
    """采集线索响应模型"""

    model_config = ConfigDict(from_attributes=True)

    id: str
    raw_data: Dict[str, Any]
    data_source: str
    source_url: Optional[str]
    company_name: str
    company_name_en: Optional[str]
    country: str
    country_code: str
    city: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    whatsapp: Optional[str]
    website: Optional[str]
    business_type: Optional[str]
    description: Optional[str]
    confidence_score: int
    status: str
    reviewed_by: Optional[str]
    reviewed_at: Optional[datetime]
    rejection_reason: Optional[str]
    imported_to_customer_id: Optional[str]
    imported_at: Optional[datetime]
    scraping_task_id: str
    matched_by: Optional[str]
    duplicate_of: Optional[str]
    similarity_score: Optional[int]
    created_at: datetime
    updated_at: datetime


class ScrapedLeadListParams(BaseModel):
    """采集线索列表查询参数"""

    skip: int = Field(0, ge=0)
    limit: int = Field(20, ge=1, le=100)
    status: Optional[str] = None
    data_source: Optional[str] = None
    country_code: Optional[str] = None
    scraping_task_id: Optional[str] = None


class BulkApproveRequest(BaseModel):
    """批量审核请求"""

    lead_ids: List[str]
    approved: bool = True
    rejection_reason: Optional[str] = None


class BulkImportRequest(BaseModel):
    """批量导入请求"""

    lead_ids: List[str]


class DuplicateCheckResponse(BaseModel):
    """重复检测结果"""

    is_duplicate: bool
    duplicate_lead_id: Optional[str]
    similarity_score: Optional[int]
    existing_customer_id: Optional[str]
