/**
 * 权限矩阵类型定义
 */

/** 角色类型 */
export type Role = 'admin' | 'manager' | 'specialist' | 'sales'

/** 功能模块 */
export type Module = 'customer' | 'settlement' | 'reporting' | 'permission'

/** 操作类型 */
export type Action = 'read' | 'create' | 'update' | 'delete'

/** 单个权限配置 */
export interface PermissionConfig {
  role: Role
  module: Module
  action: Action
  granted: boolean
}

/** 模块权限映射 */
export interface ModulePermissions {
  [action: string]: boolean
}

/** 角色权限映射 */
export interface RolePermissions {
  [module: string]: ModulePermissions
}

/** 所有角色权限 */
export interface AllPermissions {
  admin: RolePermissions
  manager: RolePermissions
  specialist: RolePermissions
  sales: RolePermissions
}

/** 权限检查请求 */
export interface PermissionCheckRequest {
  module: Module | string
  action: Action | string
}

/** 权限检查响应 */
export interface PermissionCheckResponse {
  granted: boolean
  role: Role
  module: string
  action: string
}

/** 缓存统计 */
export interface CacheStats {
  size: number
  max_size: number
  hits: number
  misses: number
  hit_rate: number
  ttl_seconds: number
}

/** API 响应基础结构 */
export interface ApiResponse<T> {
  data: T
  meta?: {
    total?: number
    timestamp?: string
    request_id?: string
    [key: string]: any
  }
  error?: {
    code: string
    message: string
    details?: any
  }
}
