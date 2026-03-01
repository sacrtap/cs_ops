<template>
  <div class="role-management">
    <a-card title="角色管理" :bordered="false">
      <!-- 角色列表 -->
      <a-table
        :data="roleList"
        :columns="roleColumns"
        :loading="loading"
        :pagination="false"
        size="small"
      >
        <template #roleName="{ record }">
          <a-tag :color="getRoleColor(record.role)" size="large">
            {{ record.name }}
          </a-tag>
        </template>
        <template #permissions="{ record }">
          <a-popover position="right">
            <a-button type="text" size="small">
              {{ getPermissionCount(record.role) }} 个权限
            </a-button>
            <template #content>
              <permission-matrix :matrix="permissionMatrix" :role="record.role" readonly />
            </template>
          </a-popover>
        </template>
      </a-table>
    </a-card>

    <!-- 用户角色分配 -->
    <a-card title="用户角色分配" :bordered="false" style="margin-top: 16px">
      <a-table
        :data="userList"
        :columns="userColumns"
        :loading="loading"
        :pagination="pagination"
        size="small"
      >
        <template #role="{ record }">
          <role-selector
            v-model="record.role"
            :disabled="!canEditUserRole(record)"
            @change="handleUserRoleChange(record)"
          />
        </template>
      </a-table>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Message } from '@arco-design/web-vue'
import { usePermissionStore } from '@/stores/permission'
import RoleSelector from '@/components/business/permission/RoleSelector.vue'
import PermissionMatrix from '@/components/business/permission/PermissionMatrix.vue'

const permissionStore = usePermissionStore()

// 状态
const loading = ref(false)
const roleList = ref<any[]>([])
const userList = ref<any[]>([])
const permissionMatrix = ref<any>({})

// 当前用户角色
const currentRole = localStorage.getItem('user_role') || ''

// 是否可以编辑用户角色（Manager 及以上）
const canEditUserRole = (user: any) => {
  const roleHierarchy: Record<string, number> = {
    admin: 4,
    manager: 3,
    specialist: 2,
    sales: 1,
  }
  const currentLevel = roleHierarchy[currentRole] || 0
  const userLevel = roleHierarchy[user.role] || 0
  return currentLevel > userLevel
}

// 角色表格列
const roleColumns = [
  { title: '角色', dataIndex: 'name', key: 'name', slotName: 'roleName' },
  { title: '级别', dataIndex: 'level', key: 'level' },
  { title: '描述', dataIndex: 'description', key: 'description' },
  { title: '权限', dataIndex: 'permissions', key: 'permissions', slotName: 'permissions' },
]

// 用户表格列
const userColumns = [
  { title: '用户名', dataIndex: 'username', key: 'username' },
  { title: '姓名', dataIndex: 'real_name', key: 'real_name' },
  { title: '角色', dataIndex: 'role', key: 'role', slotName: 'role' },
  { title: '状态', dataIndex: 'status', key: 'status' },
]

// 分页
const pagination = {
  current: 1,
  pageSize: 20,
  total: 0,
}

// 获取角色颜色
const roleColors: Record<string, string> = {
  admin: 'red',
  manager: 'orange',
  specialist: 'blue',
  sales: 'green',
}

function getRoleColor(role: string): string {
  return roleColors[role] || 'gray'
}

// 获取权限数量
function getPermissionCount(role: string): number {
  const roleMatrix = permissionMatrix.value[role] || {}
  let count = 0
  Object.values(roleMatrix).forEach((actions: any) => {
    count += Array.isArray(actions) ? actions.length : 0
  })
  return count
}

// 处理用户角色变更
async function handleUserRoleChange(user: any) {
  loading.value = true
  try {
    const response = await permissionStore.updateUserRole(user.id, user.role)
    if (response.success) {
      Message.success(`用户 ${user.username} 角色已更新为 ${user.role}`)
    } else {
      Message.error(response.error || '更新失败')
      // 恢复原角色
      user.role = user._originalRole
    }
  } catch (err) {
    Message.error('更新失败')
    user.role = user._originalRole
  } finally {
    loading.value = false
  }
}

// 加载数据
async function loadData() {
  loading.value = true
  try {
    // 加载角色列表
    await permissionStore.loadRoles()
    roleList.value = permissionStore.roles

    // 加载权限矩阵
    const matrixResponse = await permissionStore.loadPermissionMatrix()
    permissionMatrix.value = matrixResponse.data || {}

    // TODO: 加载用户列表（需要用户管理 API）
    userList.value = []
  } catch (err) {
    Message.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.role-management {
  padding: 20px;
}
</style>
