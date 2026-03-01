/**
 * 权限指令 v-permission
 *
 * 使用方式:
 * <button v-permission="['customer', 'delete']">删除</button>
 * <button v-permission:customer.create>创建</button>
 * <button v-permission="[customer.read, customer.update]">查看或编辑</button>
 */
import type { Directive, DirectiveBinding } from 'vue'
import { usePermissionStore } from '@/stores/permission'
import type { PermissionResource, PermissionAction } from '@/types/permission'

interface PermissionHTMLElement extends HTMLElement {
  _permission_disabled?: boolean
}

/**
 * 解析指令参数
 */
function parsePermission(binding: DirectiveBinding): Array<[PermissionResource, PermissionAction]> {
  const { arg, value } = binding

  // 处理值方式：v-permission="[['customer', 'delete']]"
  if (value && Array.isArray(value)) {
    return value
  }

  // 处理参数方式：v-permission:customer.delete
  if (arg) {
    const parts = arg.split('.')
    if (parts.length === 2) {
      return [[parts[0] as PermissionResource, parts[1] as PermissionAction]]
    }
  }

  // 默认返回空数组（无权限）
  return []
}

/**
 * 更新元素可见性
 */
function updateElementVisibility(el: PermissionHTMLElement, hasPermission: boolean) {
  if (hasPermission) {
    el.style.display = ''
    el.removeAttribute('disabled')
    el._permission_disabled = false
  } else {
    el.style.display = 'none'
    el.setAttribute('disabled', 'true')
    el._permission_disabled = true
  }
}

/**
 * v-permission 指令
 */
export const permissionDirective: Directive<PermissionHTMLElement> = {
  mounted(el, binding) {
    const permissions = parsePermission(binding)
    const permissionStore = usePermissionStore()

    // 如果没有权限，检查是否至少有一个权限
    let hasPermission = false
    if (permissions.length === 1) {
      const [resource, action] = permissions[0]
      hasPermission = permissionStore.hasPermission(resource, action)
    } else if (permissions.length > 1) {
      hasPermission = permissionStore.hasAnyPermission(permissions)
    }

    updateElementVisibility(el, hasPermission)
  },

  updated(el, binding) {
    const permissions = parsePermission(binding)
    const permissionStore = usePermissionStore()

    let hasPermission = false
    if (permissions.length === 1) {
      const [resource, action] = permissions[0]
      hasPermission = permissionStore.hasPermission(resource, action)
    } else if (permissions.length > 1) {
      hasPermission = permissionStore.hasAnyPermission(permissions)
    }

    updateElementVisibility(el, hasPermission)
  },
}

/**
 * 自动注册指令
 */
export function setupPermissionDirective(app: any) {
  app.directive('permission', permissionDirective)
}

export default permissionDirective
