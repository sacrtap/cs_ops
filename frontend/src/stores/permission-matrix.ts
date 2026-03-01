/**
 * 权限矩阵 Pinia Store
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import {
  getPermissionMatrix,
  updatePermission as updatePermissionApi,
  bulkUpdatePermissions,
  checkPermission as checkPermissionApi,
  clearCache,
} from '@/api/permission-matrix'
import { useAuthStore } from './auth'
import type { RolePermissions, ModulePermissions } from '@/types/permission-matrix'

/**
 * 权限矩阵 Store
 *
 * 管理功能权限矩阵的状态
 */
export const usePermissionMatrixStore = defineStore('permission-matrix', () => {
  // State
  const permissions = ref<Record<string, RolePermissions>>({})
  const loading = ref(false)
  const lastUpdated = ref<Date | null>(null)

  // Getters
  /**
   * 获取当前用户角色的权限
   */
  const currentUserPermissions = computed<RolePermissions>(() => {
    const authStore = useAuthStore()
    const role = authStore.user?.role || 'sales'
    return permissions.value[role] || {}
  })

  /**
   * 检查当前用户是否有某模块的某操作权限
   */
  const hasPermission = computed(() => {
    return (module: string, action: string): boolean => {
      const rolePermissions = currentUserPermissions.value

      // 如果模块不存在，返回 false
      if (!rolePermissions[module]) {
        return false
      }

      // 如果操作不存在，返回 false
      if (rolePermissions[module][action] === undefined) {
        return false
      }

      return rolePermissions[module][action]
    }
  })

  /**
   * 检查是否有某模块的读取权限
   */
  const canRead = computed(() => {
    return (module: string): boolean => hasPermission.value(module, 'read')
  })

  /**
   * 检查是否有某模块的创建权限
   */
  const canCreate = computed(() => {
    return (module: string): boolean => hasPermission.value(module, 'create')
  })

  /**
   * 检查是否有某模块的更新权限
   */
  const canUpdate = computed(() => {
    return (module: string): boolean => hasPermission.value(module, 'update')
  })

  /**
   * 检查是否有某模块的删除权限
   */
  const canDelete = computed(() => {
    return (module: string): boolean => hasPermission.value(module, 'delete')
  })

  /**
   * 检查是否是 Admin 角色
   */
  const isAdmin = computed(() => {
    const authStore = useAuthStore()
    return authStore.user?.role === 'admin'
  })

  // Actions
  /**
   * 加载权限矩阵
   */
  async function loadPermissions() {
    if (loading.value) {
      return
    }

    loading.value = true
    try {
      const data = await getPermissionMatrix()
      permissions.value = data
      lastUpdated.value = new Date()
    } catch (error) {
      console.error('Failed to load permission matrix:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  /**
   * 更新单个权限
   */
  async function updatePermission(role: string, module: string, action: string, granted: boolean) {
    try {
      await updatePermissionApi(role, module, action, granted)

      // 更新本地状态
      if (!permissions.value[role]) {
        permissions.value[role] = {}
      }
      if (!permissions.value[role][module]) {
        permissions.value[role][module] = {}
      }
      permissions.value[role][module][action] = granted

      // 清除缓存
      await clearCache(role)

      // 更新时间
      lastUpdated.value = new Date()
    } catch (error) {
      console.error('Failed to update permission:', error)
      throw error
    }
  }

  /**
   * 批量更新权限
   */
  async function bulkUpdate(
    permissionList: Array<{ role: string; module: string; action: string; granted: boolean }>
  ) {
    try {
      const count = await bulkUpdatePermissions(permissionList)

      // 更新本地状态
      permissionList.forEach(({ role, module, action, granted }) => {
        if (!permissions.value[role]) {
          permissions.value[role] = {}
        }
        if (!permissions.value[role][module]) {
          permissions.value[role][module] = {}
        }
        permissions.value[role][module][action] = granted
      })

      // 清除所有缓存
      await clearCache()

      // 更新时间
      lastUpdated.value = new Date()

      return count
    } catch (error) {
      console.error('Failed to bulk update permissions:', error)
      throw error
    }
  }

  /**
   * 检查权限（实时查询）
   */
  async function checkPermission(module: string, action: string): Promise<boolean> {
    try {
      const result = await checkPermissionApi(module, action)
      return result.granted
    } catch (error) {
      console.error('Failed to check permission:', error)
      return false
    }
  }

  /**
   * 刷新权限（强制重新加载）
   */
  async function refreshPermissions() {
    await clearCache()
    await loadPermissions()
  }

  /**
   * 重置 Store
   */
  function reset() {
    permissions.value = {}
    loading.value = false
    lastUpdated.value = null
  }

  return {
    // State
    permissions,
    loading,
    lastUpdated,

    // Getters
    currentUserPermissions,
    hasPermission,
    canRead,
    canCreate,
    canUpdate,
    canDelete,
    isAdmin,

    // Actions
    loadPermissions,
    updatePermission,
    bulkUpdate,
    checkPermission,
    refreshPermissions,
    reset,
  }
})
