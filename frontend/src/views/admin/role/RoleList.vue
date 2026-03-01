<template>
  <div class="role-management-container" data-testid="role-management-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>角色管理</h2>
      <a-button type="primary" @click="showCreateModal = true" data-testid="create-role-btn">
        <template #icon><icon-plus /></template>
        创建角色
      </a-button>
    </div>

    <!-- 角色列表表格 -->
    <a-table
      :columns="columns"
      :data="roles"
      :loading="loading"
      :pagination="pagination"
      @page-change="onPageChange"
      @page-size-change="onPageSizeChange"
      class="role-list-table"
      data-testid="role-list-table"
    >
      <!-- 角色名称列 -->
      <template #name="{ record }">
        <span :class="['role-name', record.name]">{{ getRoleName(record.name) }}</span>
      </template>

      <!-- 状态列 -->
      <template #status="{ record }">
        <a-tag :color="record.status === 'active' ? 'green' : 'red'">
          {{ record.status === 'active' ? '启用' : '禁用' }}
        </a-tag>
      </template>

      <!-- 用户数量列 -->
      <template #userCount="{ record }">
        <a-tag color="blue">{{ record.user_count || 0 }} 人</a-tag>
      </template>

      <!-- 操作列 -->
      <template #action="{ record }">
        <a-space>
          <a-button
            type="text"
            size="small"
            @click="handleConfigPermissions(record)"
            data-testid="config-permissions-btn"
          >
            配置权限
          </a-button>
          <a-button
            type="text"
            size="small"
            @click="handleEdit(record)"
            data-testid="edit-role-btn"
          >
            编辑
          </a-button>
          <a-popconfirm
            content="确定要删除这个角色吗？"
            @ok="handleDelete(record)"
            :disabled="!isDeletable(record)"
          >
            <a-button
              type="text"
              size="small"
              status="danger"
              :disabled="!isDeletable(record)"
              data-testid="delete-role-btn"
            >
              删除
            </a-button>
          </a-popconfirm>
        </a-space>
      </template>
    </a-table>

    <!-- 创建/编辑角色弹窗 -->
    <a-modal
      v-model:visible="showCreateModal"
      :title="editingRole ? '编辑角色' : '创建角色'"
      @ok="handleSubmit"
      @cancel="showCreateModal = false"
      :confirm-loading="saving"
      width="600px"
    >
      <a-form :model="formData" layout="vertical">
        <a-form-item
          label="角色名称"
          field="name"
          :rules="[
            { required: true, message: '请输入角色名称' },
            { maxLength: 50, message: '角色名称不能超过 50 个字符' },
          ]"
        >
          <a-input v-model="formData.name" placeholder="请输入角色名称" :disabled="!!editingRole" />
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
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Message } from '@arco-design/web-vue'
import { useRoleManagementStore } from '@/stores/role-management'
import type { Role } from '@/types/role-management'

// Router
const router = useRouter()

// Store
const roleStore = useRoleManagementStore()

// State
const loading = ref(false)
const saving = ref(false)
const showCreateModal = ref(false)
const editingRole = ref<Role | null>(null)

// 表单数据
const formData = reactive({
  name: '',
  description: '',
  status: 'active' as 'active' | 'inactive',
})

// 分页
const pagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0,
  showTotal: true,
  showJumper: true,
})

// 表格列定义
const columns = [
  {
    title: '角色名称',
    dataIndex: 'name',
    slotName: 'name',
    width: 200,
  },
  {
    title: '描述',
    dataIndex: 'description',
    width: 300,
  },
  {
    title: '状态',
    dataIndex: 'status',
    slotName: 'status',
    width: 100,
  },
  {
    title: '用户数',
    slotName: 'userCount',
    width: 100,
  },
  {
    title: '创建时间',
    dataIndex: 'created_at',
    width: 180,
  },
  {
    title: '操作',
    slotName: 'action',
    width: 250,
    fixed: 'right',
  },
]

// 获取角色列表
const roles = computed(() => roleStore.roles)

// 角色是否可以删除
function isDeletable(role: Role): boolean {
  const defaultNames = ['admin', 'manager', 'specialist', 'sales']
  return !defaultNames.includes(role.name)
}

// 获取角色显示名称
function getRoleName(name: string): string {
  const names: Record<string, string> = {
    admin: '管理员',
    manager: '经理',
    specialist: '专员',
    sales: '销售',
  }
  return names[name] || name
}

// 分页变更
function onPageChange(page: number) {
  pagination.current = page
}

function onPageSizeChange(pageSize: number) {
  pagination.pageSize = pageSize
  pagination.current = 1
}

// 配置权限
function handleConfigPermissions(role: Role) {
  router.push(`/admin/role/${role.id}/config`)
}

// 编辑角色
function handleEdit(role: Role) {
  editingRole.value = role
  formData.name = role.name
  formData.description = role.description || ''
  formData.status = role.status
  showCreateModal.value = true
}

// 删除角色
async function handleDelete(role: Role) {
  try {
    await roleStore.deleteRole(role.id)
    Message.success('角色删除成功')
  } catch (error) {
    Message.error('删除失败：' + (error as Error).message)
  }
}

// 提交表单
async function handleSubmit() {
  try {
    saving.value = true
    if (editingRole.value) {
      await roleStore.updateRole(editingRole.value.id, {
        description: formData.description,
        status: formData.status,
      })
      Message.success('角色更新成功')
    } else {
      await roleStore.createRole({
        name: formData.name,
        description: formData.description,
        status: formData.status,
      })
      Message.success('角色创建成功')
    }
    showCreateModal.value = false
    resetForm()
  } catch (error) {
    Message.error('操作失败：' + (error as Error).message)
  } finally {
    saving.value = false
  }
}

// 重置表单
function resetForm() {
  editingRole.value = null
  formData.name = ''
  formData.description = ''
  formData.status = 'active'
}

// 加载角色列表
async function loadRoles() {
  loading.value = true
  try {
    await roleStore.loadRoles()
    pagination.total = roleStore.roles.length
  } catch (error) {
    Message.error('加载失败：' + (error as Error).message)
  } finally {
    loading.value = false
  }
}

// 组件挂载时加载数据
onMounted(() => {
  loadRoles()
})
</script>

<style scoped lang="scss">
.role-management-container {
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

  .role-list-table {
    background: #fff;
    border-radius: 4px;
  }

  .role-name {
    font-weight: 500;
    text-transform: capitalize;

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
</style>
