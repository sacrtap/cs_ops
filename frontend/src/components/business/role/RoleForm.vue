<template>
  <a-form v-bind="formLayout" :model="formData" @finish="handleSubmit">
    <a-form-item
      label="角色名称"
      field="name"
      :rules="[
        { required: true, message: '请输入角色名称' },
        { maxLength: 50, message: '角色名称不能超过 50 个字符' },
      ]"
    >
      <a-input v-model="formData.name" placeholder="请输入角色名称" :disabled="isEdit" />
    </a-form-item>

    <a-form-item
      label="角色描述"
      field="description"
      :rules="[{ maxLength: 500, message: '描述不能超过 500 个字符' }]"
    >
      <a-textarea
        v-model="formData.description"
        placeholder="请输入角色描述"
        :max-length="500"
        show-word-limit
      />
    </a-form-item>

    <a-form-item label="状态" field="status">
      <a-radio-group v-model="formData.status">
        <a-radio value="active">启用</a-radio>
        <a-radio value="inactive">禁用</a-radio>
      </a-radio-group>
    </a-form-item>

    <a-form-item>
      <a-space>
        <a-button type="primary" html-type="submit" :loading="loading"> 提交 </a-button>
        <a-button @click="handleReset">重置</a-button>
      </a-space>
    </a-form-item>
  </a-form>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import type { RoleFormData } from '@/types/role-management'

// Props
const props = defineProps<{
  initialData?: RoleFormData
  isEdit?: boolean
  loading?: boolean
}>()

// Emits
const emit = defineEmits<{
  submit: [data: RoleFormData]
  reset: []
}>()

// Form layout
const formLayout = {
  layout: 'vertical',
  labelCol: { span: 24 },
  wrapperCol: { span: 24 },
}

// Form data
const formData = reactive<RoleFormData>({
  name: '',
  description: '',
  status: 'active',
})

// Watch initial data changes
watch(
  () => props.initialData,
  (newData) => {
    if (newData) {
      formData.name = newData.name
      formData.description = newData.description
      formData.status = newData.status
    }
  },
  { immediate: true }
)

// Submit handler
function handleSubmit() {
  emit('submit', { ...formData })
}

// Reset handler
function handleReset() {
  if (props.initialData) {
    formData.name = props.initialData.name
    formData.description = props.initialData.description
    formData.status = props.initialData.status
  } else {
    formData.name = ''
    formData.description = ''
    formData.status = 'active'
  }
  emit('reset')
}
</script>
