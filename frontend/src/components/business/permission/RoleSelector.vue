<template>
  <a-select
    :model-value="modelValue"
    :options="roleOptions"
    :placeholder="placeholder"
    :disabled="disabled"
    :loading="loading"
    @change="handleRoleChange"
  >
    <template #prefix>
      <icon-user />
    </template>
    <template #label="{ data }">
      <a-tag :color="getRoleColor(data.value)" size="small">
        {{ data.label }}
      </a-tag>
    </template>
  </a-select>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { usePermissionStore } from '@/stores/permission'
import type { Role } from '@/types/permission'

interface Props {
  modelValue?: string
  placeholder?: string
  disabled?: boolean
  loading?: boolean
  excludeRoles?: string[] // 排除某些角色
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: '',
  placeholder: '请选择角色',
  disabled: false,
  loading: false,
  excludeRoles: () => [],
})

const emit = defineEmits<{
  'update:modelValue': [value: string]
  change: [value: string, role: Role]
}>()

const permissionStore = usePermissionStore()

// 角色选项
const roleOptions = computed(() => {
  return permissionStore.roles
    .filter((role) => !props.excludeRoles.includes(role.role))
    .map((role) => ({
      label: role.name,
      value: role.role,
      level: role.level,
      description: role.description,
    }))
    .sort((a, b) => b.level - a.level) // 按级别降序排序
})

// 角色颜色映射
const roleColors: Record<string, string> = {
  admin: 'red',
  manager: 'orange',
  specialist: 'blue',
  sales: 'green',
}

function getRoleColor(role: string): string {
  return roleColors[role] || 'gray'
}

// 处理角色变更
function handleRoleChange(value: string) {
  const role = permissionStore.roles.find((r) => r.role === value)
  if (role) {
    emit('update:modelValue', value)
    emit('change', value, role)
  }
}

// 加载角色列表
onMounted(async () => {
  if (permissionStore.roles.length === 0) {
    await permissionStore.loadRoles()
  }
})
</script>

<style scoped>
:deep(.arco-select-view-single) {
  min-width: 150px;
}
</style>
