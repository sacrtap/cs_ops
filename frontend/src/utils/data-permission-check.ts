/**
 * 数据权限检查工具函数
 *
 * 提供便捷的数据权限检查方法，可在组件和模板中使用
 *
 * Story 1.4: Data Permission
 */
import { useDataPermissionStore } from '@/stores/data-permission'
import type { DataScope } from '@/types/data-permission'

/**
 * 检查当前用户是否可以访问指定数据范围
 *
 * @param scope 数据范围
 * @returns boolean 是否可以访问
 *
 * @example
 * ```typescript
 * if (canAccessDataScope('organization')) {
 *   // 显示组织数据
 * }
 * ```
 */
export function canAccessDataScope(scope: DataScope): boolean {
  const dataPermissionStore = useDataPermissionStore()

  switch (scope) {
    case 'all':
      return dataPermissionStore.canAccessAll
    case 'organization':
      return dataPermissionStore.canAccessOrg
    case 'assigned':
      return dataPermissionStore.canAccessAssigned
    case 'personal':
      return dataPermissionStore.canAccessPersonal
    default:
      return false
  }
}

/**
 * 检查当前用户是否可以访问指定组织的数据
 *
 * @param orgId 组织 ID
 * @returns boolean 是否可以访问
 *
 * @example
 * ```typescript
 * if (canAccessOrg(5)) {
 *   // 显示该组织的数据
 * }
 * ```
 */
export function canAccessOrg(orgId: number): boolean {
  const dataPermissionStore = useDataPermissionStore()

  // Admin 可以访问所有组织
  if (dataPermissionStore.canAccessAll) {
    return true
  }

  // 检查是否是当前用户的组织
  return dataPermissionStore.currentOrgId === orgId
}

/**
 * 检查当前用户是否可以访问指定销售代表的客户
 *
 * @param salesRepId 销售代表 ID
 * @returns boolean 是否可以访问
 *
 * @example
 * ```typescript
 * if (canAccessSalesRepCustomers(1)) {
 *   // 显示该销售代表的客户
 * }
 * ```
 */
export function canAccessSalesRepCustomers(salesRepId: number): boolean {
  const dataPermissionStore = useDataPermissionStore()

  // Admin 和经理可以访问所有销售代表的客户
  if (dataPermissionStore.canAccessAll || dataPermissionStore.canAccessOrg) {
    return true
  }

  // 销售代表只能访问自己的客户
  return dataPermissionStore.currentUserId === salesRepId
}

/**
 * 检查当前用户是否可以访问特定客户
 *
 * @param customerId 客户 ID
 * @param customerOrgId 客户组织 ID
 * @param customerSalesRepId 客户销售代表 ID
 * @returns boolean 是否可以访问
 *
 * @example
 * ```typescript
 * if (canAccessCustomer(customer.id, customer.org_id, customer.sales_rep_id)) {
 *   // 显示客户详情
 * }
 * ```
 */
export function canAccessCustomer(
  _customerId: number,
  customerOrgId: number,
  customerSalesRepId: number
): boolean {
  const dataPermissionStore = useDataPermissionStore()

  // Admin 可以访问所有客户
  if (dataPermissionStore.canAccessAll) {
    return true
  }

  // 经理可以访问本组织所有客户
  if (dataPermissionStore.canAccessOrg && customerOrgId === dataPermissionStore.currentOrgId) {
    return true
  }

  // 销售代表只能访问自己负责的客户
  return customerSalesRepId === dataPermissionStore.currentUserId
}

/**
 * 获取当前用户的数据范围标签
 *
 * @returns string 数据范围标签
 *
 * @example
 * ```typescript
 * <span>{{ getDataScopeLabel() }}</span>
 * ```
 */
export function getDataScopeLabel(): string {
  const dataPermissionStore = useDataPermissionStore()
  return dataPermissionStore.dataScopeLabel
}

/**
 * 获取当前用户的组织 ID
 *
 * @returns number | null 组织 ID
 */
export function getCurrentOrgId(): number | null {
  const dataPermissionStore = useDataPermissionStore()
  return dataPermissionStore.currentOrgId
}

/**
 * 获取当前用户 ID
 *
 * @returns number 用户 ID
 */
export function getCurrentUserId(): number {
  const dataPermissionStore = useDataPermissionStore()
  return dataPermissionStore.currentUserId || 0
}
