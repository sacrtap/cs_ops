/**
 * 认证相关的 TypeScript 类型定义
 */

// ==================== 请求类型 ====================

/** 登录请求 */
export interface LoginRequest {
  username: string
  password: string
}

/** 刷新 Token 请求 */
export interface RefreshTokenRequest {
  refresh_token: string
}

// ==================== 响应类型 ====================

/** 用户角色（4 级 RBAC） */
export type UserRole = 'admin' | 'manager' | 'specialist' | 'sales'

/** 用户状态 */
export type UserStatus = 'active' | 'inactive' | 'locked'

/** 用户信息 */
export interface User {
  id: number
  username: string
  real_name: string
  role: UserRole
  email?: string | null
  phone?: string | null
  status: UserStatus
  created_at: string
}

/** Token 响应 */
export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: 'bearer'
  expires_in: number
}

/** 登录响应 */
export interface LoginResponse extends TokenResponse {
  user: User
}

/** 刷新 Token 响应 */
export interface RefreshTokenResponse extends TokenResponse {}

// ==================== 错误类型 ====================

/** API 错误详情 */
export interface ErrorDetail {
  field: string
  message: string
}

/** API 错误响应 */
export interface ErrorResponse {
  error: {
    code: string
    message: string
    details?: ErrorDetail[] | null
  }
}

// ==================== 认证 Store 类型 ====================

/** 认证状态 */
export interface AuthState {
  user: User | null
  accessToken: string | null
  refreshToken: string | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
}

/** 登录表单数据 */
export interface LoginForm {
  username: string
  password: string
}
