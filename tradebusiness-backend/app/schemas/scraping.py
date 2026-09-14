"""
数据采集相关的 Pydantic 模型
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_serializer


class ScrapingTaskCreate(BaseModel):
    """创建采集任务的请求模型"""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "测试任务",
                "task_type": "google",
                "keywords": ["物流", "货运"],
                "countries": ["NG", "KE"],
                "source_urls": ["https://example-directory.com/logistics"],
                "config": {
                    "max_concurrent": 5,
                    "delay_min": 2,
                    "delay_max": 5,
                },
            }
        }
    )

    name: str = Field(..., min_length=1, max_length=200, description="任务名称")
    task_type: str = Field(
        ..., description="任务类型：google, kompass, yellow_pages, port_authorities"
    )
    keywords: List[str] = Field(default_factory=list, description="关键词列表")
    countries: List[str] = Field(default_factory=list, description="国家代码列表")
    source_urls: List[str] = Field(default_factory=list, description="采集数据来源地址列表")
    config: Dict[str, Any] = Field(default_factory=dict, description="任务配置")


class ScrapingTaskResponse(BaseModel):
    """采集任务响应模型"""

    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    task_type: str
    status: str
    config: Dict[str, Any]
    keywords: List[str]
    countries: List[str]
    source_urls: List[str] = Field(default_factory=list)
    progress_current: int = 0
    progress_total: int = 0
    total_found: int = 0
    total_saved: int = 0
    status_message: Optional[str] = None
    error_message: Optional[str] = None
    last_run_summary: Optional[Dict[str, Any]] = None
    execution_log: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    @field_serializer("created_at", "updated_at", "started_at", "completed_at")
    def serialize_datetime(self, dt: Optional[datetime]) -> Optional[str]:
        """序列化datetime为ISO格式字符串"""
        if dt is None:
            return None
        return dt.isoformat()
