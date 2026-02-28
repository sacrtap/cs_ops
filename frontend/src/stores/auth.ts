/**
 * 认证状态管理 - Pinia Store
 * 
 * 功能：
 * - 用户登录/登出
 * - Token 管理（存储、刷新）
 * - 认证状态维护
 * - 自动 Token 刷新
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as loginApi, refreshToken as refreshTokenApi, logout as logoutApi, storeTokens, getStoredTokens } from '@/api/auth'
import type { User, LoginForm } from '@/types/auth'

export const useAuthStore = defineStore('auth', () => {
  // ==================== State ====================

  const user = ref<User | null>(null)
  const accessToken = ref<string | null>(null)
  const refreshTokenStr = ref<string | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // 从本地存储恢复 Token
  const stored = getStoredTokens()
  if (stored.accessToken) {
    accessToken.value = stored.accessToken
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
   * 刷新 Token
   */
  async function refreshToken() {
    if (!refreshTokenStr.value) {
      throw new Error('没有刷新 Token')
    }

    try {
      const response = await refreshTokenApi({
        refresh_token: refreshTokenStr.value,
      })

      // 更新 Token
      accessToken.value = response.access_token
      refreshTokenStr.value = response.refresh_token
      storeTokens(response.access_token, response.refresh_token)

      return { success: true }
    } catch (err) {
      // 刷新失败，清除认证状态
      logout()
      throw err
    }
  }

  /**
   * 退出登录
   */
  function logout() {
    // 清除本地状态
    user.value = null
    accessToken.value = null
    refreshTokenStr.value = null
    error.value = null

    // 清除本地存储
    logoutApi()

    // 跳转到登录页
    // router.push('/login') // 在组件中调用
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
    refreshToken: refreshTokenStr,
    isLoading,
    error,

    // Getters
    isAuthenticated,
    userRole,
    username,
    hasRole,

    // Actions
    login,
    refreshToken,
    logout,
    clearError,
    restoreAuth,
  }
})
