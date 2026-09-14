"""
任务相关的 Pydantic 模型
用于请求和响应的数据验证
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class TaskBase(BaseModel):
    """任务基础模型"""

    title: str = Field(..., min_length=1, max_length=200, description="任务标题")
    description: Optional[str] = Field(None, description="任务描述")
    type: Optional[str] = Field(None, description="任务类型")
    priority: str = Field("medium", description="优先级")
    due_date: Optional[datetime] = Field(None, description="截止日期")
    reminder_at: Optional[datetime] = Field(None, description="提醒时间")


class TaskCreate(TaskBase):
    """创建任务Schema"""

    assigned_to: str = Field(..., description="分配给的用户ID")
    customer_id: Optional[str] = Field(None, description="关联客户ID")


class TaskUpdate(BaseModel):
    """更新任务Schema"""

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    type: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[datetime] = None
    reminder_at: Optional[datetime] = None
    assigned_to: Optional[str] = None


class TaskResponse(BaseModel):
    """任务响应Schema"""

    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    description: Optional[str]
    type: Optional[str]
    status: str
    priority: str
    customer_id: Optional[str]
    assigned_to: Optional[str]
    created_by: Optional[str]
    due_date: Optional[datetime]
    completed_at: Optional[datetime]
    reminder_at: Optional[datetime]
    is_reminded: bool
    created_at: datetime
    updated_at: datetime


class TaskListParams(BaseModel):
    """任务列表查询参数"""

    status: Optional[str] = None
    priority: Optional[str] = None
    customer_id: Optional[str] = None
