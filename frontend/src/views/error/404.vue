<template>
  <div class="error-page">
    <a-result status="404" title="404 Not Found" subtitle="您访问的页面不存在">
      <template #extra>
        <a-space>
          <a-button type="primary" @click="goHome"> 返回首页 </a-button>
          <a-button @click="goBack"> 返回上一页 </a-button>
        </a-space>
      </template>
    </a-result>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

const goHome = () => {
  router.push('/')
}

const goBack = () => {
  router.back()
}
</script>

<style scoped>
.error-page {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
}
</style>
