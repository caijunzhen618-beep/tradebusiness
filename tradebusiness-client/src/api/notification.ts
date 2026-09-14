import request from './request'

export interface Notification {
  id: string
  type: string
  title: string
  message: string
  data?: Record<string, any>
  user_id: string
  is_read: boolean
  created_at: string
  read_at?: string | null
}

export interface NotificationListResponse {
  items: Notification[]
  total: number
  skip: number
  limit: number
}

export function getNotifications(params?: {
  skip?: number
  limit?: number
  unread_only?: boolean
}) {
  return request<NotificationListResponse>({
    url: '/api/v1/notifications',
    method: 'get',
    params,
  })
}

export function getUnreadCount() {
  return request<{ count: number }>({
    url: '/api/v1/notifications/unread-count',
    method: 'get',
  })
}

export function markNotificationRead(id: string) {
  return request<Notification>({
    url: `/api/v1/notifications/${id}/read`,
    method: 'post',
  })
}

export function markAllNotificationsRead() {
  return request<{ count: number }>({
    url: '/api/v1/notifications/mark-all-read',
    method: 'post',
  })
}

export function deleteNotification(id: string) {
  return request<void>({
    url: `/api/v1/notifications/${id}`,
    method: 'delete',
  })
}
