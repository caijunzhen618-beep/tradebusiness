import { post, get, put, del } from './request'
import type { LoginResponse, User } from '@/types/user'

export function login(username: string, password: string): Promise<LoginResponse> {
  return post<LoginResponse>('/api/v1/auth/login', { username, password })
}

export function getUserInfo(): Promise<User> {
  return get<User>('/api/v1/users/me')
}

export function getUserList(params?: Record<string, unknown>): Promise<any> {
  const normalizedParams = { ...params }

  // “全部”不是后端 UserStatus 的有效值；查询全部时省略 status。
  if (!normalizedParams.status || normalizedParams.status === 'all') {
    delete normalizedParams.status
  }

  return get('/api/v1/users', { params: normalizedParams })
}

export function createUser(data: any): Promise<User> {
  return post('/api/v1/users', data)
}

export function updateUser(id: string, data: any): Promise<User> {
  return put(`/api/v1/users/${id}`, data)
}

export function deleteUser(id: string): Promise<void> {
  return del(`/api/v1/users/${id}`)
}

export function toggleUserStatus(id: string): Promise<User> {
  return post(`/api/v1/users/${id}/toggle-status`)
}

export function changePassword(data: {
  old_password: string
  new_password: string
}): Promise<User> {
  return post('/api/v1/users/me/change-password', data)
}
