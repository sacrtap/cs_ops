/**
 * 权限检查工具函数
 *
 * 提供便捷的权限检查方法，可在组件和模板中使用
 */
import type { PermissionResource, PermissionAction } from '@/types/permission'
import { usePermissionStore } from '@/stores/permission'

/**
 * 检查当前用户是否有权限
 *
 * @param resource 资源名称
 * @param action 操作类型
 * @returns boolean 是否有权限
 *
 * @example
 * ```typescript
 * if (hasPermission('customer', 'delete')) {
 *   // 显示删除按钮
 * }
 * ```
 */
export function hasPermission(resource: PermissionResource, action: PermissionAction): boolean {
  const permissionStore = usePermissionStore()
  return permissionStore.hasPermission(resource, action)
}

/**
 * 检查当前用户是否有任意一个权限
 *
 * @param permissions 权限列表
 * @returns boolean 是否有至少一个权限
 *
 * @example
 * ```typescript
 * if (hasAnyPermission([
 *   ['customer', 'read'],
 *   ['customer', 'create']
 * ])) {
 *   // 显示客户管理菜单
 * }
 * ```
 */
export function hasAnyPermission(
  permissions: Array<[PermissionResource, PermissionAction]>
): boolean {
  const permissionStore = usePermissionStore()
  return permissionStore.hasAnyPermission(permissions)
}

/**
 * 检查当前用户是否拥有所有权限
 *
 * @param permissions 权限列表
 * @returns boolean 是否拥有所有权限
 *
 * @example
 * ```typescript
 * if (hasAllPermissions([
 *   ['customer', 'read'],
 *   ['customer', 'delete']
 * ])) {
 *   // 显示完整客户管理功能
 * }
 * ```
 */
export function hasAllPermissions(
  permissions: Array<[PermissionResource, PermissionAction]>
): boolean {
  const permissionStore = usePermissionStore()
  return permissionStore.hasAllPermissions(permissions)
}

/**
 * 获取当前用户的角色级别
 *
 * @param roleName 角色名称
 * @returns number 角色级别（1-4）
 */
export function getRoleLevel(roleName: string): number {
  const permissionStore = usePermissionStore()
  return permissionStore.getRoleLevel(roleName)
}

/**
 * 检查是否是 Admin 角色
 */
export function isAdmin(): boolean {
  const userRole = localStorage.getItem('user_role')
  return userRole === 'admin'
}

/**
 * 检查是否是 Manager 或更高级别
 */
export function isManagerOrHigher(): boolean {
  const userRole = localStorage.getItem('user_role')
  const permissionStore = usePermissionStore()
  const level = permissionStore.getRoleLevel(userRole || '')
  return level >= 3
}

/**
 * 检查是否是 Specialist 或更高级别
 */
export function isSpecialistOrHigher(): boolean {
  const userRole = localStorage.getItem('user_role')
  const permissionStore = usePermissionStore()
  const level = permissionStore.getRoleLevel(userRole || '')
  return level >= 2
}
