"""
WebSocket 和通知管理 API
实现实时通知推送和通知管理
"""

import uuid
from typing import List

from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.common import MessageResponse, PaginatedResponse
from app.schemas.notification import NotificationResponse
from app.services.notification_service import NotificationService, manager

router = APIRouter()


@router.websocket("/ws/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    user_id: str,
):
    """
    WebSocket 连接端点

    用于实时推送通知给客户端

    Args:
        websocket: WebSocket 连接
        user_id: 用户ID
    """
    await websocket.accept()

    # 验证用户（简化版，实际应该验证 Token）
    try:
        # 将连接添加到管理器
        await manager.connect(user_id, websocket)

        # 发送欢迎消息
        await websocket.send_json(
            {
                "type": "connected",
                "message": "WebSocket connected successfully",
                "user_id": user_id,
            }
        )

        # 持续接收消息（保持连接）
        while True:
            data = await websocket.receive_text()
            # 可以处理客户端发送的消息
            import json

            try:
                message = json.loads(data)
                if message.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
            except json.JSONDecodeError:
                pass

    except WebSocketDisconnect:
        manager.disconnect(user_id, websocket)
    except Exception as e:
        manager.disconnect(user_id, websocket)
        raise e


@router.get("", response_model=PaginatedResponse[NotificationResponse])
async def get_notifications(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(20, ge=1, le=100, description="返回的记录数"),
    unread_only: bool = Query(False, description="仅获取未读通知"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取当前用户的通知列表

    支持分页和筛选。
    """
    notification_service = NotificationService(db)

    notifications, total = await notification_service.get_user_notifications(
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        unread_only=unread_only,
    )

    notification_responses = [
        NotificationResponse(
            id=str(notification.id),
            type=notification.type,
            title=notification.title,
            message=notification.message,
            data=notification.data,
            user_id=str(notification.user_id),
            is_read=notification.is_read,
            created_at=notification.created_at,
            read_at=notification.read_at,
        )
        for notification in notifications
    ]

    return PaginatedResponse.create(
        items=notification_responses,
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/unread-count")
async def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取当前用户的未读通知数量
    """
    notification_service = NotificationService(db)

    count = await notification_service.get_unread_count(current_user.id)

    return {"count": count}


@router.post("/{notification_id}/read", response_model=NotificationResponse)
async def mark_notification_as_read(
    notification_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    标记通知为已读
    """
    notification_service = NotificationService(db)

    notification = await notification_service.mark_as_read(
        notification_id=notification_id,
        user_id=current_user.id,
    )

    return NotificationResponse(
        id=str(notification.id),
        type=notification.type,
        title=notification.title,
        message=notification.message,
        data=notification.data,
        user_id=str(notification.user_id),
        is_read=notification.is_read,
        created_at=notification.created_at,
        read_at=notification.read_at,
    )


@router.post("/mark-all-read")
async def mark_all_as_read(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    标记所有通知为已读
    """
    notification_service = NotificationService(db)

    count = await notification_service.mark_all_as_read(current_user.id)

    return MessageResponse(
        code=200,
        message=f"已标记 {count} 条通知为已读",
        data={"count": count},
    )


@router.delete("/delete-read", response_model=MessageResponse)
async def delete_read_notifications(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    删除当前用户所有已读通知
    """
    notification_service = NotificationService(db)
    count = await notification_service.delete_read_notifications(current_user.id)

    return MessageResponse(
        code=200,
        message=f"已删除 {count} 条已读通知",
        data={"count": count},
    )


@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(
    notification_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    删除通知
    """
    notification_service = NotificationService(db)
    await notification_service.delete_notification(
        notification_id=notification_id,
        user_id=current_user.id,
    )


@router.get("/online-users")
async def get_online_users():
    """
    获取在线用户列表

    Returns:
        在线用户ID列表
    """
    online_users = manager.get_online_users()
    return {
        "count": len(online_users),
        "users": online_users,
    }
