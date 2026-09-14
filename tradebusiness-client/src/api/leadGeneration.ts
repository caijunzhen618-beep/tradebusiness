import { get, post, request } from './request'

export interface LeadGenerationStats {
  leads: number
  sales_copies: number
  followups: number
  completed_followups: number
  contacted: number
  replied: number
  reply_rate: number
  channels: Record<string, number>
}

export interface CreditWallet {
  balance: number
}

export interface Lead {
  id: string
  company_name: string
  country?: string
  industry?: string
  status: string
  do_not_contact: boolean
  do_not_contact_reason?: string
  website?: string
  description?: string
  source?: string
}

export interface LeadListResponse {
  items: Lead[]
  total: number
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
}

export interface SalesCopy {
  id: string
  lead_id: string
  channel: string
  language: string
  subject?: string
  content: string
  tone?: string
  status: string
}

export interface LeadContact {
  id: string
  lead_id: string
  name?: string
  title?: string
  email?: string
  phone?: string
  linkedin_url?: string
  is_verified: boolean
}

export interface FollowupTask {
  id: string
  lead_id: string
  channel: string
  subject?: string
  content: string
  due_at: string
  status: string
}

export function getLeadGenerationStats() {
  return get<LeadGenerationStats>('/api/v1/lead-generation/stats')
}

export function getCreditWallet() {
  return get<CreditWallet>('/api/v1/billing/wallet')
}

export function getLeads(params?: { limit?: number; search?: string }) {
  return get<LeadListResponse>('/api/v1/lead-generation/leads', { params })
}

export function getLeadDetail(leadId: string) {
  return get<Lead>(`/api/v1/lead-generation/leads/${leadId}`)
}

export function updateLead(leadId: string, data: { do_not_contact: boolean; do_not_contact_reason?: string }) {
  return request<Lead>({ url: `/api/v1/lead-generation/leads/${leadId}`, method: 'patch', data })
}

export function getCompanyResearch(leadId: string) {
  return get<CompanyResearchReport | null>(`/api/v1/lead-generation/leads/${leadId}/research`)
}

export function getLeadContacts(leadId: string) {
  return get<LeadContact[]>(`/api/v1/lead-generation/leads/${leadId}/contacts`)
}

export function createLeadContact(leadId: string, data: Omit<LeadContact, 'id' | 'lead_id'>) {
  return post<LeadContact>(`/api/v1/lead-generation/leads/${leadId}/contacts`, { lead_id: leadId, ...data })
}

export function generateCompanyResearch(leadId: string) {
  return post<CompanyResearchReport>(`/api/v1/lead-generation/leads/${leadId}/research`)
}

export function getSalesCopies(leadId: string) {
  return get<SalesCopy[]>(`/api/v1/lead-generation/leads/${leadId}/sales-copies`)
}

export function generateSalesCopy(leadId: string, options: { channel: 'email' | 'whatsapp' | 'linkedin'; language: 'en' | 'zh' }) {
  return post<SalesCopy>(`/api/v1/lead-generation/leads/${leadId}/sales-copy`, {
    channel: options.channel,
    language: options.language,
    tone: 'professional',
  })
}

export function sendLeadEmail(leadId: string, data: { to_email: string; to_name?: string; subject: string; body: string }) {
  return post<{ id: string; status: string; lead_id: string }>(`/api/v1/lead-generation/leads/${leadId}/send-email`, data)
}

export function createFollowup(leadId: string, data: { channel: 'email'; subject?: string; content: string; due_at: string }) {
  return post(`/api/v1/lead-generation/followups`, { lead_id: leadId, ...data })
}

export function getFollowups(leadId?: string) {
  return get<FollowupTask[]>('/api/v1/lead-generation/followups', { params: leadId ? { lead_id: leadId } : undefined })
}

export function updateFollowup(id: string, status: 'pending' | 'completed' | 'failed' | 'cancelled') {
  return request<FollowupTask>({ url: `/api/v1/lead-generation/followups/${id}`, method: 'patch', params: { status } })
}

export function retryFollowup(id: string) {
  return post<FollowupTask>(`/api/v1/lead-generation/followups/${id}/retry`)
}
