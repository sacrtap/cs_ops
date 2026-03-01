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

// ==================== 权限继承相关类型 ====================

/** 角色层级信息 */
export interface RoleHierarchyLevel {
  level: number
  role: string
  name: string
  inherits: string[] // 继承的角色列表
}

/** 角色层级结构响应 */
export interface RoleHierarchyResponse {
  data: {
    levels: RoleHierarchyLevel[]
  }
  meta: {
    timestamp: string
    roles_count: number
  }
  error?: {
    code: string
    message: string
  }
}

/** 继承权限信息 */
export interface InheritedPermission {
  resource: string
  action: string
  inherited_from: string // 从哪个角色继承
}

/** 直接权限信息 */
export interface DirectPermission {
  resource: string
  action: string
}

/** 角色权限详情（包含继承） */
export interface RolePermissionsDetail {
  role: string
  level: number
  inherited_from: string[] // 继承的角色来源
  inherited_permissions: InheritedPermission[] // 继承的权限
  direct_permissions: DirectPermission[] // 直接权限
  all_permissions: Array<{
    resource: string
    action: string
  }> // 所有权限（合并后）
}

/** 角色权限响应 */
export interface RolePermissionsResponse {
  data: RolePermissionsDetail
  meta: {
    timestamp: string
  }
  error?: {
    code: string
    message: string
  }
}

/** 权限检查结果（包含继承信息） */
export interface PermissionCheckWithInheritanceResponse {
  data: {
    has_permission: boolean
    source: 'admin' | 'direct' | 'inherited' | 'none' // 权限来源
    inherited_from?: string // 如果是继承的，指明从哪个角色继承
    message: string
  }
  meta: {
    timestamp: string
    role: string
    resource: string
    action: string
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
  hierarchy: RoleHierarchyLevel[] // 角色层级结构
  isLoading: boolean
  error: string | null
}
