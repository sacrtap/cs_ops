/**
 * 认证 API 客户端
 */
import { api } from '@/utils/request'
import type {
  LoginRequest,
  LoginResponse,
  RefreshTokenRequest,
  RefreshTokenResponse,
} from '@/types/auth'

const API_PREFIX = '/auth'

/**
 * 用户登录
 * @param data 登录请求数据
 * @returns 登录响应（包含 Token 和用户信息）
 */
export async function login(data: LoginRequest) {
  const response = await api.post<LoginResponse>(`${API_PREFIX}/login`, data)
  return response.data.data
}

/**
 * 刷新 Token
 * @param data 刷新 Token 请求数据
 * @returns 新的 Token 响应
 */
export async function refreshToken(data: RefreshTokenRequest) {
  const response = await api.post<RefreshTokenResponse>(`${API_PREFIX}/refresh`, data)
  return response.data.data
}

/**
 * 退出登录
 * 调用服务端 API 使 Token 失效
 */
export async function logout(data?: { refresh_token: string }) {
  if (data) {
    // 调用服务端登出 API
    await api.post(`${API_PREFIX}/logout`, data)
  }
  // 清除本地存储（在 store 中处理）
}

/**
 * 获取本地存储的 Token
 */
export function getStoredTokens() {
  const accessToken = localStorage.getItem('access_token')
  const refreshToken = localStorage.getItem('refresh_token')
  return { accessToken, refreshToken }
}

/**
 * 存储 Token 到本地
 */
export function storeTokens(accessToken: string, refreshToken: string) {
  localStorage.setItem('access_token', accessToken)
  localStorage.setItem('refresh_token', refreshToken)
}
