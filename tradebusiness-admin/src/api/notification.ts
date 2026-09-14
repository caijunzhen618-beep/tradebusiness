/**
 * 通知 API
 */
import request from '@/utils/request'

export interface Notification {
  id: string
  user_id: string
  type: string
  title: string
  message: string
  data: any
  is_read: boolean
  read_at: string | null
  expires_at: string | null
  created_at: string
  updated_at: string
}

export interface NotificationListParams {
  skip?: number
  limit?: number
  type?: string
  is_read?: boolean
}

/**
 * 获取通知列表
 */
export function getNotifications(params: NotificationListParams) {
  return request<{ total: number; items: Notification[] }>({
    url: '/api/v1/notifications',
    method: 'get',
    params,
  })
}

/**
 * 获取未读数量
 */
export function getUnreadCount() {
  return request<{ count: number }>({
    url: '/api/v1/notifications/unread-count',
    method: 'get',
  })
}

/**
 * 标记为已读
 */
export function markAsRead(id: string) {
  return request<Notification>({
    url: `/api/v1/notifications/${id}/read`,
    method: 'post',
  })
}

/**
 * 全部标记为已读
 */
export function markAllAsRead() {
  return request({
    url: '/api/v1/notifications/mark-all-read',
    method: 'post',
  })
}

/**
 * 删除通知
 */
export function deleteNotification(id: string) {
  return request({
    url: `/api/v1/notifications/${id}`,
    method: 'delete',
  })
}

/**
 * 批量删除已读
 */
export function deleteReadNotifications() {
  return request({
    url: '/api/v1/notifications/delete-read',
    method: 'delete',
  })
}
