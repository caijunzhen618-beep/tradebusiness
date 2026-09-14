/**
 * 采集线索 API
 */
import request from '@/utils/request'

export interface ScrapedLead {
  id: string
  raw_data: Record<string, any>
  data_source: string
  source_url?: string
  company_name: string
  company_name_en?: string
  country: string
  country_code: string
  city?: string
  email?: string
  phone?: string
  whatsapp?: string
  website?: string
  business_type?: string
  description?: string
  confidence_score: number
  status: 'pending' | 'approved' | 'rejected' | 'imported'
  reviewed_by?: string
  reviewed_at?: string
  rejection_reason?: string
  imported_to_customer_id?: string
  imported_at?: string
  scraping_task_id: string
  matched_by?: string
  duplicate_of?: string
  similarity_score?: number
  created_at: string
  updated_at: string
}

export interface ScrapedLeadListParams {
  skip?: number
  limit?: number
  status?: string
  data_source?: string
  country_code?: string
  scraping_task_id?: string
}

export interface ScrapedLeadListResponse {
  items: ScrapedLead[]
  total: number
  skip: number
  limit: number
}

export interface BulkApproveRequest {
  lead_ids: string[]
  approved: boolean
  rejection_reason?: string
}

export interface BulkImportRequest {
  lead_ids: string[]
}

export interface BulkApproveResponse {
  approved_count: number
  rejected_count: number
  errors: string[]
}

export interface BulkImportResponse {
  imported_count: number
  duplicate_count: number
  errors: string[]
}

export interface DuplicateCheckResponse {
  is_duplicate: boolean
  duplicate_lead_id?: string
  similarity_score?: number
  existing_customer_id?: string
}

/**
 * 获取采集线索列表
 */
export function getScrapedLeads(params?: ScrapedLeadListParams) {
  return request<ScrapedLeadListResponse>({
    url: '/api/v1/leads',
    method: 'get',
    params,
  }).catch((error) => {
    console.error('获取采集线索列表失败:', error)
    // 返回默认值避免渲染错误
    return { items: [], total: 0, skip: 0, limit: 20 }
  })
}

/**
 * 获取采集线索详情
 */
export function getScrapedLead(id: string) {
  return request<ScrapedLead>({
    url: `/api/v1/leads/${id}`,
    method: 'get',
  })
}

/**
 * 审核通过线索
 */
export function approveScrapedLead(id: string) {
  return request<ScrapedLead>({
    url: `/api/v1/leads/${id}/approve`,
    method: 'post',
  })
}

/**
 * 拒绝线索
 */
export function rejectScrapedLead(id: string, reason?: string) {
  return request<ScrapedLead>({
    url: `/api/v1/leads/${id}/reject`,
    method: 'post',
    params: { reason },
  })
}

/**
 * 批量审核线索
 */
export function bulkApproveLeads(data: BulkApproveRequest) {
  return request<BulkApproveResponse>({
    url: '/api/v1/leads/bulk-approve',
    method: 'post',
    data,
  })
}

/**
 * 批量导入线索到客户表
 */
export function importLeadsToCustomers(data: BulkImportRequest) {
  return request<BulkImportResponse>({
    url: '/api/v1/leads/import',
    method: 'post',
    data,
  })
}

/**
 * 检查线索是否重复
 */
export function checkDuplicate(id: string) {
  return request<DuplicateCheckResponse>({
    url: `/api/v1/leads/${id}/duplicate-check`,
    method: 'get',
  })
}

/**
 * 删除线索
 */
export function deleteScrapedLead(id: string) {
  return request({
    url: `/api/v1/leads/${id}`,
    method: 'delete',
  })
}
