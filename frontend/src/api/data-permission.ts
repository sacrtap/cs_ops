/**
 * 数据权限 API 客户端
 *
 * 提供与后端数据权限相关的 API 调用
 */
import request from '@/utils/request'
import type { DataScopeListResponse, UserDataPermissionResponse } from '@/types/data-permission'

/**
 * 获取当前用户可用的数据范围列表
 *
 * @returns Promise<DataScopeListResponse> 数据范围列表
 */
export async function getDataScopes(): Promise<DataScopeListResponse> {
  const response = await request<DataScopeListResponse>({
    url: '/api/v1/data-permission/scopes',
    method: 'get',
  })
  return response.data
}

/**
 * 获取当前用户的数据权限信息
 *
 * @returns Promise<UserDataPermissionResponse> 用户数据权限信息
 */
export async function getUserDataPermission(): Promise<UserDataPermissionResponse> {
  const response = await request<UserDataPermissionResponse>({
    url: '/api/v1/data-permission/current',
    method: 'get',
  })
  return response.data
}

/**
 * 切换当前数据范围
 *
 * @param scope 数据范围
 * @param org_id 组织 ID（可选）
 * @returns Promise<UserDataPermissionResponse> 更新后的用户数据权限
 */
export async function switchDataScope(
  scope: string,
  org_id?: number
): Promise<UserDataPermissionResponse> {
  const response = await request<UserDataPermissionResponse>({
    url: '/api/v1/data-permission/scope',
    method: 'post',
    data: {
      scope,
      org_id,
    },
  })
  return response.data
}

/**
 * 获取客户列表（带数据权限过滤）
 *
 * @param params 查询参数
 * @returns Promise<any> 客户列表
 */
export async function getCustomersWithPermission(params?: {
  page?: number
  page_size?: number
  org_id?: number
  sales_rep_id?: number
  status?: string
}): Promise<any> {
  const response = await request({
    url: '/api/v1/customers',
    method: 'get',
    params,
  })
  return response.data
}

/**
 * 获取客户详情（带数据权限检查）
 *
 * @param id 客户 ID
 * @returns Promise<any> 客户详情
 */
export async function getCustomerById(id: number): Promise<any> {
  const response = await request({
    url: `/api/v1/customers/${id}`,
    method: 'get',
  })
  return response.data
}
