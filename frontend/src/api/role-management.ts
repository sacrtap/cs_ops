/**
 * 角色管理 API 客户端
 */
import { api } from '@/utils/request'
import type {
  RoleListResponse,
  RoleResponse,
  RolePermissionsResponse,
  RoleStatsResponse,
  RoleActionResponse,
  RoleCreateRequest,
  RoleUpdateRequest,
  RolePermissionsUpdateRequest,
} from '@/types/role-management'

const API_PREFIX = '/roles'

/**
 * 获取所有角色列表
 */
export async function getRoles() {
  const response = await api.get<RoleListResponse>(`${API_PREFIX}`)
  return response.data
}

/**
 * 获取角色详情
 */
export async function getRole(roleId: number) {
  const response = await api.get<RoleResponse>(`${API_PREFIX}/${roleId}`)
  return response.data
}

/**
 * 获取角色权限
 */
export async function getRolePermissions(roleId: number) {
  const response = await api.get<RolePermissionsResponse>(`${API_PREFIX}/${roleId}/permissions`)
  return response.data
}

/**
 * 获取角色统计信息
 */
export async function getRoleStats() {
  const response = await api.get<RoleStatsResponse>(`${API_PREFIX}/stats`)
  return response.data
}

/**
 * 创建角色
 */
export async function createRole(data: RoleCreateRequest) {
  const response = await api.post<RoleActionResponse>(`${API_PREFIX}`, data)
  return response.data
}

/**
 * 更新角色
 */
export async function updateRole(roleId: number, data: RoleUpdateRequest) {
  const response = await api.put<RoleActionResponse>(`${API_PREFIX}/${roleId}`, data)
  return response.data
}

/**
 * 删除角色
 */
export async function deleteRole(roleId: number) {
  const response = await api.delete<RoleActionResponse>(`${API_PREFIX}/${roleId}`)
  return response.data
}

/**
 * 更新角色权限
 */
export async function updateRolePermissions(roleId: number, data: RolePermissionsUpdateRequest) {
  const response = await api.put<RoleActionResponse>(`${API_PREFIX}/${roleId}/permissions`, data)
  return response.data
}
