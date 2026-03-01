<template>
  <div class="role-config-container" data-testid="role-config-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-left">
        <a-button type="text" @click="goBack" data-testid="back-btn">
          <template #icon><icon-arrow-left /></template>
          返回
        </a-button>
        <h2 v-if="currentRole">配置权限 - {{ getRoleName(currentRole.name) }}</h2>
      </div>
      <a-button
        type="primary"
        @click="savePermissions"
        :loading="saving"
        data-testid="save-permissions-btn"
      >
        <template #icon><icon-save /></template>
        保存更改
      </a-button>
    </div>

    <!-- 权限矩阵表格 -->
    <a-table
      :columns="columns"
      :data="matrixData"
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
      <template #read="{ record }">
        <a-checkbox
          :model-value="record.read"
          @change="onPermissionChange(record, 'read', $event)"
          data-testid="permission-read-checkbox"
        />
      </template>

      <template #create="{ record }">
        <a-checkbox
          :model-value="record.create"
          @change="onPermissionChange(record, 'create', $event)"
          data-testid="permission-create-checkbox"
        />
      </template>

      <template #update="{ record }">
        <a-checkbox
          :model-value="record.update"
          @change="onPermissionChange(record, 'update', $event)"
          data-testid="permission-update-checkbox"
        />
      </template>

      <template #delete="{ record }">
        <a-checkbox
          :model-value="record.delete"
          @change="onPermissionChange(record, 'delete', $event)"
          data-testid="permission-delete-checkbox"
        />
      </template>
    </a-table>

    <!-- 修改提示 -->
    <a-alert v-if="hasUnsavedChanges" type="warning" show-icon class="unsaved-changes-alert">
      <template #message> 您有未保存的更改，请点击"保存更改"按钮 </template>
    </a-alert>

    <!-- Admin 角色提示 -->
    <a-alert v-if="isAdminRole" type="info" show-icon class="admin-role-alert">
      <template #message> Admin 角色拥有所有权限，无法修改权限配置 </template>
    </a-alert>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, reactive } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Message } from '@arco-design/web-vue'
import { useRoleManagementStore } from '@/stores/role-management'
import type { Role, PermissionMatrix } from '@/types/role-management'

// Router
const route = useRoute()
const router = useRouter()

// Store
const roleStore = useRoleManagementStore()

// State
const saving = ref(false)
const hasUnsavedChanges = ref(false)
const localPermissions = ref<PermissionMatrix>({})

// 当前角色
const currentRole = computed(() => roleStore.currentRole)

// 是否是 Admin 角色
const isAdminRole = computed(() => {
  return currentRole.value?.name === 'admin'
})

// 模块列表
const modules = [
  'customer',
  'settlement',
  'reporting',
  'role',
  'data_permission',
  'function_permission',
]

// 操作列表
const actions = ['read', 'create', 'update', 'delete']

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

// 获取矩阵数据
const matrixData = computed(() => {
  const rolePerms = localPermissions.value

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
})

// 获取角色名称
function getRoleName(name: string): string {
  const names: Record<string, string> = {
    admin: '管理员',
    manager: '经理',
    specialist: '专员',
    sales: '销售',
  }
  return names[name] || name
}

// 获取模块名称
function getModuleName(module: string): string {
  const names: Record<string, string> = {
    customer: '客户管理',
    settlement: '结算管理',
    reporting: '报表管理',
    role: '角色管理',
    data_permission: '数据权限',
    function_permission: '功能权限',
  }
  return names[module] || module
}

// 获取行唯一键
function getRowKey(record: any) {
  return record.module
}

// 权限变更处理
function onPermissionChange(record: any, action: string, event: Event) {
  const target = event.target as HTMLInputElement
  const granted = target.checked

  // 更新本地权限数据
  if (!localPermissions.value[record.module]) {
    localPermissions.value[record.module] = {}
  }
  localPermissions.value[record.module][action] = granted

  // 标记有未保存的更改
  hasUnsavedChanges.value = true
}

// 保存权限
async function savePermissions() {
  if (!currentRole.value) {
    Message.error('角色信息不存在')
    return
  }

  if (isAdminRole.value) {
    Message.warning('Admin 角色权限无法修改')
    return
  }

  if (!hasUnsavedChanges.value) {
    Message.info('没有需要保存的更改')
    return
  }

  saving.value = true
  try {
    await roleStore.updateRolePermissions(currentRole.value.id, localPermissions.value)
    Message.success('权限配置已保存')
    hasUnsavedChanges.value = false
  } catch (error) {
    Message.error('保存失败：' + (error as Error).message)
  } finally {
    saving.value = false
  }
}

// 返回上一页
function goBack() {
  router.back()
}

// 加载角色权限
async function loadRolePermissions() {
  const roleId = Number(route.params.id)
  if (!roleId) {
    Message.error('角色 ID 无效')
    router.back()
    return
  }

  try {
    await roleStore.loadRoleWithPermissions(roleId)
    if (currentRole.value) {
      // 复制权限数据到本地
      localPermissions.value = JSON.parse(JSON.stringify(currentRole.value.permissions))
    }
  } catch (error) {
    Message.error('加载权限配置失败：' + (error as Error).message)
    router.back()
  }
}

// 组件挂载时加载数据
onMounted(() => {
  loadRolePermissions()
})
</script>

<style scoped lang="scss">
.role-config-container {
  padding: 24px;

  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;

    .header-left {
      display: flex;
      align-items: center;
      gap: 16px;

      h2 {
        margin: 0;
        font-size: 20px;
        font-weight: 600;
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

  .admin-role-alert {
    margin-top: 16px;
  }
}
</style>
