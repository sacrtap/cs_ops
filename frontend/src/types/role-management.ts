/**
 * 角色管理的 TypeScript 类型定义
 */

// ==================== 角色相关类型 ====================

/** 角色信息 */
export interface Role {
  id: number
  name: string
  description: string | null
  status: 'active' | 'inactive'
  created_at: string
  updated_at: string
}

/** 角色统计信息 */
export interface RoleStats {
  total_roles: number
  active_roles: number
  inactive_roles: number
  roles: Array<Role & { user_count: number }>
}

/** 权限矩阵（模块 → 操作 → 是否授权） */
export interface PermissionMatrix {
  [module: string]: {
    [action: string]: boolean
  }
}

/** 带权限的角色信息 */
export interface RoleWithPermissions extends Role {
  permissions: PermissionMatrix
}

// ==================== API 请求类型 ====================

/** 角色创建请求 */
export interface RoleCreateRequest {
  name: string
  description?: string
  status?: 'active' | 'inactive'
}

/** 角色更新请求 */
export interface RoleUpdateRequest {
  name?: string
  description?: string
  status?: 'active' | 'inactive'
}

/** 角色权限更新请求 */
export interface RolePermissionsUpdateRequest {
  permissions: PermissionMatrix
}

// ==================== API 响应类型 ====================

/** 角色列表响应 */
export interface RoleListResponse {
  data: Role[]
  meta: {
    total: number
  }
}

/** 角色详情响应 */
export interface RoleResponse {
  data: Role
}

/** 角色权限响应 */
export interface RolePermissionsResponse {
  data: PermissionMatrix
}

/** 角色统计响应 */
export interface RoleStatsResponse {
  data: RoleStats
}

/** 通用操作响应 */
export interface RoleActionResponse {
  data: {
    success: boolean
    [key: string]: any
  }
  message?: string
}

// ==================== Store 状态类型 ====================

/** 角色管理状态 */
export interface RoleManagementState {
  roles: Role[]
  currentRole: RoleWithPermissions | null
  stats: RoleStats | null
  isLoading: boolean
  isSaving: boolean
  error: string | null
}

// ==================== 表单类型 ====================

/** 角色表单数据 */
export interface RoleFormData {
  name: string
  description: string
  status: 'active' | 'inactive'
}

/** 角色权限配置数据 */
export interface RolePermissionFormData {
  roleId: number
  permissions: PermissionMatrix
}
