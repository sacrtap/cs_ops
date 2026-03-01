import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { usePermissionMatrixStore } from '@/stores/permission-matrix'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/LoginView.vue'),
    meta: {
      title: '登录 - CS Ops',
      requiresAuth: false,
    },
  },
  {
    path: '/',
    name: 'Home',
    redirect: '/dashboard',
    meta: {
      title: '首页 - CS Ops',
      requiresAuth: true,
    },
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue'),
    meta: {
      title: '仪表盘 - CS Ops',
      requiresAuth: true,
      module: 'dashboard',
      action: 'read',
    },
  },
  // 客户管理
  {
    path: '/customers',
    name: 'Customers',
    component: () => import('@/views/customer/CustomerList.vue'),
    meta: {
      title: '客户管理 - CS Ops',
      requiresAuth: true,
      module: 'customer',
      action: 'read',
    },
  },
  // 结算管理
  {
    path: '/settlement',
    name: 'Settlement',
    component: () => import('@/views/settlement/SettlementList.vue'),
    meta: {
      title: '结算管理 - CS Ops',
      requiresAuth: true,
      module: 'settlement',
      action: 'read',
    },
  },
  // 报表管理
  {
    path: '/reporting',
    name: 'Reporting',
    component: () => import('@/views/reporting/ReportingList.vue'),
    meta: {
      title: '报表管理 - CS Ops',
      requiresAuth: true,
      module: 'reporting',
      action: 'read',
    },
  },
  // 权限配置（仅 Admin）
  {
    path: '/admin/permission/matrix',
    name: 'PermissionMatrix',
    component: () => import('@/views/admin/permission/MatrixConfig.vue'),
    meta: {
      title: '功能权限配置 - CS Ops',
      requiresAuth: true,
      module: 'permission',
      action: 'read',
      requiresAdmin: true,
    },
  },
  // 角色管理（仅 Admin）
  {
    path: '/admin/role',
    name: 'RoleList',
    component: () => import('@/views/admin/role/RoleList.vue'),
    meta: {
      title: '角色管理 - CS Ops',
      requiresAuth: true,
      module: 'role',
      action: 'read',
      requiresAdmin: true,
    },
  },
  // 权限审计（仅 Admin）
  {
    path: '/permissions/audit',
    name: 'PermissionAudit',
    component: () => import('@/views/permission/PermissionAudit.vue'),
    meta: {
      title: '权限审计 - CS Ops',
      requiresAuth: true,
      module: 'permission',
      action: 'read',
      requiresAdmin: true,
    },
  },
  {
    path: '/admin/role/:id/config',
    name: 'RoleConfig',
    component: () => import('@/views/admin/role/RoleConfig.vue'),
    meta: {
      title: '角色权限配置 - CS Ops',
      requiresAuth: true,
      module: 'role',
      action: 'update',
      requiresAdmin: true,
    },
  },
  // 403 权限拒绝页面
  {
    path: '/403',
    name: 'Forbidden',
    component: () => import('@/views/error/403.vue'),
    meta: {
      title: '无权访问 - CS Ops',
      requiresAuth: false,
    },
  },
  // 404 页面
  {
    path: '/404',
    name: 'NotFound',
    component: () => import('@/views/error/404.vue'),
    meta: {
      title: '页面未找到 - CS Ops',
      requiresAuth: false,
    },
  },
  // 通配符路由 - 捕获所有未匹配的路由
  {
    path: '/:pathMatch(.*)*',
    redirect: '/404',
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 路由守卫
router.beforeEach(async (to, _from, next) => {
  // 设置页面标题
  document.title = (to.meta.title as string) || 'CS Ops 运营系统'

  // 获取认证状态
  const token = localStorage.getItem('access_token')
  const requiresAuth = to.meta.requiresAuth !== false

  // 1. 检查认证状态
  if (requiresAuth && !token) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
    return
  }

  if (to.name === 'Login' && token) {
    next({ name: 'Home' })
    return
  }

  // 2. 如果需要认证，检查功能权限
  if (requiresAuth && token) {
    const authStore = useAuthStore()
    const permissionStore = usePermissionMatrixStore()

    // 确保权限矩阵已加载
    if (Object.keys(permissionStore.permissions).length === 0) {
      try {
        await permissionStore.loadPermissions()
      } catch (error) {
        console.error('Failed to load permissions:', error)
      }
    }

    // 检查是否需要 Admin 权限
    if (to.meta.requiresAdmin) {
      const userRole = authStore.user?.role
      if (userRole !== 'admin') {
        next({ name: 'Forbidden', query: { reason: 'requires_admin' } })
        return
      }
    }

    // 检查具体模块权限
    const module = to.meta.module as string
    const action = (to.meta.action as string) || 'read'

    if (module && !permissionStore.isAdmin) {
      const hasAccess = permissionStore.hasPermission(module, action)
      if (!hasAccess) {
        next({
          name: 'Forbidden',
          query: {
            reason: 'permission_denied',
            module,
            action,
            role: authStore.user?.role,
          },
        })
        return
      }
    }
  }

  next()
})

export default router
