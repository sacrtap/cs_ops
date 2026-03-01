/**
 * 权限管理 API 客户端
 * 已集成权限继承功能
 */
import { api } from '@/utils/request'
import type {
  PermissionCheckRequest,
  PermissionMatrixUpdateRequest,
  UserRoleUpdateRequest,
  RoleListResponse,
  PermissionMatrixResponse,
  PermissionCheckResponse,
  PermissionMatrixUpdateResponse,
  UserRoleUpdateResponse,
  RoleHierarchyResponse,
  RolePermissionsResponse,
  PermissionCheckWithInheritanceResponse,
} from '@/types/permission'

const API_PREFIX = '/permissions'

/**
 * 获取所有角色列表
 */
export async function getRoles() {
  const response = await api.get<RoleListResponse>(`${API_PREFIX}/roles`)
  return response.data
}

/**
 * 获取权限矩阵
 */
export async function getPermissionMatrix() {
  const response = await api.get<PermissionMatrixResponse>(`${API_PREFIX}/matrix`)
  return response.data
}

/**
 * 检查权限
 */
export async function checkPermission(data: PermissionCheckRequest) {
  const response = await api.post<PermissionCheckResponse>(`${API_PREFIX}/check`, data)
  return response.data
}

/**
 * 更新权限矩阵（仅 Admin）
 */
export async function updatePermissionMatrix(data: PermissionMatrixUpdateRequest) {
  const response = await api.put<PermissionMatrixUpdateResponse>(`${API_PREFIX}/matrix`, data)
  return response.data
}

/**
 * 更新用户角色
 */
export async function updateUserRole(userId: number, role: string) {
  const data: UserRoleUpdateRequest = { role }
  const response = await api.put<UserRoleUpdateResponse>(`${API_PREFIX}/users/${userId}/role`, data)
  return response.data
}

// ==================== 权限继承相关 API ====================

/**
 * 获取角色层级结构
 */
export async function getRoleHierarchy() {
  const response = await api.get<RoleHierarchyResponse>('/roles/hierarchy')
  return response.data
}

/**
 * 获取角色的所有权限（包含继承权限）
 */
export async function getRolePermissions(roleName: string) {
  const response = await api.get<RolePermissionsResponse>(`/roles/${roleName}/permissions`)
  return response.data
}

/**
 * 检查权限（包含继承信息）
 */
export async function checkPermissionWithInheritance(data: {
  role: string
  resource: string
  action: string
}) {
  const response = await api.post<PermissionCheckWithInheritanceResponse>(
    `${API_PREFIX}/check`,
    data
  )
  return response.data
}

/**
 * 清除权限缓存（仅 Admin）
 */
export async function clearPermissionCache() {
  const response = await api.post<{ data: { success: boolean; message: string } }>(
    `${API_PREFIX}/cache/clear`
  )
  return response.data
}

/**
 * 为角色添加额外授权
 */
export async function grantAdditionalPermission(
  roleName: string,
  data: {
    resource: string
    action: string
  }
) {
  const response = await api.post(`/roles/${roleName}/permissions/additional`, data)
  return response.data
}

/**
 * 撤销角色的额外授权
 */
export async function revokeAdditionalPermission(
  roleName: string,
  params: {
    resource: string
    action: string
  }
) {
  const response = await api.delete(`/roles/${roleName}/permissions/additional`, { params })
  return response.data
}

/**
 * 获取角色的额外授权列表
 */
export async function getAdditionalPermissions(roleName: string) {
  const response = await api.get(`/roles/${roleName}/permissions/additional`)
  return response.data
}
