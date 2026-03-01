/**
 * 用户 Store - 管理当前用户信息
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export interface UserInfo {
  id: number
  username: string
  email: string
  role: string
}

export const useUserStore = defineStore('user', () => {
  // 状态
  const currentUser = ref<UserInfo | null>(null)

  // 计算属性
  const isLoggedIn = computed(() => currentUser.value !== null)
  const isAdmin = computed(() => currentUser.value?.role === 'admin')
  const username = computed(() => currentUser.value?.username || '')

  // 方法
  function setUser(user: UserInfo) {
    currentUser.value = user
  }

  function clearUser() {
    currentUser.value = null
  }

  return {
    currentUser,
    isLoggedIn,
    isAdmin,
    username,
    setUser,
    clearUser,
  }
})
