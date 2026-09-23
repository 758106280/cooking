<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

import { api } from '../api'

const router = useRouter()
const isRegister = ref(false)
const username = ref('admin')
const nickname = ref('')
const password = ref('change-me')
const error = ref('')
const loading = ref(false)

async function submit() {
  loading.value = true
  error.value = ''
  try {
    const user = isRegister.value
      ? await api.register(username.value, password.value, nickname.value)
      : await api.login(username.value, password.value)
    await router.push(user.role === 'admin' ? '/admin/recipes' : '/')
  } catch (err) {
    error.value = err instanceof Error ? err.message : '操作失败'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <section class="auth-card">
    <p class="eyebrow dark">{{ isRegister ? 'JOIN FAMILY' : 'SIGN IN' }}</p>
    <h1>{{ isRegister ? '创建账户' : '登录' }}</h1>
    <form class="form-stack" @submit.prevent="submit">
      <label>用户名<input v-model="username" required minlength="3" autocomplete="username" /></label>
      <label v-if="isRegister">昵称<input v-model="nickname" placeholder="家人的称呼" maxlength="64" /></label>
      <label>密码<input v-model="password" required minlength="6" type="password" autocomplete="current-password" /></label>
      <p v-if="error" class="error-message">{{ error }}</p>
      <button class="primary-button" :disabled="loading" type="submit">{{ loading ? '处理中...' : isRegister ? '注册并登录' : '登录' }}</button>
      <button class="secondary-button" type="button" @click="isRegister = !isRegister">{{ isRegister ? '已有账号，去登录' : '创建家庭成员账号' }}</button>
    </form>
  </section>
</template>
