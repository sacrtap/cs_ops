import { createRouter, createWebHistory } from 'vue-router'
import type {
  RouteRecordRaw,
  Router,
  NavigationGuardNext,
  RouteLocationNormalized,
} from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/LoginView.vue'),
    meta: {
      title: '登录 - CS Ops',
      requiresAuth: false, // 登录页不需要认证
    },
  },
  {
    path: '/',
    name: 'Home',
    redirect: '/login', // TODO: 实现首页后修改为实际首页
    meta: {
      title: '首页 - CS Ops',
      requiresAuth: true, // 首页需要认证
    },
  },
  // TODO: 添加更多路由
  // {
  //   path: '/customers',
  //   name: 'Customers',
  //   component: () => import('@/views/Customer/CustomerList.vue'),
  //   meta: {
  //     title: '客户管理 - CS Ops',
  //     requiresAuth: true,
  //   },
  // },
  // {
  //   path: '/billing',
  //   name: 'Billing',
  //   component: () => import('@/views/Billing/BillingList.vue'),
  //   meta: {
  //     title: '账单管理 - CS Ops',
  //     requiresAuth: true,
  //   },
  // },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  document.title = (to.meta.title as string) || 'CS Ops 运营系统'

  // 获取认证状态（从 localStorage 或 pinia）
  const token = localStorage.getItem('access_token')
  const requiresAuth = to.meta.requiresAuth !== false

  if (requiresAuth && !token) {
    // 需要认证但未登录，跳转到登录页
    next({ name: 'Login', query: { redirect: to.fullPath } })
  } else if (to.name === 'Login' && token) {
    // 已登录但访问登录页，跳转到首页
    next({ name: 'Home' })
  } else {
    next()
  }
})

export default router
