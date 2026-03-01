<template>
  <div class="permission-matrix-container" data-testid="permission-matrix-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>功能权限配置</h2>
      <a-button
        type="primary"
        @click="saveChanges"
        :loading="saving"
        data-testid="save-permission-btn"
      >
        <template #icon><icon-save /></template>
        保存更改
      </a-button>
    </div>

    <!-- 角色标签页 -->
    <a-tabs v-model:activeKey="activeRole" type="card" class="role-tabs">
      <a-tab-pane v-for="role in roles" :key="role" :data-testid="`role-tab-${role}`">
        <template #title>
          <span :class="['role-title', role]">
            {{ getRoleName(role) }}
          </span>
        </template>

        <!-- 权限矩阵表格 -->
        <a-table
          :columns="columns"
          :data="getMatrixData(role)"
          :pagination="false"
          :bordered="true"
          :row-key="getRowKey"
          class="permission-matrix-table"
          data-testid="permission-matrix-table"
        >
          <!-- 模块名称列 -->
          <template #module="{ record }">
            <span class="module-name">{{ getModuleName(record.module) }}</span>
          </template>

          <!-- 权限复选框列 -->
          <template #read="{ record, rowIndex }">
            <a-checkbox
              :model-value="record.read"
              :disabled="record.read === undefined"
              @change="onPermissionChange(record, 'read', $event)"
              :data-testid="`permission-checkbox-${role}-${record.module}-read`"
            />
          </template>

          <template #create="{ record, rowIndex }">
            <a-checkbox
              :model-value="record.create"
              :disabled="record.create === undefined"
              @change="onPermissionChange(record, 'create', $event)"
              :data-testid="`permission-checkbox-${role}-${record.module}-create`"
            />
          </template>

          <template #update="{ record, rowIndex }">
            <a-checkbox
              :model-value="record.update"
              :disabled="record.update === undefined"
              @change="onPermissionChange(record, 'update', $event)"
              :data-testid="`permission-checkbox-${role}-${record.module}-update`"
            />
          </template>

          <template #delete="{ record, rowIndex }">
            <a-checkbox
              :model-value="record.delete"
              :disabled="record.delete === undefined"
              @change="onPermissionChange(record, 'delete', $event)"
              :data-testid="`permission-checkbox-${role}-${record.module}-delete`"
            />
          </template>
        </a-table>
      </a-tab-pane>
    </a-tabs>

    <!-- 修改提示 -->
    <a-alert v-if="hasUnsavedChanges" type="warning" show-icon class="unsaved-changes-alert">
      <template #message> 您有未保存的更改，请点击"保存更改"按钮 </template>
    </a-alert>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { Message } from '@arco-design/web-vue'
import { usePermissionMatrixStore } from '@/stores/permission-matrix'
import type { RolePermissions, Role } from '@/types/permission-matrix'

// Store
const permissionStore = usePermissionMatrixStore()

// State
const activeRole = ref<Role>('admin')
const saving = ref(false)
const hasUnsavedChanges = ref(false)

// 角色列表
const roles: Role[] = ['admin', 'manager', 'specialist', 'sales']

// 表格列定义
const columns = [
  {
    title: '功能模块',
    dataIndex: 'module',
    slotName: 'module',
    width: 200,
    fixed: 'left',
  },
  {
    title: '读取',
    slotName: 'read',
    width: 100,
    align: 'center',
  },
  {
    title: '创建',
    slotName: 'create',
    width: 100,
    align: 'center',
  },
  {
    title: '更新',
    slotName: 'update',
    width: 100,
    align: 'center',
  },
  {
    title: '删除',
    slotName: 'delete',
    width: 100,
    align: 'center',
  },
]

// 模块列表
const modules = ['customer', 'settlement', 'reporting', 'permission']

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

// 获取矩阵数据
function getMatrixData(role: Role) {
  const rolePerms = permissionStore.permissions[role] || {}

  return modules.map((module) => {
    const modulePerms = rolePerms[module] || {}
    return {
      module,
      read: modulePerms.read ?? false,
      create: modulePerms.create ?? false,
      update: modulePerms.update ?? false,
      delete: modulePerms.delete ?? false,
    }
  })
}

// 获取行唯一键
function getRowKey(record: any) {
  return record.module
}

// 权限变更处理
function onPermissionChange(record: any, action: string, event: Event) {
  const target = event.target as HTMLInputElement
  const granted = target.checked

  // 标记有未保存的更改
  hasUnsavedChanges.value = true
}

// 保存更改
async function saveChanges() {
  if (!hasUnsavedChanges.value) {
    Message.info('没有需要保存的更改')
    return
  }

  saving.value = true
  try {
    // TODO: 收集所有变更并调用 bulkUpdate
    Message.success('权限配置已保存')
    hasUnsavedChanges.value = false
  } catch (error) {
    Message.error('保存失败：' + (error as Error).message)
  } finally {
    saving.value = false
  }
}

// 加载权限矩阵
onMounted(async () => {
  try {
    await permissionStore.loadPermissions()
  } catch (error) {
    Message.error('加载权限矩阵失败：' + (error as Error).message)
  }
})
</script>

<style scoped lang="scss">
.permission-matrix-container {
  padding: 24px;

  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;

    h2 {
      margin: 0;
      font-size: 20px;
      font-weight: 600;
    }
  }

  .role-tabs {
    :deep(.arco-tabs-header) {
      margin-bottom: 16px;
    }

    .role-title {
      &.admin {
        color: #f53f3f;
      }
      &.manager {
        color: #ff7d00;
      }
      &.specialist {
        color: #00b42a;
      }
      &.sales {
        color: #165dff;
      }
    }
  }

  .permission-matrix-table {
    background: #fff;
    border-radius: 4px;
  }

  .module-name {
    font-weight: 500;
    color: #1d2129;
  }

  .unsaved-changes-alert {
    margin-top: 16px;
  }
}
</style>
