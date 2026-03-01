/**
 * 权限矩阵 API 客户端
 */

import { api } from '@/utils/request'
import type {
  AllPermissions,
  PermissionConfig,
  PermissionCheckResponse,
  CacheStats,
  ApiResponse,
} from '@/types/permission-matrix'

/**
 * 获取所有角色的权限矩阵
 */
export async function getPermissionMatrix(): Promise<AllPermissions> {
  const response = await api.get<ApiResponse<AllPermissions>>('/api/v1/permission-matrix')
  return response.data.data
}

/**
 * 更新单个权限配置
 */
export async function updatePermission(
  role: string,
  module: string,
  action: string,
  granted: boolean
): Promise<PermissionConfig> {
  const response = await api.put<ApiResponse<{ success: boolean; permission: PermissionConfig }>>(
    '/api/v1/permission-matrix',
    { role, module, action, granted }
  )
  return response.data.data.permission
}

/**
 * 批量更新权限配置
 */
export async function bulkUpdatePermissions(
  permissions: Array<{ role: string; module: string; action: string; granted: boolean }>
): Promise<number> {
  const response = await api.put<ApiResponse<{ success: boolean; updated_count: number }>>(
    '/api/v1/permission-matrix/bulk',
    { permissions }
  )
  return response.data.data.updated_count
}

/**
 * 检查当前用户是否有指定权限
 */
export async function checkPermission(
  module: string,
  action: string
): Promise<PermissionCheckResponse> {
  const response = await api.post<ApiResponse<PermissionCheckResponse>>(
    '/api/v1/permission-matrix/check',
    { module, action }
  )
  return response.data.data
}

/**
 * 获取缓存统计信息
 */
export async function getCacheStats(): Promise<CacheStats> {
  const response = await api.get<ApiResponse<CacheStats>>('/api/v1/permission-matrix/cache/stats')
  return response.data.data
}

/**
 * 清除权限缓存
 */
export async function clearCache(role?: string): Promise<void> {
  const params = role ? { role } : {}
  await api.delete<ApiResponse<{ success: boolean }>>('/api/v1/permission-matrix/cache', { params })
}
