export interface User {
  id: string
  username: string
  email: string
  full_name?: string
  role: 'admin' | 'sales'
  is_active: boolean
  is_superuser: boolean
  phone?: string
  avatar_url?: string
  department?: string
  created_at: string
  updated_at: string
}

export interface LoginRequest {
  username: string
  password: string
}

export interface LoginResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
  user: User
}
