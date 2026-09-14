import { request } from './request'
import type { CustomerResponse, CustomerCreate, CustomerUpdate } from '@/types/customer'

export function getCustomers(params?: Record<string, unknown>) {
  const normalizedParams = { ...params }

  // 后端使用 skip/limit；“全部”筛选必须省略 status，而不是传 status=all。
  if (!normalizedParams.status || normalizedParams.status === 'all') {
    delete normalizedParams.status
  }
  if (typeof normalizedParams.page === 'number') {
    const page = normalizedParams.page
    const pageSize = typeof normalizedParams.page_size === 'number'
      ? normalizedParams.page_size
      : 20
    normalizedParams.skip = (page - 1) * pageSize
    normalizedParams.limit = pageSize
    delete normalizedParams.page
    delete normalizedParams.page_size
  }

  return request<any>({
    url: '/api/v1/customers',
    method: 'get',
    params: normalizedParams,
  })
}

export function getCustomer(id: string) {
  return request<CustomerResponse>({
    url: `/api/v1/customers/${id}`,
    method: 'get',
  })
}

export function createCustomer(data: CustomerCreate) {
  return request<CustomerResponse>({
    url: '/api/v1/customers',
    method: 'POST',
    data,
  })
}

export function updateCustomer(id: string, data: CustomerUpdate) {
  return request<CustomerResponse>({
    url: `/api/v1/customers/${id}`,
    method: 'PUT',
    data,
  })
}

export function deleteCustomer(id: string) {
  return request({
    url: `/api/v1/customers/${id}`,
    method: 'DELETE',
  })
}

export function assignCustomer(id: string) {
  return request<CustomerResponse>({
    url: `/api/v1/customers/${id}/assign`,
    method: 'POST',
  })
}

export function updateCustomerStatus(id: string, status: string) {
  return request<CustomerResponse>({
    url: `/api/v1/customers/${id}/status`,
    method: 'POST',
    data: { new_status: status },
  })
}

export function getMyCustomers(params?: any) {
  return request<any>({
    url: '/api/v1/customers/my',
    method: 'get',
    params,
  })
}

export function getUnassignedCustomers(params?: any) {
  return request<any>({
    url: '/api/v1/customers/unassigned',
    method: 'get',
    params,
  })
}

export function getCustomerStats() {
  return request<any>({
    url: '/api/v1/customers/stats',
    method: 'get',
  })
}

export function batchImportCustomers(data: any) {
  return request<any>({
    url: '/api/v1/customers/batch',
    method: 'POST',
    data,
  })
}
