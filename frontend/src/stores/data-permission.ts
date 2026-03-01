/**
 * 数据权限状态管理 - Pinia Store
 *
 * 功能:
 * - 管理当前用户的数据范围
 * - 管理可用数据范围列表
 * - 提供数据权限检查功能
 *
 * Story 1.4: Data Permission
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { getDataScopes, getUserDataPermission, switchDataScope } from '@/api/data-permission'
import type { DataScope, DataScopeInfo, UserDataPermission } from '@/types/data-permission'

export const useDataPermissionStore = defineStore('dataPermission', () => {
  // ==================== State ====================

  /** 当前数据范围 */
  const currentScope = ref<DataScope | null>(null)

  /** 可用的数据范围列表 */
  const availableScopes = ref<DataScopeInfo[]>([])

  /** 用户数据权限信息 */
  const userDataPermission = ref<UserDataPermission | null>(null)

  /** 加载状态 */
  const isLoading = ref(false)

  /** 错误信息 */
  const error = ref<string | null>(null)

  // ==================== Getters ====================

  /** 当前数据范围信息 */
  const currentScopeInfo = computed(() => {
    if (!currentScope.value) {
      return null
    }
    return availableScopes.value.find((scope) => scope.scope === currentScope.value) || null
  })

  /** 是否可以访问全部数据 */
  const canAccessAll = computed(() => {
    return userDataPermission.value?.can_access_all || false
  })

  /** 是否可以访问本组织数据 */
  const canAccessOrg = computed(() => {
    return userDataPermission.value?.can_access_org || false
  })

  /** 是否可以访问分配的数据 */
  const canAccessAssigned = computed(() => {
    return userDataPermission.value?.can_access_assigned || false
  })

  /** 是否可以访问个人数据 */
  const canAccessPersonal = computed(() => {
    return userDataPermission.value?.can_access_personal || false
  })

  /** 当前用户的组织 ID */
  const currentOrgId = computed(() => {
    return userDataPermission.value?.org_id || null
  })

  /** 当前用户 ID */
  const currentUserId = computed(() => {
    return userDataPermission.value?.user_id || 0
  })

  /** 数据范围标签 */
  const dataScopeLabel = computed(() => {
    const scope = currentScopeInfo.value
    return scope ? scope.label : '未知数据范围'
  })

  // ==================== Actions ====================

  /**
   * 加载用户数据权限信息
   */
  async function loadUserDataPermission() {
    if (userDataPermission.value) {
      // 已有数据，直接返回
      return { success: true }
    }

    isLoading.value = true
    error.value = null

    try {
      const response = await getUserDataPermission()
      userDataPermission.value = response.data
      currentScope.value = response.data.data_scope
      return { success: true }
    } catch (err) {
      error.value = err instanceof Error ? err.message : '加载用户数据权限失败'
      return { success: false, error: error.value }
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 加载可用数据范围列表
   */
  async function loadDataScopes() {
    if (availableScopes.value.length > 0) {
      // 已有数据，直接返回
      return { success: true }
    }

    isLoading.value = true
    error.value = null

    try {
      const response = await getDataScopes()
      availableScopes.value = response.data
      return { success: true }
    } catch (err) {
      error.value = err instanceof Error ? err.message : '加载数据范围列表失败'
      return { success: false, error: error.value }
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 切换数据范围
   *
   * @param scope 数据范围
   * @param org_id 组织 ID（可选）
   */
  async function changeDataScope(scope: DataScope, org_id?: number) {
    isLoading.value = true
    error.value = null

    try {
      const response = await switchDataScope(scope, org_id)
      userDataPermission.value = response.data
      currentScope.value = response.data.data_scope

      // 保存到 localStorage 以便持久化
      localStorage.setItem('data_scope', scope)
      if (org_id) {
        localStorage.setItem('data_scope_org_id', org_id.toString())
      }

      return { success: true }
    } catch (err) {
      error.value = err instanceof Error ? err.message : '切换数据范围失败'
      return { success: false, error: error.value }
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 初始化数据权限（在应用启动时调用）
   */
  async function initialize() {
    // 从 localStorage 恢复上次的数据范围
    const savedScope = localStorage.getItem('data_scope') as DataScope | null
    const savedOrgId = localStorage.getItem('data_scope_org_id')
    const org_id = savedOrgId ? parseInt(savedOrgId) : undefined

    // 加载用户权限和可用范围
    await Promise.all([loadUserDataPermission(), loadDataScopes()])

    // 如果有保存的范围，尝试恢复
    if (savedScope && currentScope.value !== savedScope) {
      await changeDataScope(savedScope, org_id)
    }
  }

  /**
   * 清除数据权限状态（登出时调用）
   */
  function clear() {
    currentScope.value = null
    availableScopes.value = []
    userDataPermission.value = null
    error.value = null
    localStorage.removeItem('data_scope')
    localStorage.removeItem('data_scope_org_id')
  }

  return {
    // State
    currentScope,
    availableScopes,
    userDataPermission,
    isLoading,
    error,
    // Getters
    currentScopeInfo,
    canAccessAll,
    canAccessOrg,
    canAccessAssigned,
    canAccessPersonal,
    currentOrgId,
    currentUserId,
    dataScopeLabel,
    // Actions
    loadUserDataPermission,
    loadDataScopes,
    changeDataScope,
    initialize,
    clear,
  }
})
