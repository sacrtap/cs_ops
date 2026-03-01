<template>
  <div class="permission-editor">
    <a-table :columns="columns" :data="tableData" :pagination="false" :bordered="true" size="small">
      <template #module="{ record }">
        <span class="module-name">{{ getModuleName(record.module) }}</span>
      </template>

      <template #read="{ record }">
        <a-checkbox
          :model-value="record.read"
          :disabled="disabled"
          @change="onPermissionChange(record, 'read', $event)"
        />
      </template>

      <template #create="{ record }">
        <a-checkbox
          :model-value="record.create"
          :disabled="disabled"
          @change="onPermissionChange(record, 'create', $event)"
        />
      </template>

      <template #update="{ record }">
        <a-checkbox
          :model-value="record.update"
          :disabled="disabled"
          @change="onPermissionChange(record, 'update', $event)"
        />
      </template>

      <template #delete="{ record }">
        <a-checkbox
          :model-value="record.delete"
          :disabled="disabled"
          @change="onPermissionChange(record, 'delete', $event)"
        />
      </template>
    </a-table>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { PermissionMatrix } from '@/types/role-management'

// Props
const props = defineProps<{
  permissions: PermissionMatrix
  disabled?: boolean
}>()

// Emits
const emit = defineEmits<{
  change: [permissions: PermissionMatrix]
}>()

// Modules list
const modules = [
  'customer',
  'settlement',
  'reporting',
  'role',
  'data_permission',
  'function_permission',
]

// Columns
const columns = [
  { title: '功能模块', dataIndex: 'module', slotName: 'module', width: 150 },
  { title: '读取', slotName: 'read', width: 80, align: 'center' },
  { title: '创建', slotName: 'create', width: 80, align: 'center' },
  { title: '更新', slotName: 'update', width: 80, align: 'center' },
  { title: '删除', slotName: 'delete', width: 80, align: 'center' },
]

// Table data
const tableData = computed(() => {
  return modules.map((module) => {
    const perms = props.permissions[module] || {}
    return {
      module,
      read: perms.read ?? false,
      create: perms.create ?? false,
      update: perms.update ?? false,
      delete: perms.delete ?? false,
    }
  })
})

// Get module name
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

// Permission change handler
function onPermissionChange(record: any, action: string, event: Event) {
  if (props.disabled) return

  const target = event.target as HTMLInputElement
  const granted = target.checked

  // Create new permissions object
  const newPermissions: PermissionMatrix = JSON.parse(JSON.stringify(props.permissions))

  if (!newPermissions[record.module]) {
    newPermissions[record.module] = {}
  }
  newPermissions[record.module][action] = granted

  emit('change', newPermissions)
}
</script>

<style scoped lang="scss">
.permission-editor {
  .module-name {
    font-weight: 500;
  }
}
</style>
