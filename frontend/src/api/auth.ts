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
 * 注意：这是客户端操作，只需要清除本地存储
 * 如果需要服务端失效 Token，可以添加黑名单机制
 */
export function logout() {
  // 清除本地 Token
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
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
