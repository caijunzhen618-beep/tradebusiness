/**
 * 邮件管理 API
 */
import request from '@/utils/request'

export interface Email {
  id: string
  customer_id?: string
  sender_id?: string
  subject: string
  body: string
  direction?: 'incoming' | 'outgoing'
  status: 'draft' | 'queued' | 'sent' | 'failed' | 'opened' | 'replied'
  to_email?: string
  to_name?: string
  from_email?: string
  from_name?: string
  template_name?: string
  sent_at: string | null
  opened_at?: string | null
  replied_at?: string | null
  error_message?: string | null
  created_at: string
  updated_at: string
  customer?: {
    id: string
    company_name: string
    email: string
  }
}

export interface EmailListParams {
  skip?: number
  limit?: number
  status?: string
  customer_id?: string
  search?: string
}

export interface EmailStats {
  total: number
  sent: number
  opened: number
  replied: number
  failed: number
  opened_count: number
  clicked: number
  by_template: Record<string, number>
  open_rate: number
  click_rate: number
  reply_rate: number
}

export interface EmailTemplate {
  id: string
  name: string
  subject: string
  body: string
  category?: string
  language: string
  variables?: Record<string, any>
  is_active: boolean
  created_by?: string | null
  created_at?: string | null
  updated_at?: string | null
}

/**
 * 获取邮件列表
 */
export function getEmails(params: EmailListParams) {
  return request<{ total: number; items: Email[] }>({
    url: '/api/v1/emails',
    method: 'get',
    params,
  })
}

/**
 * 获取邮件统计
 */
export function getEmailStats() {
  return request<EmailStats>({
    url: '/api/v1/emails/stats',
    method: 'get',
  })
}

/**
 * 获取邮件详情
 */
export function getEmail(id: string) {
  return request<Email>({
    url: `/api/v1/emails/${id}`,
    method: 'get',
  })
}

/**
 * 删除邮件
 */
export function deleteEmail(id: string) {
  return request({
    url: `/api/v1/emails/${id}`,
    method: 'delete',
  })
}

/**
 * 重新发送失败邮件
 */
export function resendEmail(id: string) {
  return request<Email>({
    url: `/api/v1/emails/${id}/resend`,
    method: 'post',
  })
}

export function getEmailTemplates(params?: { category?: string; language?: string }) {
  return request<EmailTemplate[]>({
    url: '/api/v1/emails/templates',
    method: 'get',
    params,
  })
}

export function createEmailTemplate(data: Partial<EmailTemplate>) {
  return request<EmailTemplate>({
    url: '/api/v1/emails/templates',
    method: 'post',
    data,
  })
}

export function updateEmailTemplate(id: string, data: Partial<EmailTemplate>) {
  return request<EmailTemplate>({
    url: `/api/v1/emails/templates/${id}`,
    method: 'put',
    data,
  })
}

export function deleteEmailTemplate(id: string) {
  return request<void>({
    url: `/api/v1/emails/templates/${id}`,
    method: 'delete',
  })
}

export function previewEmailTemplate(templateId: string, variables?: Record<string, any>) {
  return request<{ subject: string; body: string }>({
    url: `/api/v1/emails/templates/${templateId}/preview`,
    method: 'post',
    data: { variables },
  })
}
