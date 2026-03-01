<template>
  <div class="function-access-guard">
    <slot v-if="hasAccess" />
    <div v-else class="access-denied">
      <a-result
        status="403"
        title="没有权限访问此功能"
        :subtitle="`需要权限：${module}.${action}`"
        data-testid="permission-denied-message"
      >
        <template #extra>
          <a-space>
            <a-button type="primary" @click="goBack"> 返回上一页 </a-button>
            <a-button @click="goHome"> 返回首页 </a-button>
          </a-space>
        </template>
      </a-result>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { usePermissionMatrixStore } from '@/stores/permission-matrix'
import { useAuthStore } from '@/stores/auth'

interface Props {
  module: string
  action?: string
}

const props = withDefaults(defineProps<Props>(), {
  action: 'read',
})

const router = useRouter()
const permissionStore = usePermissionMatrixStore()
const authStore = useAuthStore()

// 检查是否有权限
const hasAccess = computed(() => {
  // Admin 拥有所有权限
  if (authStore.user?.role === 'admin') {
    return true
  }

  // 检查具体权限
  return permissionStore.hasPermission(props.module, props.action)
})

// 返回上一页
function goBack() {
  router.back()
}

// 返回首页
function goHome() {
  router.push('/dashboard')
}
</script>

<style scoped lang="scss">
.function-access-guard {
  width: 100%;
  min-height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;

  .access-denied {
    width: 100%;
    max-width: 600px;
    padding: 40px;
  }
}
</style>
