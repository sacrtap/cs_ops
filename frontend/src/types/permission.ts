/**
 * 权限管理的 TypeScript 类型定义
 */

// ==================== 权限相关类型 ====================

/** 权限资源类型 */
export type PermissionResource = 'customer' | 'settlement' | 'report' | 'user' | 'role'

/** 权限操作类型 */
export type PermissionAction = 'create' | 'read' | 'update' | 'delete' | 'view' | 'export'

/** 角色信息 */
export interface Role {
  role: string
  name: string
  level: number
  description: string
}

/** 权限矩阵 */
export interface PermissionMatrix {
  [role: string]: {
    [resource: string]: string[]
  }
}

// ==================== API 请求类型 ====================

/** 权限检查请求 */
export interface PermissionCheckRequest {
  resource: PermissionResource
  action: PermissionAction
}

/** 权限矩阵更新请求 */
export interface PermissionMatrixUpdateRequest {
  role: string
  resource: PermissionResource
  action: PermissionAction
  enabled: boolean
}

/** 用户角色更新请求 */
export interface UserRoleUpdateRequest {
  role: string
}

// ==================== API 响应类型 ====================

/** 角色列表响应 */
export interface RoleListResponse {
  data: Role[]
  meta: {
    timestamp: string
    count: number
  }
  error?: {
    code: string
    message: string
  }
}

/** 权限矩阵响应 */
export interface PermissionMatrixResponse {
  data: PermissionMatrix
  meta: {
    timestamp: string
    roles_count: number
  }
  error?: {
    code: string
    message: string
  }
}

/** 权限检查响应 */
export interface PermissionCheckResponse {
  data: {
    has_permission: boolean
    role: string
    resource: string
    action: string
  }
  meta: {
    timestamp: string
  }
  error?: {
    code: string
    message: string
  }
}

/** 权限矩阵更新响应 */
export interface PermissionMatrixUpdateResponse {
  data: {
    success: boolean
    message: string
  }
  meta: {
    timestamp: string
  }
  error?: {
    code: string
    message: string
  }
}

/** 用户角色更新响应 */
export interface UserRoleUpdateResponse {
  data: {
    success: boolean
    message: string
    user: {
      id: number
      username: string
      real_name: string
      role: string
      email?: string | null
      phone?: string | null
      status: string
      created_at: string
    }
  }
  meta: {
    timestamp: string
  }
  error?: {
    code: string
    message: string
  }
}

// ==================== Store 状态类型 ====================

/** 权限状态 */
export interface PermissionState {
  roles: Role[]
  matrix: PermissionMatrix
  isLoading: boolean
  error: string | null
}
