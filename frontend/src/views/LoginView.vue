<template>
  <div class="login-view">
    <div class="login-container">
      <div class="login-header">
        <h1>CS Ops 运营系统</h1>
        <p>内部运营中台客户信息管理与运营系统</p>
      </div>

      <a-card class="login-card" :bordered="false">
        <h2>用户登录</h2>

        <a-form ref="formRef" :model="loginForm" @submit="handleLogin" layout="vertical">
          <a-form-item
            label="用户名"
            field="username"
            :rules="[
              { required: true, message: '请输入用户名' },
              { minLength: 3, message: '用户名至少 3 个字符' },
            ]"
          >
            <a-input
              v-model="loginForm.username"
              placeholder="请输入用户名"
              size="large"
              allow-clear
            >
              <template #prefix>
                <icon-user />
              </template>
            </a-input>
          </a-form-item>

          <a-form-item
            label="密码"
            field="password"
            :rules="[
              { required: true, message: '请输入密码' },
              { minLength: 6, message: '密码至少 6 个字符' },
            ]"
          >
            <a-input-password
              v-model="loginForm.password"
              placeholder="请输入密码"
              size="large"
              allow-clear
            >
              <template #prefix>
                <icon-lock />
              </template>
            </a-input-password>
          </a-form-item>

          <a-form-item>
            <a-space direction="vertical" size="small" style="width: 100%">
              <a-button type="primary" html-type="submit" size="large" :loading="loading" long>
                {{ loading ? '登录中...' : '登录' }}
              </a-button>

              <a-alert v-if="error" type="error" :content="error" />
            </a-space>
          </a-form-item>
        </a-form>

        <div class="login-tips">
          <a-divider>测试账号</a-divider>
          <p><strong>管理员:</strong> admin / admin123</p>
          <p><strong>经理:</strong> manager / manager123</p>
          <p><strong>销售:</strong> sales / sales123</p>
        </div>
      </a-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { Message } from '@arco-design/web-vue'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const formRef = ref()
const loading = ref(false)
const error = ref('')

const loginForm = reactive({
  username: '',
  password: '',
})

const handleLogin = async () => {
  try {
    await formRef.value.validate()
    loading.value = true
    error.value = ''

    const result = await authStore.login(loginForm.username, loginForm.password)

    if (result.success) {
      Message.success('登录成功')
      // 根据角色跳转到不同页面
      if (result.role === 'admin') {
        router.push('/permissions/audit')
      } else {
        router.push('/dashboard')
      }
    } else {
      error.value = result.error || '登录失败'
      Message.error(error.value)
    }
  } catch (err: any) {
    error.value = err.message || '登录失败'
    Message.error(error.value)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-view {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-container {
  width: 100%;
  max-width: 420px;
  padding: 20px;
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
  color: white;
}

.login-header h1 {
  margin: 0 0 10px 0;
  font-size: 32px;
  font-weight: 600;
}

.login-header p {
  margin: 0;
  font-size: 14px;
  opacity: 0.9;
}

.login-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
}

.login-card h2 {
  margin: 0 0 24px 0;
  text-align: center;
  color: #1d2129;
  font-size: 24px;
}

.login-tips {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #e5e6eb;
}

.login-tips p {
  margin: 8px 0;
  font-size: 13px;
  color: #4e5969;
}

.login-tips strong {
  color: #1d2129;
}
</style>
