/**
 * 任务管理 API
 */
import request from '@/utils/request'

export interface Task {
  id: string
  title: string
  description: string
  type?: string
  status: 'pending' | 'in_progress' | 'completed' | 'cancelled'
  priority: 'low' | 'medium' | 'high' | 'urgent'
  customer_id?: string | null
  assigned_to: string
  due_date: string | null
  completed_at: string | null
  created_by: string
  created_at: string
  updated_at: string
  assigned_user?: {
    id: string
    username: string
    full_name: string
  }
  creator?: {
    id: string
    username: string
    full_name: string
  }
}

export interface TaskCreate {
  title: string
  description: string
  priority: 'low' | 'medium' | 'high' | 'urgent'
  assigned_to: string
  due_date?: string
}

export interface TaskUpdate {
  title?: string
  description?: string
  status?: 'pending' | 'in_progress' | 'completed' | 'cancelled'
  priority?: 'low' | 'medium' | 'high' | 'urgent'
  assigned_to?: string
  due_date?: string
}

export interface TaskListParams {
  skip?: number
  limit?: number
  status?: string
  priority?: string
  assigned_to?: string
  search?: string
}

export interface TaskListResponse {
  total: number
  items: Task[]
}

function normalizeTaskListResponse(response: TaskListResponse | Task[]): TaskListResponse {
  if (Array.isArray(response)) {
    return {
      items: response,
      total: response.length,
    }
  }

  return response
}

/**
 * 获取任务列表
 */
export function getTasks(params: TaskListParams) {
  return request<TaskListResponse>({
    url: '/api/v1/tasks',
    method: 'get',
    params,
  })
}

/**
 * 获取我的任务
 */
export function getMyTasks(params: TaskListParams) {
  return request<TaskListResponse>({
    url: '/api/v1/tasks/my',
    method: 'get',
    params,
  })
}

/**
 * 获取逾期任务
 */
export function getOverdueTasks(params: TaskListParams) {
  return request<Task[]>({
    url: '/api/v1/tasks/overdue',
    method: 'get',
    params,
  }).then(normalizeTaskListResponse)
}

/**
 * 获取即将到期任务
 */
export function getUpcomingTasks(params: TaskListParams) {
  return request<Task[]>({
    url: '/api/v1/tasks/upcoming',
    method: 'get',
    params,
  }).then(normalizeTaskListResponse)
}

/**
 * 获取任务详情
 */
export function getTask(id: string) {
  return request<Task>({
    url: `/api/v1/tasks/${id}`,
    method: 'get',
  })
}

/**
 * 创建任务
 */
export function createTask(data: TaskCreate) {
  return request<Task>({
    url: '/api/v1/tasks',
    method: 'post',
    data,
  })
}

/**
 * 更新任务
 */
export function updateTask(id: string, data: TaskUpdate) {
  return request<Task>({
    url: `/api/v1/tasks/${id}`,
    method: 'put',
    data,
  })
}

/**
 * 删除任务
 */
export function deleteTask(id: string) {
  return request({
    url: `/api/v1/tasks/${id}`,
    method: 'delete',
  })
}

/**
 * 完成任务
 */
export function completeTask(id: string) {
  return request<Task>({
    url: `/api/v1/tasks/${id}/complete`,
    method: 'post',
  })
}

/**
 * 获取任务统计
 */
export function getTaskStats() {
  return request<{
    total: number
    pending: number
    in_progress: number
    completed: number
    overdue: number
    upcoming: number
  }>({
    url: '/api/v1/tasks/stats',
    method: 'get',
  })
}
