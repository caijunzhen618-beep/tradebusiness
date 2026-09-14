/**
 * 客户相关 API
 */

import request from './request'
import type {
  Customer,
  CustomerCreate,
  CustomerListParams,
  CustomerListResponse,
  CustomerStats,
} from '@/types/customer'

export type {
  Customer,
  CustomerCreate,
  CustomerListParams,
  CustomerListResponse,
  CustomerStats,
}

/**
 * 获取客户列表
 */
export function getCustomers(params?: CustomerListParams) {
  const normalizedParams = { ...params }
  if (!normalizedParams.status || normalizedParams.status === 'all') {
    delete normalizedParams.status
  }

  return request<CustomerListResponse>({
    url: '/api/v1/customers',
    method: 'get',
    params: normalizedParams,
  })
}

/**
 * 获取我的客户列表
 */
export function getMyCustomers(params?: Pick<CustomerListParams, 'page' | 'page_size' | 'search' | 'status'>) {
  return request<CustomerListResponse>({
    url: '/api/v1/customers/my',
    method: 'get',
    params,
  })
}

/**
 * 获取未分配客户列表
 */
export function getUnassignedCustomers(params?: Pick<CustomerListParams, 'page' | 'page_size'>) {
  return request<CustomerListResponse>({
    url: '/api/v1/customers/unassigned',
    method: 'get',
    params,
  })
}

/**
 * 获取客户详情
 */
export function getCustomer(id: string) {
  return request<Customer>({
    url: `/api/v1/customers/${id}`,
    method: 'get',
  })
}

/**
 * 创建客户
 */
export function createCustomer(data: CustomerCreate) {
  return request<Customer>({
    url: '/api/v1/customers',
    method: 'post',
    data,
  })
}

/**
 * 更新客户
 */
export function updateCustomer(id: string, data: Partial<CustomerCreate>) {
  return request<Customer>({
    url: `/api/v1/customers/${id}`,
    method: 'put',
    data,
  })
}

/**
 * 删除客户
 */
export function deleteCustomer(id: string) {
  return request<void>({
    url: `/api/v1/customers/${id}`,
    method: 'delete',
  })
}

/**
 * 分配客户给我
 */
export function assignCustomer(id: string) {
  return request<Customer>({
    url: `/api/v1/customers/${id}/assign`,
    method: 'post',
  })
}

/**
 * 更新客户状态
 */
export function updateCustomerStatus(id: string, status: string) {
  return request<Customer>({
    url: `/api/v1/customers/${id}/status`,
    method: 'post',
    data: { new_status: status },
  })
}

/**
 * 取消客户分配
 */
export function unassignCustomer(id: string) {
  return request<Customer>({
    url: `/api/v1/customers/${id}/unassign`,
    method: 'post',
  })
}

/**
 * 获取客户统计
 */
export function getCustomerStats() {
  return request<CustomerStats>({
    url: '/api/v1/customers/stats',
    method: 'get',
  })
}

/**
 * 批量导入客户
 */
export function batchImportCustomers(data: {
  customers: CustomerCreate[]
  overwrite?: boolean
}) {
  return request<{ success: number; failed: number; errors: string[] }>({
    url: '/api/v1/customers/batch',
    method: 'post',
    data,
  })
}
