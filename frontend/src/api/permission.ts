/**
 * 权限管理 API 客户端
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
