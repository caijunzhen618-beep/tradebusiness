import { post, get, put } from './request'

export function login(username: string, password: string) {
  return post('/api/v1/auth/login', { username, password })
}

export function getUserInfo() {
  return get('/api/v1/users/me')
}

export function updateUser(id: string, data: any) {
  return put(`/api/v1/users/${id}`, data)
}

export function changePassword(data: {
  old_password: string
  new_password: string
}) {
  return post('/api/v1/users/me/change-password', data)
}

export function getMyCustomers(params?: any) {
  return get('/api/v1/customers/my', { params })
}

export function getUnassignedCustomers(params?: any) {
  return get('/api/v1/customers/unassigned', { params })
}

export function assignCustomer(customerId: string) {
  return post(`/api/v1/customers/${customerId}/assign`)
}
