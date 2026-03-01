/**
 * 用户 API 客户端
 */
import { api } from '@/utils/request'

const API_PREFIX = '/users'

/**
 * 获取用户列表
 */
export async function getUserList(params?: { page?: number; page_size?: number }) {
  const response = await api.get(API_PREFIX, { params })
  return response.data
}
