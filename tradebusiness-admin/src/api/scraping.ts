/**
 * 数据采集 API
 */
import request from '@/utils/request'

export interface ScrapingTask {
  id: string
  name: string
  task_type:
    | 'google'
    | 'kompass'
    | 'yellow_pages'
    | 'port_authorities'
    | 'directory'
    | 'specific_site'
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled'
  config: {
    max_concurrent: number
    delay_min: number
    delay_max: number
    sources?: string[]
    source_urls?: string[]
  }
  keywords: string[]
  countries: string[]
  source_urls: string[]
  progress_current: number
  progress_total: number
  total_found: number
  total_saved: number
  status_message?: string
  error_message?: string
  last_run_summary?: {
    total_found?: number
    total_saved?: number
    diagnostics?: string[]
    source_checks?: Array<{
      url: string
      ok: boolean
      reason?: string
      status_code?: number
      found_fields?: string[]
    }>
  }
  execution_log?: Array<{
    time: string
    level: 'info' | 'warning' | 'error' | 'success'
    message: string
    extra?: Record<string, any>
  }>
  created_at: string
  updated_at: string
  started_at?: string
  completed_at?: string
}

export interface ScrapingTaskCreate {
  name: string
  task_type: string
  keywords: string[]
  countries: string[]
  source_urls: string[]
  config: {
    max_concurrent: number
    delay_min: number
    delay_max: number
    sources?: string[]
    source_urls?: string[]
  }
}

export interface ScrapingTaskListParams {
  skip?: number
  limit?: number
  status?: string
}

/**
 * 获取采集任务列表
 */
export function getScrapingTasks(params?: ScrapingTaskListParams) {
  return request<{ total: number; items: ScrapingTask[] }>({
    url: '/api/v1/scraping/tasks',
    method: 'get',
    params,
  }).catch((error) => {
    console.error('获取采集任务列表失败:', error)
    // 返回默认值避免渲染错误
    return { items: [], total: 0 }
  })
}

/**
 * 创建采集任务
 */
export function createScrapingTask(data: ScrapingTaskCreate) {
  return request<ScrapingTask>({
    url: '/api/v1/scraping/tasks',
    method: 'post',
    data,
  })
}

/**
 * 获取任务详情
 */
export function getScrapingTask(id: string) {
  return request<ScrapingTask>({
    url: `/api/v1/scraping/tasks/${id}`,
    method: 'get',
  })
}

/**
 * 启动任务
 */
export function startScrapingTask(id: string) {
  return request<ScrapingTask>({
    url: `/api/v1/scraping/tasks/${id}/start`,
    method: 'post',
  })
}

/**
 * 取消任务
 */
export function cancelScrapingTask(id: string) {
  return request<ScrapingTask>({
    url: `/api/v1/scraping/tasks/${id}/cancel`,
    method: 'post',
  })
}

/**
 * 删除任务
 */
export function deleteScrapingTask(id: string) {
  return request({
    url: `/api/v1/scraping/tasks/${id}`,
    method: 'delete',
  })
}

/**
 * 获取可用数据源
 */
export function getScrapingSources() {
  return request<{ sources: string[] }>({
    url: '/api/v1/scraping/sources',
    method: 'get',
  })
}
