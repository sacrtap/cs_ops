<template>
  <div class="login-container">
    <div class="login-box">
      <!-- Logo 和标题 -->
      <div class="login-header">
        <h1 class="login-title">CS Ops 运营系统</h1>
        <p class="login-subtitle">客户成功运营平台</p>
      </div>

      <!-- 登录表单 -->
      <a-form
        ref="formRef"
        :model="form"
        :rules="rules"
        layout="vertical"
        @submit="handleSubmit"
      >
        <!-- 用户名 -->
        <a-form-item field="username" label="用户名">
          <a-input
            v-model="form.username"
            placeholder="请输入用户名"
            size="large"
            :disabled="loading"
          >
            <template #prefix>
              <icon-user />
            </template>
          </a-input>
        </a-form-item>

        <!-- 密码 -->
        <a-form-item field="password" label="密码">
          <a-input-password
            v-model="form.password"
            placeholder="请输入密码"
            size="large"
            :disabled="loading"
          >
            <template #prefix>
              <icon-lock />
            </template>
          </a-input-password>
        </a-form-item>

        <!-- 错误提示 -->
        <a-alert v-if="error" type="error" :closable="true" @close="clearError">
          {{ error }}
        </a-alert>

        <!-- 登录按钮 -->
        <a-form-item>
          <a-button
            type="primary"
            html-type="submit"
            size="large"
            long
            :loading="loading"
          >
            {{ loading ? '登录中...' : '登录' }}
          </a-button>
        </a-form-item>
      </a-form>

      <!-- 底部信息 -->
      <div class="login-footer">
        <p class="login-tip">
          <icon-info-circle />
          演示账号：admin / admin123
        </p>
      </div>
    </div>

    <!-- 版权信息 -->
    <div class="login-copyright">
      <p>© 2026 CS Ops. All rights reserved.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage } from '@arco-design/web-vue'
import { useAuthStore } from '@/stores/auth'
import type { FormInstance, FormRules } from '@arco-design/web-vue'

const router = useRouter()
const message = useMessage()
const authStore = useAuthStore()

// 表单引用
const formRef = ref<FormInstance>()

// 表单数据
const form = reactive({
  username: '',
  password: '',
})

// 表单验证规则
const rules: FormRules = {
  username: [
    { required: true, message: '请输入用户名' },
    { minLength: 3, maxLength: 50, message: '用户名长度应在 3-50 个字符之间' },
  ],
  password: [
    { required: true, message: '请输入密码' },
    { minLength: 6, message: '密码长度至少 6 个字符' },
  ],
}

// 登录处理
const handleSubmit = async () => {
  // 验证表单
  const valid = await formRef.value?.validate()
  if (valid) return

  // 调用登录接口
  const result = await authStore.login(form)

  if (result.success) {
    message.success('登录成功')
    // 跳转到首页
    router.push('/')
  } else {
    message.error(result.error || '登录失败')
  }
}

// 清除错误
const clearError = () => {
  authStore.clearError()
}

// 计算属性
const loading = authStore.isLoading
const error = authStore.error
</script>

<style scoped lang="less">
.login-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.login-box {
  width: 100%;
  max-width: 420px;
  padding: 40px;
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.login-title {
  font-size: 28px;
  font-weight: 600;
  color: #1d2129;
  margin: 0 0 8px 0;
}

.login-subtitle {
  font-size: 14px;
  color: #86909c;
  margin: 0;
}

.login-footer {
  margin-top: 24px;
  text-align: center;
}

.login-tip {
  font-size: 13px;
  color: #86909c;
  margin: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
}

.login-copyright {
  margin-top: 24px;
  text-align: center;
  color: rgba(255, 255, 255, 0.8);
  font-size: 13px;

  p {
    margin: 0;
  }
}

// 覆盖 Arco Design 默认样式
:deep(.arco-form-item) {
  margin-bottom: 20px;
}

:deep(.arco-input-wrapper) {
  padding: 12px 16px;
}

:deep(.arco-btn-primary) {
  height: 44px;
  font-size: 16px;
  font-weight: 500;
}
</style>
