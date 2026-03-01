/**
 * 角色管理状态管理 - Pinia Store
 *
 * 功能:
 * - 角色列表管理
 * - 角色详情管理
 * - 角色权限配置
 * - 角色 CRUD 操作
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import {
  getRoles as getRolesApi,
  getRole as getRoleApi,
  getRolePermissions as getRolePermissionsApi,
  getRoleStats as getRoleStatsApi,
  createRole as createRoleApi,
  updateRole as updateRoleApi,
  deleteRole as deleteRoleApi,
  updateRolePermissions as updateRolePermissionsApi,
} from '@/api/role-management'
import type {
  Role,
  RoleWithPermissions,
  RoleStats,
  PermissionMatrix,
  RoleCreateRequest,
  RoleUpdateRequest,
} from '@/types/role-management'

export const useRoleManagementStore = defineStore('roleManagement', () => {
  // ==================== State ====================

  const roles = ref<Role[]>([])
  const currentRole = ref<RoleWithPermissions | null>(null)
  const stats = ref<RoleStats | null>(null)
  const isLoading = ref(false)
  const isSaving = ref(false)
  const error = ref<string | null>(null)

  // ==================== Getters ====================

  /** 获取所有角色 */
  const allRoles = computed(() => roles.value)

  /** 获取活跃角色 */
  const activeRoles = computed(() => roles.value.filter((r) => r.status === 'active'))

  /** 获取系统默认角色 */
  const systemRoles = computed(() => {
    const defaultNames = ['admin', 'manager', 'specialist', 'sales']
    return roles.value.filter((r) => defaultNames.includes(r.name))
  })

  /** 获取自定义角色 */
  const customRoles = computed(() => {
    const defaultNames = ['admin', 'manager', 'specialist', 'sales']
    return roles.value.filter((r) => !defaultNames.includes(r.name))
  })

  /** 角色是否可以删除 */
  const isRoleDeletable = computed(() => {
    return (role: Role): boolean => {
      const defaultNames = ['admin', 'manager', 'specialist', 'sales']
      return !defaultNames.includes(role.name)
    }
  })

  /** 角色是否可以编辑权限 */
  const isRolePermissionEditable = computed(() => {
    return (role: Role): boolean => {
      return role.name !== 'admin' // Admin 角色权限不可修改
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
   * 加载角色统计信息
   */
  async function loadRoleStats() {
    isLoading.value = true
    error.value = null

    try {
      const response = await getRoleStatsApi()
      stats.value = response.data
      return { success: true }
    } catch (err) {
      error.value = err instanceof Error ? err.message : '加载角色统计失败'
      return { success: false, error: error.value }
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 加载角色详情（包含权限）
   */
  async function loadRoleWithPermissions(roleId: number) {
    isLoading.value = true
    error.value = null

    try {
      // 获取角色详情
      const roleResponse = await getRoleApi(roleId)

      // 获取角色权限
      const permissionsResponse = await getRolePermissionsApi(roleId)

      // 合并数据
      currentRole.value = {
        ...roleResponse.data,
        permissions: permissionsResponse.data,
      }

      return { success: true, role: currentRole.value }
    } catch (err) {
      error.value = err instanceof Error ? err.message : '加载角色详情失败'
      return { success: false, error: error.value }
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 创建角色
   */
  async function createRole(data: RoleCreateRequest) {
    isSaving.value = true
    error.value = null

    try {
      const response = await createRoleApi(data)

      // 刷新角色列表
      await loadRoles()

      return { success: true, message: response.message }
    } catch (err) {
      error.value = err instanceof Error ? err.message : '创建角色失败'
      return { success: false, error: error.value }
    } finally {
      isSaving.value = false
    }
  }

  /**
   * 更新角色
   */
  async function updateRole(roleId: number, data: RoleUpdateRequest) {
    isSaving.value = true
    error.value = null

    try {
      const response = await updateRoleApi(roleId, data)

      // 更新本地缓存
      const index = roles.value.findIndex((r) => r.id === roleId)
      if (index !== -1) {
        roles.value[index] = { ...roles.value[index], ...data }
      }

      // 如果当前角色被更新，也更新 currentRole
      if (currentRole.value?.id === roleId) {
        currentRole.value = { ...currentRole.value, ...data }
      }

      return { success: true, message: response.message }
    } catch (err) {
      error.value = err instanceof Error ? err.message : '更新角色失败'
      return { success: false, error: error.value }
    } finally {
      isSaving.value = false
    }
  }

  /**
   * 删除角色
   */
  async function deleteRole(roleId: number) {
    isSaving.value = true
    error.value = null

    try {
      const response = await deleteRoleApi(roleId)

      // 从本地缓存中移除
      roles.value = roles.value.filter((r) => r.id !== roleId)

      // 如果当前角色被删除，清空 currentRole
      if (currentRole.value?.id === roleId) {
        currentRole.value = null
      }

      return { success: true, message: response.message }
    } catch (err) {
      error.value = err instanceof Error ? err.message : '删除角色失败'
      return { success: false, error: error.value }
    } finally {
      isSaving.value = false
    }
  }

  /**
   * 更新角色权限
   */
  async function updateRolePermissions(roleId: number, permissions: PermissionMatrix) {
    isSaving.value = true
    error.value = null

    try {
      const response = await updateRolePermissionsApi(roleId, { permissions })

      // 更新本地缓存
      const index = roles.value.findIndex((r) => r.id === roleId)
      if (index !== -1) {
        // 只更新权限部分
        roles.value[index] = { ...roles.value[index] }
      }

      // 更新当前角色
      if (currentRole.value?.id === roleId) {
        currentRole.value = {
          ...currentRole.value,
          permissions,
        }
      }

      return { success: true, message: response.message }
    } catch (err) {
      error.value = err instanceof Error ? err.message : '更新角色权限失败'
      return { success: false, error: error.value }
    } finally {
      isSaving.value = false
    }
  }

  /**
   * 清除角色数据
   */
  function clearRoleData() {
    roles.value = []
    currentRole.value = null
    stats.value = null
    error.value = null
  }

  return {
    // State
    roles,
    currentRole,
    stats,
    isLoading,
    isSaving,
    error,
    // Getters
    allRoles,
    activeRoles,
    systemRoles,
    customRoles,
    isRoleDeletable,
    isRolePermissionEditable,
    // Actions
    loadRoles,
    loadRoleStats,
    loadRoleWithPermissions,
    createRole,
    updateRole,
    deleteRole,
    updateRolePermissions,
    clearRoleData,
  }
})
