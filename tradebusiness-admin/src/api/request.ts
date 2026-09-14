import axios, { AxiosRequestConfig, AxiosResponse, InternalAxiosRequestConfig } from 'axios'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/store/modules/user'
import logger from '@/utils/logger'

// 创建 axios 实例
interface RequestClient {
  <T = any>(config: AxiosRequestConfig): Promise<T>
  request<T = any>(config: AxiosRequestConfig): Promise<T>
  get<T = any>(url: string, config?: AxiosRequestConfig): Promise<T>
  post<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T>
  put<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T>
  delete<T = any>(url: string, config?: AxiosRequestConfig): Promise<T>
}

// 创建 axios 实例
const axiosService = axios.create({
  baseURL: import.meta.env.VITE_APP_BASE_API,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

const service = axiosService as unknown as RequestClient

// 请求拦截器
axiosService.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const userStore = useUserStore()
    if (userStore.token) {
      config.headers.Authorization = `Bearer ${userStore.token}`
    }

    // Log API request
    logger.debug('API Request', {
      method: config.method?.toUpperCase(),
      url: config.url,
      params: config.params,
      data: config.data,
      headers: {
        ...config.headers,
        Authorization: config.headers.Authorization ? 'Bearer ***' : undefined,
      },
    })

    return config
  },
  (error: any) => {
    logger.error('Request Error', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
axiosService.interceptors.response.use(
  (response: AxiosResponse) => {
    const res = response.data

    // Log API response
    logger.debug('API Response', {
      method: response.config.method?.toUpperCase(),
      url: response.config.url,
      status: response.status,
      data: res,
    })

    // 如果响应包含 code 字段，处理业务错误
    if (res.code !== undefined) {
      if (res.code === 200) {
        return res.data
      } else {
        const errorMsg = res.message || '请求失败'
        logger.warn('API Business Error', {
          url: response.config.url,
          code: res.code,
          message: errorMsg,
        })
        ElMessage.error(errorMsg)
        return Promise.reject(new Error(errorMsg))
      }
    }

    return res
  },
  (error: any) => {
    logger.error('API Error', {
      url: error.config?.url,
      method: error.config?.method?.toUpperCase(),
      status: error.response?.status,
      message: error.message,
      data: error.response?.data,
    })

    if (error.response) {
      const { status, data } = error.response

      switch (status) {
        case 401:
          ElMessage.error('登录已过期，请重新登录')
          const userStore = useUserStore()
          userStore.logout()
          window.location.href = '/login'
          break
        case 403:
          ElMessage.error('没有权限访问')
          break
        case 404:
          ElMessage.error('请求的资源不存在')
          break
        case 500:
          ElMessage.error('服务器错误')
          break
        default:
          ElMessage.error(data?.message || '请求失败')
      }
    } else {
      ElMessage.error('网络连接失败')
    }

    return Promise.reject(error)
  }
)

export default service

// 导出常用的请求方法
export function request<T = any>(config: AxiosRequestConfig): Promise<T> {
  return service.request(config)
}

export function get<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
  return service.get(url, config)
}

export function post<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
  return service.post(url, data, config)
}

export function put<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
  return service.put(url, data, config)
}

export function del<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
  return service.delete(url, config)
}
