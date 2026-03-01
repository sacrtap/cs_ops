<template>
  <div class="main-menu" data-testid="main-menu">
    <a-menu
      :selected-keys="selectedKeys"
      :open-keys="openKeys"
      mode="vertical"
      theme="dark"
      @menu-item-click="onMenuClick"
    >
      <!-- 仪表盘 -->
      <a-menu-item key="dashboard" data-testid="menu-item-dashboard">
        <icon-dashboard />
        <span>仪表盘</span>
      </a-menu-item>

      <!-- 客户管理 -->
      <a-menu-item
        v-if="hasPermission('customer', 'read')"
        key="customers"
        data-testid="menu-item-customer"
      >
        <icon-user />
        <span>客户管理</span>
      </a-menu-item>

      <!-- 结算管理 -->
      <a-menu-item
        v-if="hasPermission('settlement', 'read')"
        key="settlement"
        data-testid="menu-item-settlement"
        :class="{ disabled: !hasPermission('settlement', 'read') }"
      >
        <icon-safe />
        <span>结算管理</span>
      </a-menu-item>

      <!-- 报表管理 -->
      <a-menu-item
        v-if="hasPermission('reporting', 'read')"
        key="reporting"
        data-testid="menu-item-reporting"
      >
        <icon-bar-chart />
        <span>报表管理</span>
      </a-menu-item>

      <!-- 权限管理 (仅 Admin) -->
      <a-sub-menu v-if="isAdmin" key="admin" data-testid="menu-item-admin">
        <template #icon>
          <icon-settings />
        </template>
        <template #title>系统管理</template>

        <a-menu-item key="permission-matrix" data-testid="menu-item-permission">
          <icon-lock />
          <span>功能权限配置</span>
        </a-menu-item>
      </a-sub-menu>
    </a-menu>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { usePermissionMatrixStore } from '@/stores/permission-matrix'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const permissionStore = usePermissionMatrixStore()
const authStore = useAuthStore()

// 当前选中的菜单项
const selectedKeys = ref<string[]>([(route.name as string) || 'dashboard'])

// 展开的子菜单
const openKeys = ref<string[]>([])

// 检查权限
function hasPermission(module: string, action: string): boolean {
  return permissionStore.hasPermission(module, action)
}

// 检查是否是 Admin
const isAdmin = computed(() => {
  return authStore.user?.role === 'admin'
})

// 菜单点击处理
function onMenuClick({ key }: { key: string }) {
  const routeMap: Record<string, string> = {
    dashboard: '/dashboard',
    customers: '/customers',
    settlement: '/settlement',
    reporting: '/reporting',
    'permission-matrix': '/admin/permission/matrix',
  }

  const path = routeMap[key]
  if (path) {
    router.push(path)
  }
}

// 监听路由变化，更新选中菜单
watch(
  () => route.name,
  (newName) => {
    if (newName) {
      selectedKeys.value = [newName as string]
    }
  }
)

// 监听权限变化，刷新菜单
watch(
  () => permissionStore.permissions,
  () => {
    // 权限变化时自动刷新菜单（通过 v-if 条件）
  },
  { deep: true }
)
</script>

<style scoped lang="scss">
.main-menu {
  height: 100%;
  overflow-y: auto;

  :deep(.arco-menu) {
    border-right: none;
  }

  :deep(.arco-menu-item) {
    &.disabled {
      color: rgba(255, 255, 255, 0.3);
      pointer-events: none;
      cursor: not-allowed;
    }

    &:not(.disabled) {
      &:hover {
        background-color: rgba(255, 255, 255, 0.1);
      }
    }
  }

  :deep(.arco-menu-submenu) {
    &.disabled {
      opacity: 0.5;
      pointer-events: none;
    }
  }
}
</style>
