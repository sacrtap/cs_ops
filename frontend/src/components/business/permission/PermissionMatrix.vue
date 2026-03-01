<template>
  <div class="permission-matrix">
    <a-table :data="tableData" :columns="columns" :pagination="false" :bordered="true" size="small">
      <template #action="{ record }">
        <a-switch
          v-if="record.editable"
          v-model="record.checked"
          :disabled="!canEdit"
          @change="handlePermissionChange(record)"
        />
        <a-tag v-else :color="record.checked ? 'green' : 'red'">
          {{ record.checked ? '允许' : '禁止' }}
        </a-tag>
      </template>
    </a-table>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { usePermissionStore } from '@/stores/permission'
import type { PermissionMatrix, PermissionResource, PermissionAction } from '@/types/permission'

interface Props {
  matrix?: PermissionMatrix
  role?: string // 如果指定角色，只编辑该角色的权限
  readonly?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  matrix: () => ({}),
  role: '',
  readonly: false,
})

const emit = defineEmits<{
  change: [role: string, resource: string, action: string, enabled: boolean]
}>()

const permissionStore = usePermissionStore()

// 当前角色（从 localStorage 获取）
const currentRole = localStorage.getItem('user_role') || ''

// 是否可以编辑（仅 Admin 可以编辑权限矩阵）
const canEdit = computed(() => {
  return currentRole === 'admin' && !props.readonly
})

// 表格列定义
const columns = computed(() => {
  const resourceActions: PermissionAction[] = [
    'create',
    'read',
    'update',
    'delete',
    'view',
    'export',
  ]

  return [
    { title: '资源', dataIndex: 'resource', key: 'resource', fixed: 'left', width: 120 },
    ...resourceActions.map((action) => ({
      title: action.toUpperCase(),
      dataIndex: action,
      key: action,
      width: 100,
      slotName: 'action',
    })),
  ]
})

// 表格数据
const tableData = ref<any[]>([])

// 构建表格数据
function buildTableData() {
  const targetRole = props.role || currentRole
  const roleMatrix = props.matrix[targetRole] || {}
  const resources: PermissionResource[] = ['customer', 'settlement', 'report', 'user', 'role']

  tableData.value = resources.map((resource) => {
    const actions = roleMatrix[resource] || []
    const row: any = {
      resource: getResourceLabel(resource),
      resourceKey: resource,
      editable: canEdit.value && resource !== 'role', // 角色管理权限不可编辑
    }

    const allActions: PermissionAction[] = ['create', 'read', 'update', 'delete', 'view', 'export']
    allActions.forEach((action) => {
      const hasPermission = actions.includes(action)
      row[action] = hasPermission
      row[`${action}_checked`] = hasPermission
    })

    return row
  })
}

// 资源名称映射
const resourceLabels: Record<string, string> = {
  customer: '客户',
  settlement: '结算',
  report: '报表',
  user: '用户',
  role: '角色',
}

function getResourceLabel(resource: string): string {
  return resourceLabels[resource] || resource
}

// 处理权限变更
function handlePermissionChange(record: any) {
  const resource = record.resourceKey
  const role = props.role || currentRole

  // 找到变更的操作
  const actions: PermissionAction[] = ['create', 'read', 'update', 'delete', 'view', 'export']
  actions.forEach((action) => {
    const oldValue = record[`${action}_checked`]
    const newValue = record[action]

    if (oldValue !== newValue) {
      emit('change', role, resource, action, newValue)
      record[`${action}_checked`] = newValue
    }
  })
}

// 监听矩阵变化
watch(() => props.matrix, buildTableData, { deep: true, immediate: true })
</script>

<style scoped>
.permission-matrix {
  overflow-x: auto;
}

:deep(.arco-table) {
  font-size: 13px;
}
</style>
