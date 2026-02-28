/**
 * JWT Token 工具函数
 *
 * 功能：
 * - Token 解码（解析 payload）
 * - Token 过期检查
 * - Token 有效期计算
 * - 自动刷新时间计算
 */

export interface JWTPayload {
  sub: string // 用户 ID
  username: string // 用户名
  role?: string // 用户角色
  exp: number // 过期时间（秒时间戳）
  iat: number // 签发时间（秒时间戳）
  type: string // Token 类型（access/refresh）
  jti?: string // JWT ID（防重放）
}

/**
 * 解码 JWT Token（Base64）
 * 注意：这不验证签名，只解析内容
 *
 * @param token JWT Token
 * @returns 解析后的 payload
 */
export function decodeJWT(token: string): JWTPayload {
  try {
    const parts = token.split('.')
    if (parts.length !== 3) {
      throw new Error('无效的 Token 格式')
    }

    // 解码 payload（第二部分）
    const payload = parts[1]
    const decoded = atob(payload)
    return JSON.parse(decoded)
  } catch (error) {
    console.error('Token 解码失败:', error)
    throw new Error('Token 解析失败')
  }
}

/**
 * 检查 Token 是否已过期
 *
 * @param token JWT Token
 * @returns true 表示已过期，false 表示有效
 */
export function isTokenExpired(token: string): boolean {
  try {
    const payload = decodeJWT(token)
    const now = Math.floor(Date.now() / 1000)
    return payload.exp <= now
  } catch {
    // 解析失败视为过期
    return true
  }
}

/**
 * 检查 Token 是否即将过期
 *
 * @param token JWT Token
 * @param thresholdSeconds 阈值（秒），默认 5 分钟
 * @returns true 表示即将过期，false 表示还有效
 */
export function isTokenExpiringSoon(token: string, thresholdSeconds: number = 300): boolean {
  try {
    const payload = decodeJWT(token)
    const now = Math.floor(Date.now() / 1000)
    const timeUntilExpiry = payload.exp - now
    return timeUntilExpiry <= thresholdSeconds
  } catch {
    // 解析失败视为即将过期
    return true
  }
}

/**
 * 获取 Token 剩余有效时间（秒）
 *
 * @param token JWT Token
 * @returns 剩余秒数，-1 表示已过期
 */
export function getTokenTimeLeft(token: string): number {
  try {
    const payload = decodeJWT(token)
    const now = Math.floor(Date.now() / 1000)
    return payload.exp - now
  } catch {
    return -1
  }
}

/**
 * 获取 Token 过期时间戳
 *
 * @param token JWT Token
 * @returns 过期时间戳（毫秒）
 */
export function getTokenExpiryTime(token: string): number {
  try {
    const payload = decodeJWT(token)
    return payload.exp * 1000 // 转换为毫秒
  } catch {
    return 0
  }
}

/**
 * 计算自动刷新的最佳时间
 * 在 Token 过期前 5 分钟触发刷新
 *
 * @param token JWT Token
 * @returns 距离刷新的毫秒数，-1 表示应立即刷新
 */
export function getAutoRefreshDelay(token: string): number {
  try {
    const payload = decodeJWT(token)
    const now = Math.floor(Date.now() / 1000)
    const timeUntilExpiry = payload.exp - now

    // 如果已过期或即将过期（< 5 分钟），立即刷新
    if (timeUntilExpiry <= 300) {
      return 0
    }

    // 在过期前 5 分钟刷新
    const refreshDelay = (timeUntilExpiry - 300) * 1000
    return refreshDelay
  } catch {
    return 0
  }
}

/**
 * 获取 Token 类型
 *
 * @param token JWT Token
 * @returns 'access' | 'refresh' | 'unknown'
 */
export function getTokenType(token: string): string {
  try {
    const payload = decodeJWT(token)
    return payload.type || 'unknown'
  } catch {
    return 'unknown'
  }
}

/**
 * 获取 Token 中的用户信息
 *
 * @param token JWT Token
 * @returns 用户信息对象
 */
export function getTokenUserInfo(token: string): {
  userId: string
  username: string
  role?: string
} {
  try {
    const payload = decodeJWT(token)
    return {
      userId: payload.sub,
      username: payload.username,
      role: payload.role,
    }
  } catch {
    throw new Error('Token 解析失败')
  }
}
