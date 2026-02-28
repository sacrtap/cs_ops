/**
 * HTTP 请求工具封装
 * 
 * 功能：
 * - 统一错误处理
 * - Token 自动注入
 * - Token 过期自动刷新
 * - 请求拦截器
 */
import axios, { AxiosError, AxiosRequestConfig, AxiosResponse } from 'axios'
import { useAuthStore } from '@/stores/auth'
import type { ErrorResponse } from '@/types/auth'

// 创建 axios 实例
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器 - 注入 Token
apiClient.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore()
    const token = authStore.accessToken

    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }

    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器 - 处理 Token 过期
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError<ErrorResponse>) => {
    const authStore = useAuthStore()
    const originalRequest = error.config as AxiosRequestConfig & { _retry?: boolean }

    // 如果是 401 错误且没有重试过
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        // 尝试刷新 Token
        await authStore.refreshToken()

        // 重试原请求
        const token = authStore.accessToken
        if (token && originalRequest.headers) {
          originalRequest.headers.Authorization = `Bearer ${token}`
        }
        return apiClient(originalRequest)
      } catch (refreshError) {
        // 刷新失败，跳转到登录页
        authStore.logout()
        return Promise.reject(refreshError)
      }
    }

    // 其他错误，提取错误信息
    const errorMessage = error.response?.data?.error?.message || '网络请求失败'
    return Promise.reject(new Error(errorMessage))
  }
)

// 导出请求方法
export const api = {
  /** GET 请求 */
  get<T>(url: string, config?: AxiosRequestConfig) {
    return apiClient.get<T>(url, config)
  },

  /** POST 请求 */
  post<T>(url: string, data?: unknown, config?: AxiosRequestConfig) {
    return apiClient.post<T>(url, data, config)
  },

  /** PUT 请求 */
  put<T>(url: string, data?: unknown, config?: AxiosRequestConfig) {
    return apiClient.put<T>(url, data, config)
  },

  /** DELETE 请求 */
  delete<T>(url: string, config?: AxiosRequestConfig) {
    return apiClient.delete<T>(url, config)
  },

  /** 下载文件 */
  download(url: string, config?: AxiosRequestConfig) {
    return apiClient.get(url, {
      ...config,
      responseType: 'blob',
    })
  },
}

export default apiClient
