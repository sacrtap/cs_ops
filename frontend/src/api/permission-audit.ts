/**
 * 权限审计 API 客户端
 */
import { api } from '@/utils/request'

const API_PREFIX = '/permissions/audit'

/**
 * 查询权限审计记录
 */
export async function queryAuditLogs(params?: {
  user_id?: string
  start_date?: string
  end_date?: string
  anomaly_type?: string
  page?: number
  page_size?: number
  sort_by?: string
  sort_order?: 'asc' | 'desc'
}) {
  const response = await api.get(API_PREFIX, { params })
  return response.data
}

/**
 * 获取权限审计统计信息
 */
export async function getAuditStatistics(params?: { start_date?: string; end_date?: string }) {
  const response = await api.get(`${API_PREFIX}/statistics`, { params })
  return response.data
}

/**
 * 导出权限审计记录
 */
export async function exportAuditLogs(params?: {
  user_id?: string
  start_date?: string
  end_date?: string
  format?: 'csv' | 'json'
}) {
  const response = await api.get(`${API_PREFIX}/export`, {
    params,
    responseType: 'blob',
  })
  return response
}
