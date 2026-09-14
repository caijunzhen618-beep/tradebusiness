interface Customer {
  id: string
  company_name: string
  company_name_en?: string
  company_name_local?: string
  logo_url?: string
  website?: string
  established_year?: number
  registered_capital?: string
  company_size?: number
  business_type?: 'sea' | 'air' | 'land' | 'multimodal'
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
  status: 'potential' | 'contacting' | 'cooperating' | 'paused' | 'lost'
  priority: number
  assigned_to?: string
  source?: string
  source_url?: string
  data_confidence?: number
  last_verified_at?: string
  tags?: string[]
  notes?: string
  first_contact_date?: string
  cooperation_date?: string
  created_at: string
  updated_at: string
}

type CustomerResponse = Customer

type CustomerCreate = Partial<Omit<Customer, 'id' | 'created_at' | 'updated_at' | 'last_verified_at'>>

type CustomerUpdate = Partial<CustomerCreate>

type CustomerListParams = {
  page?: number
  page_size?: number
  country?: string
  status?: string
  business_type?: string
  assigned_to?: string
  search?: string
  priority?: number
  tags?: string[]
  sort_by?: string
  sort_order?: 'asc' | 'desc'
}

type PaginatedResponse<T> = {
  items: T[]
  total: number
  page: number
  page_size: number
  pages: number
}

export type { Customer, CustomerResponse, CustomerCreate, CustomerUpdate, CustomerListParams, PaginatedResponse }
