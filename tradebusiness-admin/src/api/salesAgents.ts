import request from '@/utils/request'
export interface SalesAgent { id: string; name: string; company_intro?: string; product_intro?: string; value_proposition?: string; target_customer?: string; tone: string; forbidden_words?: string; default_language: string; is_default: boolean }
export function getSalesAgents() { return request<SalesAgent[]>({ url: '/api/v1/sales-agents', method: 'get' }) }
export function createSalesAgent(data: Partial<SalesAgent>) { return request<SalesAgent>({ url: '/api/v1/sales-agents', method: 'post', data }) }
export function updateSalesAgent(id: string, data: Partial<SalesAgent>) { return request<SalesAgent>({ url: `/api/v1/sales-agents/${id}`, method: 'patch', data }) }
export interface KnowledgeDocument { id: string; agent_id: string; file_name: string; content_text: string; embedding_status: string; created_at: string; updated_at: string }
export function getAgentDocuments(id: string) { return request<KnowledgeDocument[]>({ url: `/api/v1/sales-agents/${id}/documents`, method: 'get' }) }
export function uploadAgentDocument(id: string, file: File) { const data = new FormData(); data.append('file', file); return request<KnowledgeDocument>({ url: `/api/v1/sales-agents/${id}/documents`, method: 'post', data, headers: { 'Content-Type': 'multipart/form-data' } }) }

export function deleteAgentDocument(agentId: string, documentId: string) { return request<void>({ url: `/api/v1/sales-agents/${agentId}/documents/${documentId}`, method: 'delete' }) }
export interface PromptTemplate { id: string; agent_id: string; name: string; channel: string; language: string; prompt_text: string; is_active: boolean }
export function getAgentTemplates(id: string) { return request<PromptTemplate[]>({ url: `/api/v1/sales-agents/${id}/templates`, method: 'get' }) }
export function createAgentTemplate(id: string, data: Partial<PromptTemplate>) { return request<PromptTemplate>({ url: `/api/v1/sales-agents/${id}/templates`, method: 'post', data }) }
