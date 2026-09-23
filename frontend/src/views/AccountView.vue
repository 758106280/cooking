<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

import { api, type UserProfile } from '../api'

const router = useRouter()
const profile = ref<UserProfile | null>(null)
const form = reactive({ nickname: '' })
const error = ref('')
const message = ref('')

onMounted(async () => {
  try {
    profile.value = await api.me()
    form.nickname = profile.value.nickname || profile.value.username
  } catch {
    await router.push('/admin/login')
  }
})

async function save() {
  error.value = ''
  message.value = ''
  try {
    profile.value = await api.updateProfile({ nickname: form.nickname })
    message.value = '资料已保存'
  } catch (err) {
    error.value = err instanceof Error ? err.message : '保存失败'
  }
}

async function logout() {
  await api.logout()
  await router.push('/')
}
</script>

<template>
  <section class="auth-card">
    <p class="eyebrow dark">ACCOUNT</p>
    <h1>我的账户</h1>
    <p v-if="profile">登录账号：{{ profile.username }}<span v-if="profile.role === 'admin'"> · 管理员</span></p>
    <form class="form-stack" @submit.prevent="save">
      <label>昵称<input v-model="form.nickname" required maxlength="64" /></label>
      <p v-if="error" class="error-message">{{ error }}</p>
      <p v-if="message" class="success-message">{{ message }}</p>
      <button class="primary-button" type="submit">保存资料</button>
      <button class="secondary-button" type="button" @click="logout">退出登录</button>
    </form>
  </section>
</template>
