/**
 * 邮件相关 API
 */

import request from './request'
import type {
  Email,
  EmailListParams,
  EmailListResponse,
  EmailStats,
  EmailTemplate,
  SendEmailParams,
} from '@/types/email'

export type {
  Email,
  EmailListParams,
  EmailListResponse,
  EmailStats,
  EmailTemplate,
  SendEmailParams,
}

/**
 * 获取邮件列表
 */
export function getEmails(params?: EmailListParams) {
  return request<EmailListResponse>({
    url: '/api/v1/emails',
    method: 'get',
    params,
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
 * 发送邮件
 */
export function sendEmail(data: SendEmailParams) {
  return request<Email>({
    url: '/api/v1/emails/send',
    method: 'post',
    data,
  })
}

/**
 * 保存邮件草稿
 */
export function saveEmailDraft(data: SendEmailParams) {
  return request<Email>({
    url: '/api/v1/emails/draft',
    method: 'post',
    data,
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

/**
 * 删除邮件
 */
export function deleteEmail(id: string) {
  return request<void>({
    url: `/api/v1/emails/${id}`,
    method: 'delete',
  })
}

/**
 * 获取邮件模板列表
 */
export function getEmailTemplates(params?: { category?: string; language?: string }) {
  return request<EmailTemplate[]>({
    url: '/api/v1/emails/templates',
    method: 'get',
    params,
  })
}

/**
 * 获取邮件模板详情
 */
export function getEmailTemplate(id: string) {
  return request<EmailTemplate>({
    url: `/api/v1/emails/templates/${id}`,
    method: 'get',
  })
}

/**
 * 创建邮件模板
 */
export function createEmailTemplate(data: Partial<EmailTemplate>) {
  return request<EmailTemplate>({
    url: '/api/v1/emails/templates',
    method: 'post',
    data,
  })
}

/**
 * 更新邮件模板
 */
export function updateEmailTemplate(id: string, data: Partial<EmailTemplate>) {
  return request<EmailTemplate>({
    url: `/api/v1/emails/templates/${id}`,
    method: 'put',
    data,
  })
}

/**
 * 删除邮件模板
 */
export function deleteEmailTemplate(id: string) {
  return request<void>({
    url: `/api/v1/emails/templates/${id}`,
    method: 'delete',
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
 * 使用模板预览邮件
 */
export function previewEmailTemplate(templateId: string, variables?: Record<string, any>) {
  return request<{ subject: string; body: string }>({
    url: `/api/v1/emails/templates/${templateId}/preview`,
    method: 'post',
    data: { variables },
  })
}
