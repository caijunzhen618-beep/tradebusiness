/**
 * AI 获客 API
 */
import request from '@/utils/request'

export interface LeadSearchTask {
  id: string
  user_id: string
  name: string
  target_country?: string
  target_industry?: string
  product_keywords: string[]
  customer_profile?: string
  exclude_keywords: string[]
  website_inputs: string[]
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled'
  total_found: number
  error_message?: string
  created_at: string
  updated_at: string
}

export interface LeadSearchTaskCreate {
  name: string
  target_country?: string
  target_industry?: string
  product_keywords: string[]
  customer_profile?: string
  exclude_keywords: string[]
  website_inputs: string[]
}

export interface Lead {
  id: string
  task_id?: string
  user_id: string
  company_name: string
  website?: string
  country?: string
  industry?: string
  description?: string
  source?: string
  match_score?: number
  status: 'new' | 'researched' | 'copy_generated' | 'contacted' | 'replied' | 'invalid'
  do_not_contact: boolean
  do_not_contact_reason?: string
  notes?: string
  created_at: string
  updated_at: string
}

export interface CompanyResearchReport {
  id: string
  lead_id: string
  summary: string
  business_model?: string
  products?: string
  target_markets?: string
  buying_signals?: string
  pain_points?: string
  recommended_angle?: string
  raw_sources?: Record<string, unknown>
  created_at: string
  updated_at: string
}

export interface SalesCopy {
  id: string
  lead_id: string
  channel: 'email' | 'whatsapp' | 'linkedin'
  language: string
  subject?: string
  content: string
  tone?: string
  status: string
  created_at: string
  updated_at: string
}

export function getLeadTasks(params?: { skip?: number; limit?: number; status?: string }) {
  return request<{ items: LeadSearchTask[]; total: number }>({
    url: '/api/v1/lead-generation/tasks',
    method: 'get',
    params,
  })
}

export function createLeadTask(data: LeadSearchTaskCreate) {
  return request<LeadSearchTask>({
    url: '/api/v1/lead-generation/tasks',
    method: 'post',
    data,
  })
}

export function runLeadTask(id: string) {
  return request<LeadSearchTask>({
    url: `/api/v1/lead-generation/tasks/${id}/run`,
    method: 'post',
  })
}

export function cancelLeadTask(id: string) {
  return request<LeadSearchTask>({
    url: `/api/v1/lead-generation/tasks/${id}/cancel`,
    method: 'post',
  })
}

export function getLeadTask(id: string) {
  return request<LeadSearchTask>({
    url: `/api/v1/lead-generation/tasks/${id}`,
    method: 'get',
  })
}

export function getLeads(params?: {
  skip?: number
  limit?: number
  task_id?: string
  status?: string
  search?: string
}) {
  return request<{ items: Lead[]; total: number }>({
    url: '/api/v1/lead-generation/leads',
    method: 'get',
    params,
  })
}

export function createLead(data: Partial<Lead>) {
  return request<Lead>({
    url: '/api/v1/lead-generation/leads',
    method: 'post',
    data,
  })
}

export function generateCompanyResearch(leadId: string) {
  return request<CompanyResearchReport>({
    url: `/api/v1/lead-generation/leads/${leadId}/research`,
    method: 'post',
  })
}

export function getCompanyResearch(leadId: string) {
  return request<CompanyResearchReport | null>({
    url: `/api/v1/lead-generation/leads/${leadId}/research`,
    method: 'get',
  })
}

export function generateSalesCopy(
  leadId: string,
  data: { channel: 'email' | 'whatsapp' | 'linkedin'; language: string; tone?: string; agent_id?: string }
) {
  return request<SalesCopy>({
    url: `/api/v1/lead-generation/leads/${leadId}/sales-copy`,
    method: 'post',
    data,
  })
}

export function getSalesCopies(leadId: string) {
  return request<SalesCopy[]>({
    url: `/api/v1/lead-generation/leads/${leadId}/sales-copies`,
    method: 'get',
  })
}

export function importLeadsCsv(file: File, taskId?: string) {
  const formData = new FormData()
  formData.append('file', file)
  return request<{ created: number }>({
    url: '/api/v1/lead-generation/leads/import',
    method: 'post',
    params: taskId ? { task_id: taskId } : undefined,
    data: formData,
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}
export interface LeadContact { id: string; lead_id: string; name?: string; title?: string; email?: string; phone?: string; linkedin_url?: string; whatsapp?: string; source?: string; is_verified: boolean; created_at: string; updated_at: string }
export function getLeadDetail(id: string) { return request<Lead>({ url: `/api/v1/lead-generation/leads/${id}`, method: 'get' }) }
export function updateLead(id: string, data: { do_not_contact: boolean; do_not_contact_reason?: string }) { return request<Lead>({ url: `/api/v1/lead-generation/leads/${id}`, method: 'patch', data }) }
export function getLeadContacts(id: string) { return request<LeadContact[]>({ url: `/api/v1/lead-generation/leads/${id}/contacts`, method: 'get' }) }
export function createLeadContact(id: string, data: Partial<LeadContact>) { return request<LeadContact>({ url: `/api/v1/lead-generation/leads/${id}/contacts`, method: 'post', data: { ...data, lead_id: id } }) }

export function sendLeadEmail(id: string, data: { to_email: string; to_name?: string; subject: string; body: string }) { return request<{ id: string; status: string; lead_id: string }>({ url: `/api/v1/lead-generation/leads/${id}/send-email`, method: 'post', data }) }
export interface FollowupTask { id: string; lead_id: string; channel: string; subject?: string; content: string; due_at: string; status: string }
export function getFollowups(channel?: string) { return request<FollowupTask[]>({ url: '/api/v1/lead-generation/followups', method: 'get', params: channel ? { channel } : undefined }) }
export function createFollowup(data: Partial<FollowupTask>) { return request<FollowupTask>({ url: '/api/v1/lead-generation/followups', method: 'post', data }) }
export function updateFollowup(id: string, status: string) { return request<FollowupTask>({ url: `/api/v1/lead-generation/followups/${id}`, method: 'patch', params: { status } }) }
export function retryFollowup(id: string) { return request<FollowupTask>({ url: `/api/v1/lead-generation/followups/${id}/retry`, method: 'post' }) }

export function getLeadGenerationStats() { return request<{ leads: number; sales_copies: number; followups: number; completed_followups: number; channels: Record<string, number>; countries: Record<string, number>; industries: Record<string, number>; statuses: Record<string, number> }>({ url: '/api/v1/lead-generation/stats', method: 'get' }) }



