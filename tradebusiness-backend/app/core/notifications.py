"""
实时通知模块
使用 WebSocket 实现客户端与服务器之间的实时通信
"""

from datetime import datetime
from typing import Any, Dict, List

from fastapi import WebSocket, WebSocketDisconnect

from app.core.logger import get_logger

logger = get_logger(__name__)


class NotificationType:
    """通知类型"""

    NEW_EMAIL = "new_email"
    NEW_MESSAGE = "new_message"
    TASK_REMINDER = "task_reminder"
    FOLLOWUP_REMINDER = "followup"
    REPLY_RECEIVED = "reply"
    SYSTEM_ANNOUNCEMENT = "system"
    CUSTOMER_ASSIGNED = "customer_assigned"


class ConnectionManager:
    """
    WebSocket 连接管理器

    管理所有 WebSocket 连接，实现消息广播
    """

    def __init__(self):
        # 活跃的 WebSocket 连接 {user_id: {connection_id: websocket}}
        self.active_connections: Dict[str, Dict[str, WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: str, connection_id: str):
        """
        接受新的 WebSocket 连接

        Args:
            websocket: WebSocket 实例
            user_id: 用户 ID
            connection_id: 连接 ID（同一用户可能有多个连接）
        """
        await websocket.accept()

        if user_id not in self.active_connections:
            self.active_connections[user_id] = {}

        self.active_connections[user_id][connection_id] = websocket
        logger.info(f"WebSocket connected: user={user_id}, conn={connection_id}")

    def disconnect(self, user_id: str, connection_id: str):
        """
        断开 WebSocket 连接

        Args:
            user_id: 用户 ID
            connection_id: 连接 ID
        """
        if user_id in self.active_connections:
            self.active_connections[user_id].pop(connection_id, None)

            # 如果该用户没有其他连接，移除用户
            if not self.active_connections[user_id]:
                self.active_connections.pop(user_id, None)

        logger.info(f"WebSocket disconnected: user={user_id}, conn={connection_id}")

    async def send_to_user(
        self,
        user_id: str,
        message: Dict[str, Any],
        exclude_connection: str = None,
    ):
        """
        向指定用户的所有连接发送消息

        Args:
            user_id: 用户 ID
            message: 消息内容
            exclude_connection: 要排除的连接 ID
        """
        if user_id not in self.active_connections:
            return

        disconnected_connections = []

        for conn_id, connection in self.active_connections[user_id].items():
            if conn_id == exclude_connection:
                continue

            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Failed to send message to {user_id}:{conn_id}: {str(e)}")
                disconnected_connections.append(conn_id)

        # 清理断开的连接
        for conn_id in disconnected_connections:
            self.disconnect(user_id, conn_id)

    async def broadcast_to_all(self, message: Dict[str, Any]):
        """
        向所有连接的用户广播消息

        Args:
            message: 消息内容
        """
        for user_id in list(self.active_connections.keys()):
            await self.send_to_user(user_id, message)

    async def broadcast_to_users(
        self,
        user_ids: List[str],
        message: Dict[str, Any],
    ):
        """
        向指定用户列表广播消息

        Args:
            user_ids: 用户 ID 列表
            message: 消息内容
        """
        for user_id in user_ids:
            await self.send_to_user(user_id, message)

    def get_connected_users(self) -> List[str]:
        """
        获取当前连接的所有用户 ID

        Returns:
            用户 ID 列表
        """
        return list(self.active_connections.keys())

    def is_user_connected(self, user_id: str) -> bool:
        """
        检查用户是否在线

        Args:
            user_id: 用户 ID

        Returns:
            是否在线
        """
        return user_id in self.active_connections and len(self.active_connections[user_id]) > 0


# 全局连接管理器实例
manager = ConnectionManager()


async def notify_user(
    user_id: str,
    notification_type: str,
    title: str,
    message: str,
    data: Any = None,
):
    """
    向用户发送通知

    Args:
        user_id: 用户 ID
        notification_type: 通知类型
        title: 标题
        message: 消息内容
        data: 附加数据
    """
    notification = {
        "type": notification_type,
        "title": title,
        "message": message,
        "data": data,
        "timestamp": datetime.utcnow().isoformat(),
    }

    await manager.send_to_user(user_id, notification)
    logger.info(f"Notification sent to {user_id}: {title}")


async def notify_new_email(user_id: str, email_data: dict):
    """
    通知用户新邮件

    Args:
        user_id: 用户 ID
        email_data: 邮件数据
    """
    await notify_user(
        user_id=user_id,
        notification_type=NotificationType.NEW_EMAIL,
        title="新邮件",
        message=f"收到来自 {email_data.get('from_name', email_data.get('from_email'))} 的邮件",
        data=email_data,
    )


async def notify_customer_assigned(user_id: str, customer_data: dict):
    """
    通知用户新分配的客户

    Args:
        user_id: 用户 ID
        customer_data: 客户数据
    """
    await notify_user(
        user_id=user_id,
        notification_type=NotificationType.CUSTOMER_ASSIGNED,
        title="新客户分配",
        message=f"客户 {customer_data.get('company_name')} 已分配给您",
        data=customer_data,
    )


async def notify_task_reminder(user_id: str, task_data: dict):
    """
    通知用户任务提醒

    Args:
        user_id: 用户 ID
        task_data: 任务数据
    """
    await notify_user(
        user_id=user_id,
        notification_type=NotificationType.TASK_REMINDER,
        title="任务提醒",
        message=f"任务 '{task_data.get('title')}' 即将到期",
        data=task_data,
    )
