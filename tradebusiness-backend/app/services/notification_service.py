"""
通知服务
处理通知相关的业务逻辑和WebSocket推送
"""

import json
from datetime import datetime
from typing import List, Optional

from sqlalchemy import and_, delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger import get_logger
from app.models.base import UUIDMixin
from app.models.notification import Notification
from app.schemas.notification import NotificationCreate

logger = get_logger(__name__)


# WebSocket连接管理器
class ConnectionManager:
    """WebSocket连接管理器"""

    def __init__(self):
        # 存储用户的WebSocket连接: {user_id: [websocket1, websocket2, ...]}
        self.active_connections: dict[str, list] = {}

    async def connect(self, user_id: str, websocket):
        """
        建立WebSocket连接

        Args:
            user_id: 用户ID
            websocket: WebSocket连接对象
        """
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
        logger.info(
            f"WebSocket connected: user_id={user_id}, total_connections={len(self.active_connections[user_id])}"
        )

    def disconnect(self, user_id: str, websocket):
        """
        断开WebSocket连接

        Args:
            user_id: 用户ID
            websocket: WebSocket连接对象
        """
        if user_id in self.active_connections:
            try:
                self.active_connections[user_id].remove(websocket)
                logger.info(f"WebSocket disconnected: user_id={user_id}")

                # 如果该用户没有其他连接了，删除用户条目
                if not self.active_connections[user_id]:
                    del self.active_connections[user_id]
            except ValueError:
                pass

    async def send_personal_message(self, message: dict, user_id: str):
        """
        发送消息给指定用户

        Args:
            message: 消息内容
            user_id: 用户ID
        """
        if user_id in self.active_connections:
            # 给该用户的所有连接发送消息
            disconnected = []
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Failed to send message to user {user_id}: {e}")
                    disconnected.append(connection)

            # 清理断开的连接
            for conn in disconnected:
                self.disconnect(user_id, conn)
        else:
            logger.warning(f"No active connection for user {user_id}")

    async def broadcast(self, message: dict):
        """
        广播消息给所有连接的用户

        Args:
            message: 消息内容
        """
        for user_id, connections in self.active_connections.items():
            for connection in connections:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Failed to broadcast to user {user_id}: {e}")

    def get_online_users(self) -> list[str]:
        """
        获取在线用户列表

        Returns:
            在线用户ID列表
        """
        return list(self.active_connections.keys())


# 全局连接管理器实例
manager = ConnectionManager()


class NotificationService:
    """通知服务"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_notification(
        self,
        user_id: str,
        type: str,
        title: str,
        message: str,
        data: Optional[dict] = None,
        expires_at: Optional[datetime] = None,
    ) -> Notification:
        """
        创建通知

        Args:
            user_id: 接收用户ID
            type: 通知类型
            title: 通知标题
            message: 通知内容
            data: 额外数据
            expires_at: 过期时间

        Returns:
            创建的通知对象
        """
        notification = Notification(
            user_id=user_id,
            type=type,
            title=title,
            message=message,
            data=data,
            expires_at=expires_at,
            is_read=False,
        )

        self.session.add(notification)
        await self.session.flush()

        logger.info(f"Notification created: id={notification.id}, user_id={user_id}, type={type}")

        # 通过WebSocket实时推送
        await manager.send_personal_message(
            {
                "type": "notification",
                "data": {
                    "id": str(notification.id),
                    "type": notification.type,
                    "title": notification.title,
                    "message": notification.message,
                    "data": notification.data,
                    "created_at": notification.created_at.isoformat(),
                },
            },
            user_id,
        )

        return notification

    async def get_user_notifications(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 20,
        unread_only: bool = False,
    ) -> tuple[List[Notification], int]:
        """
        获取用户的通知列表

        Args:
            user_id: 用户ID
            skip: 跳过记录数
            limit: 返回记录数
            unread_only: 是否只获取未读通知

        Returns:
            (通知列表, 总数)
        """
        from sqlalchemy import func

        # 构建查询条件
        conditions = [Notification.user_id == user_id]

        if unread_only:
            conditions.append(Notification.is_read == False)

        # 获取总数
        count_stmt = select(func.count(Notification.id)).where(and_(*conditions))
        count_result = await self.session.execute(count_stmt)
        total = count_result.scalar() or 0

        # 获取分页数据
        stmt = (
            select(Notification)
            .where(and_(*conditions))
            .order_by(Notification.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        notifications = result.scalars().all()

        return list(notifications), total

    async def mark_as_read(self, notification_id: str, user_id: str) -> Notification:
        """
        标记通知为已读

        Args:
            notification_id: 通知ID
            user_id: 用户ID

        Returns:
            更新后的通知对象
        """
        stmt = select(Notification).where(
            and_(Notification.id == notification_id, Notification.user_id == user_id)
        )
        result = await self.session.execute(stmt)
        notification = result.scalar_one_or_none()

        if notification and not notification.is_read:
            notification.is_read = True
            notification.read_at = datetime.utcnow()
            await self.session.flush()

        return notification

    async def mark_all_as_read(self, user_id: str) -> int:
        """
        标记用户所有通知为已读

        Args:
            user_id: 用户ID

        Returns:
            更新的记录数
        """

        stmt = (
            update(Notification)
            .where(and_(Notification.user_id == user_id, Notification.is_read == False))
            .values(is_read=True, read_at=datetime.utcnow())
        )

        result = await self.session.execute(stmt)
        await self.session.flush()

        return result.rowcount

    async def delete_notification(self, notification_id: str, user_id: str) -> None:
        """
        删除通知

        Args:
            notification_id: 通知ID
            user_id: 用户ID
        """
        stmt = select(Notification).where(
            and_(Notification.id == notification_id, Notification.user_id == user_id)
        )
        result = await self.session.execute(stmt)
        notification = result.scalar_one_or_none()

        if notification:
            await self.session.delete(notification)
            await self.session.flush()

    async def delete_read_notifications(self, user_id: str) -> int:
        """
        删除用户所有已读通知。

        Args:
            user_id: 用户ID

        Returns:
            删除的通知数量
        """
        stmt = delete(Notification).where(
            and_(Notification.user_id == user_id, Notification.is_read == True)
        )
        result = await self.session.execute(stmt)
        await self.session.flush()

        return result.rowcount or 0

    async def get_unread_count(self, user_id: str) -> int:
        """
        获取用户未读通知数量

        Args:
            user_id: 用户ID

        Returns:
            未读通知数量
        """

        stmt = select(func.count(Notification.id)).where(
            and_(Notification.user_id == user_id, Notification.is_read == False)
        )
        result = await self.session.execute(stmt)
        return result.scalar() or 0

    async def cleanup_expired_notifications(self) -> int:
        """
        清理过期的通知

        Returns:
            删除的记录数
        """

        now = datetime.utcnow()
        stmt = delete(Notification).where(Notification.expires_at < now)
        result = await self.session.execute(stmt)

        deleted_count = result.rowcount
        logger.info(f"Cleaned up {deleted_count} expired notifications")

        return deleted_count

    # ========== 便捷方法：创建各类通知 ==========

    async def notify_new_email(
        self,
        user_id: str,
        email_subject: str,
        sender_name: str,
        email_id: str,
    ):
        """
        创建新邮件通知

        Args:
            user_id: 用户ID
            email_subject: 邮件主题
            sender_name: 发送者名称
            email_id: 邮件ID
        """
        await self.create_notification(
            user_id=user_id,
            type="new_email",
            title="收到新邮件",
            message=f"{sender_name} 发来邮件：{email_subject}",
            data={
                "email_id": email_id,
                "subject": email_subject,
                "sender": sender_name,
            },
        )

    async def notify_task_reminder(
        self,
        user_id: str,
        task_title: str,
        task_id: str,
        due_date: datetime,
    ):
        """
        创建任务提醒通知

        Args:
            user_id: 用户ID
            task_title: 任务标题
            task_id: 任务ID
            due_date: 截止日期
        """
        await self.create_notification(
            user_id=user_id,
            type="task_reminder",
            title="任务提醒",
            message=f"任务 '{task_title}' 将于 {due_date.strftime('%Y-%m-%d %H:%M')} 到期",
            data={
                "task_id": task_id,
                "title": task_title,
                "due_date": due_date.isoformat(),
            },
        )

    async def notify_customer_followup(
        self,
        user_id: str,
        company_name: str,
        customer_id: str,
        days_since_contact: int,
    ):
        """
        创建客户跟进提醒

        Args:
            user_id: 用户ID
            company_name: 公司名称
            customer_id: 客户ID
            days_since_contact: 距上次联系天数
        """
        await self.create_notification(
            user_id=user_id,
            type="followup",
            title="客户跟进提醒",
            message=f"{company_name} 已经 {days_since_contact} 天没有联系了",
            data={
                "customer_id": customer_id,
                "company_name": company_name,
                "days_since_contact": days_since_contact,
            },
        )

    async def notify_system_announcement(
        self,
        user_id: str,
        title: str,
        message: str,
        data: Optional[dict] = None,
    ):
        """
        创建系统公告通知

        Args:
            user_id: 用户ID
            title: 公告标题
            message: 公告内容
            data: 额外数据
        """
        await self.create_notification(
            user_id=user_id,
            type="system",
            title=title,
            message=message,
            data=data,
        )
