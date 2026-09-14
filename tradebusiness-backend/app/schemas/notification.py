"""
通知相关的 Pydantic 模型
用于通知的数据验证和序列化
"""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class NotificationType(str):
    """通知类型"""

    NEW_EMAIL = "new_email"
    NEW_MESSAGE = "new_message"
    TASK_REMINDER = "task_reminder"
    FOLLOWUP_REMINDER = "followup"
    REPLY_RECEIVED = "reply"
    SYSTEM_ANNOUNCEMENT = "system"


class NotificationBase(BaseModel):
    """通知基础模型"""

    type: str = Field(..., description="通知类型")
    title: str = Field(..., min_length=1, max_length=200, description="通知标题")
    message: str = Field(..., description="通知内容")
    data: Optional[dict] = Field(None, description="额外数据")


class NotificationCreate(NotificationBase):
    """创建通知Schema"""

    user_id: str = Field(..., description="接收用户ID")
    is_read: bool = Field(False, description="是否已读")


class NotificationUpdate(BaseModel):
    """更新通知Schema"""

    is_read: Optional[bool] = None


class NotificationResponse(NotificationBase):
    """通知响应Schema"""

    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    is_read: bool
    created_at: datetime
    read_at: Optional[datetime] = None


class WebSocketMessage(BaseModel):
    """WebSocket消息格式"""

    type: str = Field(..., description="消息类型")
    data: Any = Field(None, description="消息数据")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
