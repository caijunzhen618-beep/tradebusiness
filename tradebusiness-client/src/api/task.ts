/**
 * 任务管理 API
 */
import request from './request'

export interface Task {
  id: string
  title: string
  description?: string | null
  type?: string | null
  status: 'pending' | 'in_progress' | 'completed' | 'cancelled'
  priority: 'low' | 'medium' | 'high' | 'urgent'
  customer_id?: string | null
  assigned_to?: string | null
  created_by?: string | null
  due_date?: string | null
  completed_at?: string | null
  reminder_at?: string | null
  is_reminded: boolean
  created_at: string
  updated_at: string
}

export interface TaskCreate {
  title: string
  description?: string
  type?: string
  priority: string
  due_date?: string | null
  customer_id?: string | null
  assigned_to: string
}

export interface TaskUpdate {
  title?: string
  description?: string
  type?: string
  status?: string
  priority?: string
  due_date?: string | null
  customer_id?: string | null
}

export interface TaskListResponse {
  items: Task[]
  total: number
  skip?: number
  limit?: number
}

export interface TaskStats {
  total: number
  pending: number
  in_progress: number
  completed: number
  overdue?: number
  upcoming?: number
}

export function getTasks(params?: {
  skip?: number
  limit?: number
  status?: string
  priority?: string
  customer_id?: string
}) {
  return request<TaskListResponse>({
    url: '/api/v1/tasks',
    method: 'get',
    params,
  })
}

export function getTaskStats() {
  return request<TaskStats>({
    url: '/api/v1/tasks/stats',
    method: 'get',
  })
}

export function createTask(data: TaskCreate) {
  return request<Task>({
    url: '/api/v1/tasks',
    method: 'post',
    data,
  })
}

export function updateTask(id: string, data: TaskUpdate) {
  return request<Task>({
    url: `/api/v1/tasks/${id}`,
    method: 'put',
    data,
  })
}

export function completeTask(id: string) {
  return request<Task>({
    url: `/api/v1/tasks/${id}/complete`,
    method: 'post',
  })
}
