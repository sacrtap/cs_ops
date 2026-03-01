<template>
  <div class="permission-hierarchy">
    <a-card title="角色层级关系" :bordered="false">
      <template #extra>
        <a-button type="text" @click="refreshHierarchy">
          <template #icon><icon-refresh /></template>
          刷新
        </a-button>
      </template>

      <!-- 层级可视化 -->
      <div class="hierarchy-tree">
        <div
          v-for="level in hierarchyLevels"
          :key="level.role"
          class="hierarchy-node"
          :class="{ 'is-active': selectedRole === level.role }"
          @click="selectRole(level.role)"
        >
          <div class="node-content">
            <div class="node-header">
              <a-tag :color="getRoleTagColor(level.level)" size="large">
                {{ level.name }}
              </a-tag>
              <span class="node-level">L{{ level.level }}</span>
            </div>

            <div class="node-role-name">
              <icon-user />
              {{ level.role }}
            </div>

            <!-- 继承关系指示 -->
            <div v-if="level.inherits.length > 0" class="inherits-from">
              <div class="inherits-label">
                <icon-down />
                继承自
              </div>
              <div class="inherited-roles">
                <a-tag
                  v-for="inheritedRole in level.inherits"
                  :key="inheritedRole"
                  color="gray"
                  size="small"
                >
                  {{ inheritedRole }}
                </a-tag>
              </div>
            </div>

            <!-- 权限统计 -->
            <div class="permission-stats" v-if="rolePermissions[level.role]">
              <a-space size="small">
                <a-statistic
                  title="直接权限"
                  :value="rolePermissions[level.role].direct_permissions?.length || 0"
                  :value-style="{ fontSize: '14px' }"
                />
                <a-statistic
                  title="继承权限"
                  :value="rolePermissions[level.role].inherited_permissions?.length || 0"
                  :value-style="{ fontSize: '14px' }"
                />
              </a-space>
            </div>
          </div>

          <!-- 连接线 -->
          <div v-if="level.inherits.length > 0" class="connection-line">
            <icon-down />
          </div>
        </div>
      </div>

      <!-- 权限详情面板 -->
      <a-divider />

      <div v-if="selectedRole" class="permission-details">
        <div class="details-header">
          <h3>
            <icon-user />
            {{ getRoleName(selectedRole) }} - 权限详情
          </h3>
          <a-space>
            <a-button size="small" @click="showAllPermissions = !showAllPermissions">
              {{ showAllPermissions ? '收起' : '展开全部' }}
            </a-button>
            <a-button size="small" @click="refreshPermissions">
              <template #icon><icon-refresh /></template>
              刷新
            </a-button>
          </a-space>
        </div>

        <a-descriptions :column="1" bordered>
          <a-descriptions-item label="角色层级">
            <a-tag :color="getRoleTagColor(currentRoleLevel?.level || 1)">
              L{{ currentRoleLevel?.level }}
            </a-tag>
          </a-descriptions-item>

          <a-descriptions-item label="继承来源">
            <a-space wrap>
              <a-tag
                v-for="source in currentRolePermissions?.inherited_from || []"
                :key="source"
                color="blue"
              >
                {{ source }}
              </a-tag>
              <a-empty
                v-if="!currentRolePermissions?.inherited_from?.length"
                description="无继承来源（最高级别）"
                :style="{ margin: '8px 0' }"
              />
            </a-space>
          </a-descriptions-item>

          <!-- 继承权限列表 -->
          <a-descriptions-item label="继承权限">
            <a-collapse v-if="showAllPermissions">
              <a-collapse-panel
                v-for="(perms, resource) in groupedInheritedPermissions"
                :key="resource"
                :header="`资源：${resource} (${perms.length})`"
              >
                <a-table
                  :columns="inheritedPermissionColumns"
                  :data-source="perms"
                  :pagination="false"
                  size="small"
                  :scroll="{ y: 200 }"
                >
                  <template #bodyCell="{ column, record }">
                    <template v-if="column.dataIndex === 'inherited_from'">
                      <a-tag color="blue">{{ record.inherited_from }}</a-tag>
                    </template>
                  </template>
                </a-table>
              </a-collapse-panel>
            </a-collapse>

            <div v-else class="compact-permissions">
              <a-tag
                v-for="perm in currentRolePermissions?.inherited_permissions?.slice(0, 10) || []"
                :key="`${perm.resource}-${perm.action}`"
                color="blue"
                size="small"
              >
                {{ perm.resource }}:{{ perm.action }}
                <template #icon>
                  <icon-arrow-down :size="12" />
                </template>
              </a-tag>
              <a-tag
                v-if="(currentRolePermissions?.inherited_permissions?.length || 0) > 10"
                color="gray"
              >
                +{{ (currentRolePermissions?.inherited_permissions?.length || 0) - 10 }} 更多
              </a-tag>
            </div>
          </a-descriptions-item>

          <!-- 直接权限列表 -->
          <a-descriptions-item label="直接权限">
            <div class="direct-permissions">
              <a-tag
                v-for="perm in currentRolePermissions?.direct_permissions || []"
                :key="`${perm.resource}-${perm.action}`"
                color="green"
                size="small"
              >
                {{ perm.resource }}:{{ perm.action }}
              </a-tag>
              <a-empty
                v-if="!currentRolePermissions?.direct_permissions?.length"
                description="无直接权限"
                :style="{ margin: '8px 0' }"
              />
            </div>
          </a-descriptions-item>

          <!-- 所有权限统计 -->
          <a-descriptions-item label="权限统计">
            <a-space size="large">
              <a-statistic
                title="总权限数"
                :value="currentRolePermissions?.all_permissions?.length || 0"
                :value-style="{ fontSize: '18px', fontWeight: 'bold' }"
              />
              <a-statistic
                title="直接权限"
                :value="currentRolePermissions?.direct_permissions?.length || 0"
                :value-style="{ fontSize: '16px', color: '#52c41a' }"
              />
              <a-statistic
                title="继承权限"
                :value="currentRolePermissions?.inherited_permissions?.length || 0"
                :value-style="{ fontSize: '16px', color: '#1890ff' }"
              />
            </a-space>
          </a-descriptions-item>
        </a-descriptions>
      </div>

      <a-empty v-else description="点击左侧角色查看权限详情" :style="{ margin: '40px 0' }" />
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Message } from '@arco-design/web-vue'
import { IconRefresh, IconUser, IconDown, IconArrowDown } from '@arco-design/web-vue/es/icon'
import { getRoleHierarchy, getRolePermissions } from '@/api/permission'
import type { RoleHierarchyLevel, RolePermissionsDetail } from '@/types/permission'

// ==================== 响应式数据 ====================

const hierarchyLevels = ref<RoleHierarchyLevel[]>([])
const rolePermissions = ref<Record<string, RolePermissionsDetail>>({})
const selectedRole = ref<string | null>(null)
const showAllPermissions = ref(false)
const loading = ref(false)

// ==================== 计算属性 ====================

const currentRoleLevel = computed(() => {
  if (!selectedRole.value) return null
  return hierarchyLevels.value.find((l) => l.role === selectedRole.value) || null
})

const currentRolePermissions = computed(() => {
  if (!selectedRole.value) return null
  return rolePermissions.value[selectedRole.value] || null
})

const groupedInheritedPermissions = computed(() => {
  if (!currentRolePermissions.value?.inherited_permissions) return {}

  const grouped: Record<string, any[]> = {}
  currentRolePermissions.value.inherited_permissions.forEach((perm) => {
    if (!grouped[perm.resource]) {
      grouped[perm.resource] = []
    }
    grouped[perm.resource].push(perm)
  })
  return grouped
})

const inheritedPermissionColumns = [
  {
    title: '资源',
    dataIndex: 'resource',
    width: 120,
  },
  {
    title: '操作',
    dataIndex: 'action',
    width: 100,
  },
  {
    title: '继承自',
    dataIndex: 'inherited_from',
    width: 120,
  },
]

// ==================== 方法 ====================

/**
 * 获取角色层级结构
 */
async function loadHierarchy() {
  try {
    loading.value = true
    const response = await getRoleHierarchy()
    hierarchyLevels.value = response.data.levels || []
  } catch (error: any) {
    Message.error(`加载角色层级失败：${error.message || '未知错误'}`)
  } finally {
    loading.value = false
  }
}

/**
 * 获取指定角色的权限详情
 */
async function loadRolePermissions(roleName: string) {
  try {
    const response = await getRolePermissions(roleName)
    rolePermissions.value[roleName] = response.data
  } catch (error: any) {
    Message.error(`加载角色权限失败：${error.message || '未知错误'}`)
  }
}

/**
 * 刷新层级结构
 */
async function refreshHierarchy() {
  await loadHierarchy()
  Message.success('角色层级已刷新')
}

/**
 * 刷新权限详情
 */
async function refreshPermissions() {
  if (selectedRole.value) {
    await loadRolePermissions(selectedRole.value)
    Message.success('权限详情已刷新')
  }
}

/**
 * 选择角色
 */
async function selectRole(roleName: string) {
  selectedRole.value = roleName

  // 如果该角色的权限未加载，则加载
  if (!rolePermissions.value[roleName]) {
    await loadRolePermissions(roleName)
  }
}

/**
 * 获取角色显示名称
 */
function getRoleName(role: string): string {
  const level = hierarchyLevels.value.find((l) => l.role === role)
  return level?.name || role
}

/**
 * 获取角色标签颜色
 */
function getRoleTagColor(level: number): string {
  const colorMap: Record<number, string> = {
    4: 'red', // Admin
    3: 'orange', // Manager
    2: 'blue', // Specialist
    1: 'green', // Sales
  }
  return colorMap[level] || 'gray'
}

// ==================== 生命周期 ====================

onMounted(async () => {
  await loadHierarchy()

  // 默认选择第一个角色（最高级别）
  if (hierarchyLevels.value.length > 0) {
    const topLevel = hierarchyLevels.value[0]
    selectRole(topLevel.role)
  }
})
</script>

<style scoped lang="less">
.permission-hierarchy {
  width: 100%;
}

.hierarchy-tree {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 20px 0;
}

.hierarchy-node {
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
  transition: all 0.3s ease;

  &.is-active {
    transform: scale(1.05);

    .node-content {
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
      border-color: var(--color-primary-6);
    }
  }
}

.node-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 16px;
  border: 2px solid var(--color-border-2);
  border-radius: 8px;
  background: var(--color-bg-2);
  min-width: 280px;
  transition: all 0.3s ease;

  &:hover {
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }
}

.node-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.node-level {
  font-size: 12px;
  font-weight: bold;
  color: var(--color-text-3);
}

.node-role-name {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: var(--color-text-1);
  font-weight: 500;
}

.inherits-from {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 8px;
  background: var(--color-fill-2);
  border-radius: 4px;
}

.inherits-label {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: var(--color-text-3);
  font-weight: 500;
}

.inherited-roles {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.permission-stats {
  display: flex;
  justify-content: center;
  gap: 16px;
  padding-top: 8px;
  border-top: 1px solid var(--color-border-1);
}

.connection-line {
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-3);
  font-size: 20px;
  margin-top: -8px;
}

.permission-details {
  margin-top: 16px;
}

.details-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;

  h3 {
    display: flex;
    align-items: center;
    gap: 8px;
    margin: 0;
    font-size: 16px;
    font-weight: 600;
  }
}

.compact-permissions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.direct-permissions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

:deep(.arco-descriptions-item-label) {
  font-weight: 500;
}

:deep(.arco-statistic-title) {
  font-size: 12px !important;
}

:deep(.arco-collapse-item-header) {
  font-size: 13px;
}
</style>
