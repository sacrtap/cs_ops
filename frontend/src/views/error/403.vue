<template>
  <div class="error-403-page" data-testid="403-page">
    <a-result
      class="error-result"
      status="403"
      title="403 无权访问"
      :subtitle="errorMessage"
      data-testid="permission-denied-message"
    >
      <template #icon>
        <icon-forbidden style="color: #f53f3f; font-size: 80px" />
      </template>

      <template #extra>
        <a-space direction="vertical" size="large">
          <a-alert type="warning">
            <template #title>
              您尝试访问的功能需要以下权限：
              <div class="permission-details">
                <a-tag color="blue">{{ module }}</a-tag>
                <a-tag color="green">{{ action }}</a-tag>
              </div>
              <div class="role-info">
                当前角色：<a-tag color="red">{{ role }}</a-tag>
              </div>
            </template>
          </a-alert>

          <a-space>
            <a-button type="primary" @click="goBack">
              <template #icon><icon-arrow-left /></template>
              返回上一页
            </a-button>
            <a-button @click="goHome" data-testid="back-to-home-btn">
              <template #icon><icon-home /></template>
              返回首页
            </a-button>
            <a-button v-if="showContactSupport" @click="contactSupport">
              <template #icon><icon-customer-service /></template>
              联系管理员
            </a-button>
          </a-space>
        </a-space>
      </template>
    </a-result>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

// 从路由参数获取权限信息
const module = computed(() => (route.query.module as string) || 'unknown')
const action = computed(() => (route.query.action as string) || 'unknown')
const role = computed(() => (route.query.role as string) || authStore.user?.role || 'unknown')
const reason = computed(() => route.query.reason as string)

// 错误消息
const errorMessage = computed(() => {
  if (reason.value === 'requires_admin') {
    return '此功能仅限管理员访问，您当前使用的账户没有足够的权限。'
  }
  return `您没有权限访问此功能。如需访问，请联系管理员开通 "${module.value}" 模块的 "${action.value}" 权限。`
})

// 是否显示联系管理员按钮
const showContactSupport = computed(() => {
  return authStore.user?.role !== 'admin'
})

// 返回上一页
function goBack() {
  router.back()
}

// 返回首页
function goHome() {
  router.push('/dashboard')
}

// 联系管理员
function contactSupport() {
  // TODO: 实现联系管理员功能（发送邮件或工单）
  window.location.href = 'mailto:admin@example.com?subject=权限申请'
}

// 如果已登录且权限发生变化，自动检测是否可以访问
onMounted(async () => {
  // 这里可以添加权限刷新逻辑
})
</script>

<style scoped lang="scss">
.error-403-page {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 600px;
  padding: 24px;

  .error-result {
    max-width: 700px;
    width: 100%;
  }

  .permission-details {
    margin-top: 8px;
    display: flex;
    gap: 8px;
  }

  .role-info {
    margin-top: 8px;
  }
}
</style>
