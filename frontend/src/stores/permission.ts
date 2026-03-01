/**
 * 权限状态管理 - Pinia Store
 *
 * 功能:
 * - 角色列表管理
 * - 权限矩阵管理
 * - 权限检查
 * - 用户角色更新
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import {
  getRoles as getRolesApi,
  getPermissionMatrix as getPermissionMatrixApi,
  checkPermission as checkPermissionApi,
  updatePermissionMatrix as updatePermissionMatrixApi,
  updateUserRole as updateUserRoleApi,
} from '@/api/permission'
import type {
  Role,
  PermissionMatrix,
  PermissionResource,
  PermissionAction,
} from '@/types/permission'

export const usePermissionStore = defineStore('permission', () => {
  // ==================== State ====================

  const roles = ref<Role[]>([])
  const matrix = ref<PermissionMatrix>({})
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // ==================== Getters ====================

  /** 获取所有角色 */
  const allRoles = computed(() => roles.value)

  /** 获取角色级别 */
  const getRoleLevel = computed(() => {
    return (roleName: string): number => {
      const role = roles.value.find((r) => r.role === roleName)
      return role?.level || 0
    }
  })

  /** 检查是否有权限 */
  const hasPermission = computed(() => {
    return (resource: PermissionResource, action: PermissionAction): boolean => {
      // 如果是 admin，直接返回 true
      const currentRole = localStorage.getItem('user_role')
      if (currentRole === 'admin') {
        return true
      }

      // 确保 currentRole 不为 null
      if (!currentRole) {
        return false
      }

      // 查询权限矩阵
      const rolePermissions = matrix.value[currentRole]
      if (!rolePermissions) {
        return false
      }
      const resourcePermissions = rolePermissions[resource]
      if (!resourcePermissions) {
        return false
      }
      return resourcePermissions.includes(action)
    }
  })

  /** 检查是否有任意一个权限 */
  const hasAnyPermission = computed(() => {
    return (permissions: Array<[PermissionResource, PermissionAction]>): boolean => {
      return permissions.some(([resource, action]) => hasPermission.value(resource, action))
    }
  })

  /** 检查是否拥有所有权限 */
  const hasAllPermissions = computed(() => {
    return (permissions: Array<[PermissionResource, PermissionAction]>): boolean => {
      return permissions.every(([resource, action]) => hasPermission.value(resource, action))
    }
  })

  // ==================== Actions ====================

  /**
   * 加载角色列表
   */
  async function loadRoles() {
    if (roles.value.length > 0) {
      // 已有数据，直接返回
      return { success: true }
    }

    isLoading.value = true
    error.value = null

    try {
      const response = await getRolesApi()
      roles.value = response.data
      return { success: true }
    } catch (err) {
      error.value = err instanceof Error ? err.message : '加载角色列表失败'
      return { success: false, error: error.value }
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 加载权限矩阵
   */
  async function loadPermissionMatrix() {
    isLoading.value = true
    error.value = null

    try {
      const response = await getPermissionMatrixApi()
      matrix.value = response.data
      return { success: true }
    } catch (err) {
      error.value = err instanceof Error ? err.message : '加载权限矩阵失败'
      return { success: false, error: error.value }
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 检查权限
   */
  async function checkPermission(resource: PermissionResource, action: PermissionAction) {
    try {
      const response = await checkPermissionApi({ resource, action })
      return { success: response.data.has_permission }
    } catch (err) {
      return { success: false, error: err instanceof Error ? err.message : '权限检查失败' }
    }
  }

  /**
   * 更新权限矩阵（仅 Admin）
   */
  async function updatePermissionMatrix(
    role: string,
    resource: PermissionResource,
    action: PermissionAction,
    enabled: boolean
  ) {
    isLoading.value = true
    error.value = null

    try {
      const response = await updatePermissionMatrixApi({ role, resource, action, enabled })

      // 更新本地缓存
      if (enabled) {
        if (!matrix.value[role]) {
          matrix.value[role] = {}
        }
        if (!matrix.value[role][resource]) {
          matrix.value[role][resource] = []
        }
        if (!matrix.value[role][resource].includes(action)) {
          matrix.value[role][resource].push(action)
        }
      } else {
        if (matrix.value[role] && matrix.value[role][resource]) {
          matrix.value[role][resource] = matrix.value[role][resource].filter((a) => a !== action)
        }
      }

      return { success: response.data.success }
    } catch (err) {
      error.value = err instanceof Error ? err.message : '更新权限矩阵失败'
      return { success: false, error: error.value }
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 更新用户角色
   */
  async function updateUserRole(userId: number, newRole: string) {
    isLoading.value = true
    error.value = null

    try {
      const response = await updateUserRoleApi(userId, newRole)
      return { success: response.data.success, user: response.data.user }
    } catch (err) {
      error.value = err instanceof Error ? err.message : '更新用户角色失败'
      return { success: false, error: error.value }
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 清除权限数据（登出时调用）
   */
  function clearPermissionData() {
    roles.value = []
    matrix.value = {}
    error.value = null
  }

  // ==================== 初始化 ====================

  // 不需要自动加载，在需要时手动调用 loadRoles 和 loadPermissionMatrix

  return {
    // State
    roles,
    matrix,
    isLoading,
    error,
    // Getters
    allRoles,
    getRoleLevel,
    hasPermission,
    hasAnyPermission,
    hasAllPermissions,
    // Actions
    loadRoles,
    loadPermissionMatrix,
    checkPermission,
    updatePermissionMatrix,
    updateUserRole,
    clearPermissionData,
  }
})
