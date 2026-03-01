<template>
  <div class="permission-matrix-editor" :data-testid="`editor-${role}`">
    <!-- 权限概览 -->
    <div class="permission-summary">
      <h3>{{ getRoleName(role) }} 权限配置</h3>
      <div class="summary-stats">
        <a-statistic
          title="总权限数"
          :value="totalPermissions"
          :value-style="{ color: '#165dff' }"
        />
        <a-statistic title="已授予" :value="grantedCount" :value-style="{ color: '#00b42a' }" />
        <a-statistic title="已拒绝" :value="deniedCount" :value-style="{ color: '#f53f3f' }" />
      </div>
    </div>

    <!-- 权限列表 -->
    <div class="permission-list">
      <div v-for="(modulePerms, module) in permissions" :key="module" class="permission-group">
        <div class="group-header">
          <span class="group-title">{{ getModuleName(module) }}</span>
          <a-checkbox
            :model-value="isModuleAllGranted(module)"
            :indeterminate="isModulePartiallyGranted(module)"
            @change="onModuleCheckChange(module, $event)"
          >
            全选
          </a-checkbox>
        </div>

        <div class="permission-items">
          <div
            v-for="(granted, action) in modulePerms"
            :key="action"
            class="permission-item"
            :data-testid="`permission-item-${role}-${module}-${action}`"
          >
            <span class="action-name">{{ getActionName(action as string) }}</span>
            <a-switch
              :model-value="granted"
              size="small"
              @change="onPermissionToggle(module, action as string, $event)"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { RolePermissions, Role } from '@/types/permission-matrix'

interface Props {
  role: Role
  permissions: RolePermissions
  onChange?: (module: string, action: string, granted: boolean) => void
}

const props = withDefaults(defineProps<Props>(), {
  onChange: undefined,
})

// 获取角色名称
function getRoleName(role: Role): string {
  const names: Record<Role, string> = {
    admin: '管理员',
    manager: '经理',
    specialist: '专员',
    sales: '销售',
  }
  return names[role]
}

// 获取模块名称
function getModuleName(module: string): string {
  const names: Record<string, string> = {
    customer: '客户管理',
    settlement: '结算管理',
    reporting: '报表管理',
    permission: '权限管理',
  }
  return names[module] || module
}

// 获取操作名称
function getActionName(action: string): string {
  const names: Record<string, string> = {
    read: '读取',
    create: '创建',
    update: '更新',
    delete: '删除',
  }
  return names[action] || action
}

// 统计
const totalPermissions = computed(() => {
  let count = 0
  Object.values(props.permissions).forEach((perms) => {
    count += Object.keys(perms).length
  })
  return count
})

const grantedCount = computed(() => {
  let count = 0
  Object.values(props.permissions).forEach((perms) => {
    Object.values(perms).forEach((granted) => {
      if (granted) count++
    })
  })
  return count
})

const deniedCount = computed(() => {
  return totalPermissions.value - grantedCount.value
})

// 检查模块是否全部授予
function isModuleAllGranted(module: string): boolean {
  const perms = props.permissions[module]
  if (!perms) return false
  return Object.values(perms).every((granted) => granted)
}

// 检查模块是否部分授予
function isModulePartiallyGranted(module: string): boolean {
  const perms = props.permissions[module]
  if (!perms) return false
  const values = Object.values(perms)
  return values.some((v) => v) && values.some((v) => !v)
}

// 模块全选变更
function onModuleCheckChange(module: string, event: Event) {
  const target = event.target as HTMLInputElement
  const granted = target.checked

  // 通知父组件更新该模块的所有权限
  const actions = Object.keys(props.permissions[module] || {})
  actions.forEach((action) => {
    props.onChange?.(module, action, granted)
  })
}

// 权限切换
function onPermissionToggle(module: string, action: string, granted: boolean) {
  props.onChange?.(module, action, granted)
}
</script>

<style scoped lang="scss">
.permission-matrix-editor {
  .permission-summary {
    margin-bottom: 24px;

    h3 {
      margin: 0 0 16px 0;
      font-size: 16px;
      font-weight: 600;
    }

    .summary-stats {
      display: flex;
      gap: 24px;
    }
  }

  .permission-list {
    .permission-group {
      margin-bottom: 20px;
      padding: 16px;
      background: #f7f8fa;
      border-radius: 4px;

      .group-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;

        .group-title {
          font-weight: 600;
          font-size: 14px;
          color: #1d2129;
        }
      }

      .permission-items {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
        gap: 12px;

        .permission-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 8px 12px;
          background: #fff;
          border-radius: 4px;

          .action-name {
            font-size: 13px;
            color: #4e5969;
          }
        }
      }
    }
  }
}
</style>
