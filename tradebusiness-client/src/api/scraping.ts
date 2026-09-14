/**
 * 数据采集 API
 */
import request from './request'

export interface ScrapingTask {
  id: string
  name: string
  task_type: 'google' | 'directory' | 'specific_site'
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled'
  config: Record<string, any>
  keywords: string[]
  countries: string[]
  total_found: number
  total_saved: number
  error_message?: string | null
  created_at: string
  updated_at: string
  started_at?: string | null
  completed_at?: string | null
}

export interface ScrapingTaskCreate {
  name: string
  task_type: 'google' | 'directory' | 'specific_site'
  keywords: string[]
  countries: string[]
  config: Record<string, any>
}

export interface ScrapingTaskListResponse {
  items: ScrapingTask[]
  total: number
  skip: number
  limit: number
}

export function getScrapingTasks(params?: { skip?: number; limit?: number; status?: string }) {
  return request<ScrapingTaskListResponse>({
    url: '/api/v1/scraping/tasks',
    method: 'get',
    params,
  })
}

export function createScrapingTask(data: ScrapingTaskCreate) {
  return request<ScrapingTask>({
    url: '/api/v1/scraping/tasks',
    method: 'post',
    data,
  })
}

export function startScrapingTask(id: string) {
  return request<{ message: string }>({
    url: `/api/v1/scraping/tasks/${id}/start`,
    method: 'post',
  })
}

export function cancelScrapingTask(id: string) {
  return request<{ message: string }>({
    url: `/api/v1/scraping/tasks/${id}/cancel`,
    method: 'post',
  })
}
