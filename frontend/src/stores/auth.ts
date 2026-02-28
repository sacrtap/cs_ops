/**
 * 认证状态管理 - Pinia Store
 *
 * 功能：
 * - 用户登录/登出
 * - Token 管理（存储、刷新）
 * - 认证状态维护
 * - 自动 Token 刷新（过期前 5 分钟）
 * - 并发刷新控制（防重放）
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import {
  login as loginApi,
  refreshToken as refreshTokenApi,
  logout as logoutApi,
  storeTokens,
  getStoredTokens,
} from '@/api/auth'
import { getAutoRefreshDelay } from '@/utils/token'
import type { User, LoginForm } from '@/types/auth'

export const useAuthStore = defineStore('auth', () => {
  // ==================== State ====================

  const user = ref<User | null>(null)
  const accessToken = ref<string | null>(null)
  const refreshTokenStr = ref<string | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // 并发刷新控制
  let refreshPromise: Promise<{ success: boolean }> | null = null
  let autoRefreshTimer: ReturnType<typeof setTimeout> | null = null

  // 从本地存储恢复 Token
  const stored = getStoredTokens()
  if (stored.accessToken) {
    accessToken.value = stored.accessToken
    // 启动自动刷新定时器
    scheduleAutoRefresh()
  }
  if (stored.refreshToken) {
    refreshTokenStr.value = stored.refreshToken
  }

  // ==================== Getters ====================

  /** 是否已认证 */
  const isAuthenticated = computed(() => {
    return !!accessToken.value && !!user.value
  })

  /** 用户角色 */
  const userRole = computed(() => {
    return user.value?.role || null
  })

  /** 用户名 */
  const username = computed(() => {
    return user.value?.username || null
  })

  /** 是否有权限（检查角色） */
  const hasRole = computed(() => {
    return (roles: string | string[]) => {
      if (!userRole.value) return false
      const roleList = Array.isArray(roles) ? roles : [roles]
      return roleList.includes(userRole.value)
    }
  })

  // ==================== Actions ====================

  /**
   * 用户登录
   * @param form 登录表单数据
   */
  async function login(form: LoginForm) {
    isLoading.value = true
    error.value = null

    try {
      const response = await loginApi(form)

      // 保存 Token
      accessToken.value = response.access_token
      refreshTokenStr.value = response.refresh_token
      storeTokens(response.access_token, response.refresh_token)

      // 保存用户信息
      user.value = response.user

      return { success: true }
    } catch (err) {
      error.value = err instanceof Error ? err.message : '登录失败'
      return { success: false, error: error.value }
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 刷新 Token（带并发控制）
   * 防止并发请求导致多次刷新
   */
  async function refreshToken(): Promise<{ success: boolean }> {
    // 如果没有刷新 Token，抛出错误
    if (!refreshTokenStr.value) {
      throw new Error('没有刷新 Token')
    }

    // 如果已有刷新请求在进行中，返回同一个 Promise
    if (refreshPromise) {
      return refreshPromise
    }

    // 创建新的刷新请求
    refreshPromise = (async () => {
      try {
        // 确保 refreshToken 不为 null
        if (!refreshTokenStr.value) {
          throw new Error('没有刷新 Token')
        }

        const response = await refreshTokenApi({
          refresh_token: refreshTokenStr.value,
        })

        // 更新 Token
        accessToken.value = response.access_token
        refreshTokenStr.value = response.refresh_token
        storeTokens(response.access_token, response.refresh_token)

        // 重新设置自动刷新定时器
        scheduleAutoRefresh()

        return { success: true }
      } catch (err) {
        // 刷新失败，清除认证状态
        logout()
        throw err
      } finally {
        // 清除刷新锁
        refreshPromise = null
      }
    })()

    return refreshPromise
  }

  /**
   * 计划自动刷新
   * 在 Token 过期前 5 分钟触发刷新
   */
  function scheduleAutoRefresh() {
    // 清除旧的定时器
    if (autoRefreshTimer) {
      clearTimeout(autoRefreshTimer)
      autoRefreshTimer = null
    }

    // 如果没有 Access Token，不设置定时器
    if (!accessToken.value) {
      return
    }

    // 计算自动刷新延迟
    const delay = getAutoRefreshDelay(accessToken.value)

    // 如果应立即刷新（0 或负数）
    if (delay <= 0) {
      // Token 已过期或即将过期，立即刷新
      refreshToken().catch(console.error)
      return
    }

    // 设置定时器
    autoRefreshTimer = setTimeout(() => {
      console.log('[Auth] 自动刷新 Token')
      refreshToken().catch(console.error)
    }, delay)

    console.log(`[Auth] 自动刷新已计划，${delay / 1000}秒后执行`)
  }

  /**
   * 清除自动刷新定时器
   * 在登出时调用
   */
  function clearAutoRefreshTimer() {
    if (autoRefreshTimer) {
      clearTimeout(autoRefreshTimer)
      autoRefreshTimer = null
    }
  }

  /**
   * 退出登录
   * 调用服务端登出 API 并清除本地状态
   */
  async function logout() {
    // 清除自动刷新定时器
    clearAutoRefreshTimer()

    // 调用服务端登出 API（使 Token 失效）
    if (refreshTokenStr.value) {
      try {
        // 调用登出 API
        await logoutApi()
      } catch (err) {
        // 登出 API 失败也继续清除本地状态
        console.warn('服务端登出失败:', err)
      }
    }

    // 清除本地状态
    user.value = null
    accessToken.value = null
    refreshTokenStr.value = null
    error.value = null
    refreshPromise = null
    autoRefreshTimer = null

    // 清除本地存储
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')

    // 跳转到登录页（在组件中调用）
    // router.push('/login')
  }

  /**
   * 清除错误
   */
  function clearError() {
    error.value = null
  }

  /**
   * 从本地存储恢复认证状态
   * 可以在应用启动时调用
   */
  async function restoreAuth() {
    const stored = getStoredTokens()

    if (stored.accessToken && stored.refreshToken) {
      try {
        await refreshToken()
        // Token 刷新成功后，user 信息会在刷新接口的响应中返回
        // 如果需要，可以在这里添加获取用户信息的逻辑
      } catch {
        // 恢复失败，清除认证状态
        logout()
      }
    }
  }

  // ==================== 导出 ====================

  return {
    // State
    user,
    accessToken,
    refreshTokenStr, // Token 字符串
    isLoading,
    error,

    // Getters
    isAuthenticated,
    userRole,
    username,
    hasRole,

    // Actions
    login,
    refreshToken, // 刷新 Token 方法
    logout,
    clearError,
    restoreAuth,
    scheduleAutoRefresh, // 计划自动刷新
    clearAutoRefreshTimer, // 清除自动刷新定时器（组件卸载时使用）
  }
})
