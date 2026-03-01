<!--
数据范围选择器组件

功能:
- 显示当前用户可用的数据范围
- 允许用户切换数据范围
- 显示当前数据范围标签

Story 1.4: Data Permission
-->
<template>
  <div class="data-scope-selector">
    <label v-if="showLabel" class="selector-label"> 数据范围： </label>

    <el-select
      v-model="currentScope"
      :placeholder="placeholder"
      :size="size"
      :disabled="disabled || isLoading"
      :loading="isLoading"
      @change="handleScopeChange"
    >
      <el-option
        v-for="scope in availableScopes"
        :key="scope.scope"
        :label="scope.label"
        :value="scope.scope"
      >
        <div class="scope-option">
          <span>{{ scope.label }}</span>
          <span class="scope-description">{{ scope.description }}</span>
        </div>
      </el-option>
    </el-select>

    <!-- 数据范围提示 -->
    <div v-if="showTip && currentScopeInfo" class="scope-tip">
      <el-icon><Info-Filled /></el-icon>
      <span>{{ currentScopeInfo.description }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { InfoFilled } from '@element-plus/icons-vue'
import { useDataPermissionStore } from '@/stores/data-permission'
import type { DataScope } from '@/types/data-permission'

// ==================== Props ====================

interface Props {
  showLabel?: boolean
  showTip?: boolean
  placeholder?: string
  size?: 'large' | 'default' | 'small'
  disabled?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  showLabel: false,
  showTip: true,
  placeholder: '请选择数据范围',
  size: 'default',
  disabled: false,
})

// ==================== Emits ====================

const emit = defineEmits<{
  change: [scope: DataScope, orgId?: number]
}>()

// ==================== State ====================

const dataPermissionStore = useDataPermissionStore()
const currentScope = ref<DataScope | null>(null)

// ==================== Computed ====================

const isLoading = computed(() => dataPermissionStore.isLoading)

const availableScopes = computed(() => dataPermissionStore.availableScopes)

const currentScopeInfo = computed(() => dataPermissionStore.currentScopeInfo)

// ==================== Methods ====================

/**
 * 处理数据范围切换
 */
async function handleScopeChange(scope: DataScope) {
  if (!scope) {
    return
  }

  // 获取组织 ID（如果是组织范围）
  const orgId = scope === 'organization' ? dataPermissionStore.currentOrgId || undefined : undefined

  // 切换数据范围
  const result = await dataPermissionStore.changeDataScope(scope, orgId)

  if (result.success) {
    emit('change', scope, orgId)
  }
}

/**
 * 初始化
 */
onMounted(async () => {
  // 加载数据范围和用户权限
  await dataPermissionStore.initialize()

  // 设置当前数据范围
  currentScope.value = dataPermissionStore.currentScope
})

// 监听 store 中的 currentScope 变化
watch(
  () => dataPermissionStore.currentScope,
  (newScope) => {
    if (newScope) {
      currentScope.value = newScope
    }
  }
)
</script>

<style scoped lang="scss">
.data-scope-selector {
  display: inline-block;

  .selector-label {
    margin-right: 8px;
    font-weight: 500;
    color: #606266;
  }

  .scope-option {
    display: flex;
    flex-direction: column;
    gap: 4px;

    .scope-description {
      font-size: 12px;
      color: #909399;
    }
  }

  .scope-tip {
    display: flex;
    align-items: center;
    gap: 4px;
    margin-top: 8px;
    padding: 8px 12px;
    background-color: #f5f7fa;
    border-radius: 4px;
    font-size: 12px;
    color: #606266;

    .el-icon {
      color: #909399;
    }
  }
}
</style>
