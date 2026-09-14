/**
 * 邮件相关类型定义
 */

export interface Email {
  id: string
  customer_id?: string
  sender_id: string
  subject: string
  body: string
  direction: EmailDirection
  status: EmailStatus
  to_email: string
  to_name?: string
  from_email: string
  from_name?: string
  template_id?: string
  template_name?: string
  sent_at?: string
  opened_at?: string
  clicked_at?: string
  replied_at?: string
  error_message?: string
  message_id?: string
  thread_id?: string
  attachments?: EmailAttachment[]
  created_at: string
  updated_at: string
}

export type EmailDirection = 'incoming' | 'outgoing'

export type EmailStatus =
  | 'draft'
  | 'queued'
  | 'sent'
  | 'failed'
  | 'opened'
  | 'replied'

export interface EmailAttachment {
  filename: string
  url: string
  size: number
  content_type: string
}

export interface EmailTemplate {
  id: string
  name: string
  subject: string
  body: string
  category?: TemplateCategory
  language: string
  variables?: Record<string, any>
  is_active: boolean
  created_by?: string
  created_at: string
  updated_at: string
}

export type TemplateCategory = 'intro' | 'followup' | 'greeting' | 'promotion' | 'other'

export interface SendEmailParams {
  to_email: string
  to_name?: string
  subject: string
  body: string
  template_id?: string
  template_variables?: Record<string, any>
  customer_id?: string
  attachments?: EmailAttachment[]
}

export interface EmailListParams {
  search?: string
  status?: EmailStatus
  direction?: EmailDirection
  customer_id?: string
  skip?: number
  limit?: number
  page?: number
  page_size?: number
}

export interface EmailListResponse {
  items: Email[]
  total: number
  page: number
  page_size: number
}

export interface EmailStats {
  total: number
  sent: number
  opened: number
  clicked: number
  replied: number
  failed: number
  by_template: Record<string, number>
  open_rate?: number
  click_rate?: number
  reply_rate?: number
}

// 邮件状态映射
export const EmailStatusMap: Record<EmailStatus, string> = {
  draft: '草稿',
  queued: '队列中',
  sent: '已发送',
  failed: '发送失败',
  opened: '已打开',
  replied: '已回复',
}

// 邮件状态类型映射
export const EmailStatusTypeMap: Record<EmailStatus, string> = {
  draft: 'default',
  queued: 'info',
  sent: 'success',
  failed: 'error',
  opened: 'warning',
  replied: 'success',
}

// 邮件方向映射
export const EmailDirectionMap: Record<EmailDirection, string> = {
  incoming: '接收',
  outgoing: '发送',
}

// 模板分类映射
export const TemplateCategoryMap: Record<TemplateCategory, string> = {
  intro: '介绍邮件',
  followup: '跟进邮件',
  greeting: '问候邮件',
  promotion: '推广邮件',
  other: '其他',
}
