/**
 * 数据权限的 TypeScript 类型定义
 *
 * 用于 Story 1.4: Data Permission
 */

// ==================== 数据权限相关类型 ====================

/** 数据范围类型 */
export type DataScope = 'all' | 'organization' | 'assigned' | 'personal'

/** 数据范围信息 */
export interface DataScopeInfo {
  scope: DataScope
  label: string
  description: string
  org_id?: number
  org_name?: string
}

/** 用户数据权限上下文 */
export interface UserDataPermission {
  user_id: number
  role: string
  org_id: number | null
  data_scope: DataScope
  can_access_all: boolean
  can_access_org: boolean
  can_access_assigned: boolean
  can_access_personal: boolean
}

// ==================== API 响应类型 ====================

/** 数据范围列表响应 */
export interface DataScopeListResponse {
  data: DataScopeInfo[]
  meta: {
    timestamp: string
    count: number
    current_scope: DataScope
  }
  error?: {
    code: string
    message: string
  }
}

/** 用户数据权限响应 */
export interface UserDataPermissionResponse {
  data: UserDataPermission
  meta: {
    timestamp: string
  }
  error?: {
    code: string
    message: string
  }
}

// ==================== Store 状态类型 ====================

/** 数据权限状态 */
export interface DataPermissionState {
  currentScope: DataScope | null
  availableScopes: DataScopeInfo[]
  userDataPermission: UserDataPermission | null
  isLoading: boolean
  error: string | null
}
