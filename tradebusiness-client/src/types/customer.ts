/**
 * 客户相关类型定义
 */

export interface Customer {
  id: string
  company_name: string
  company_name_en?: string
  logo_url?: string
  website?: string
  established_year?: number
  registered_capital?: string
  company_size?: number
  business_type?: string
  main_ports?: string[]
  route_coverage?: string[]
  cargo_specialization?: string[]
  estimated_volume?: number
  country_code: string
  country: string
  city?: string
  address?: string
  phone?: string
  email?: string
  whatsapp?: string
  wechat?: string
  linkedin_url?: string
  facebook_url?: string
  status: CustomerStatus
  assigned_to?: string
  priority: number
  source?: string
  source_url?: string
  data_confidence?: number
  tags?: string[]
  notes?: string
  first_contact_date?: string
  cooperation_date?: string
  created_at: string
  updated_at: string
}

export type CustomerStatus =
  | 'potential'
  | 'contacting'
  | 'cooperating'
  | 'paused'
  | 'lost'

export type BusinessType = 'sea' | 'air' | 'land' | 'multimodal'

export interface CustomerCreate {
  company_name: string
  company_name_en?: string
  website?: string
  established_year?: number
  company_size?: number
  business_type?: BusinessType
  main_ports?: string[]
  route_coverage?: string[]
  cargo_specialization?: string[]
  estimated_volume?: number
  country_code: string
  country: string
  city?: string
  address?: string
  phone?: string
  email?: string
  whatsapp?: string
  wechat?: string
  linkedin_url?: string
  facebook_url?: string
  status?: CustomerStatus
  priority?: number
  source?: string
  source_url?: string
  tags?: string[]
  notes?: string
}

export interface CustomerUpdate extends Partial<CustomerCreate> {}

export interface CustomerListParams {
  search?: string
  country?: string
  status?: CustomerStatus | 'all'
  business_type?: BusinessType
  assigned?: boolean
  page?: number
  page_size?: number
}

export interface CustomerListResponse {
  items: Customer[]
  total: number
  page: number
  page_size: number
}

export interface CustomerStats {
  total: number
  by_status: Record<string, number>
  by_country: Record<string, number>
  by_assigned: Record<string, number>
  my_customers: number
  unassigned: number
  this_week?: number
}

// 业务类型映射
export const BusinessTypeMap: Record<string, string> = {
  sea: '海运',
  air: '空运',
  land: '陆运',
  multimodal: '多式联运',
}

// 客户状态映射
export const CustomerStatusMap: Record<CustomerStatus, string> = {
  potential: '潜在客户',
  contacting: '联系中',
  cooperating: '合作中',
  paused: '暂停',
  lost: '流失',
}

// 客户状态类型映射（用于 UI 颜色）
export const CustomerStatusTypeMap: Record<CustomerStatus, string> = {
  potential: 'default',
  contacting: 'info',
  cooperating: 'success',
  paused: 'warning',
  lost: 'error',
}

// 优先级映射
export const PriorityMap: Record<number, string> = {
  1: '最高',
  2: '高',
  3: '中',
  4: '低',
  5: '最低',
}

// 优先级类型映射
export const PriorityTypeMap: Record<number, string> = {
  1: 'error',
  2: 'warning',
  3: 'default',
  4: 'info',
  5: 'info',
}
