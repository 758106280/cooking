<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { RouterLink, RouterView } from 'vue-router'

import {
  getApiBaseUrl,
  isNativePlatform,
  normalizeApiBaseUrl,
  setApiBaseUrl,
} from './platform'

const checkingConfig = ref(true)
const showServerConfig = ref(false)
const serverAddress = ref('')
const savedServerAddress = ref('')
const configError = ref('')

onMounted(async () => {
  savedServerAddress.value = await getApiBaseUrl()
  serverAddress.value = savedServerAddress.value
  showServerConfig.value = isNativePlatform && !savedServerAddress.value
  checkingConfig.value = false
})

function openServerConfig() {
  configError.value = ''
  serverAddress.value = savedServerAddress.value
  showServerConfig.value = true
}

async function saveServerConfig() {
  configError.value = ''
  try {
    const normalized = normalizeApiBaseUrl(serverAddress.value)
    if (!normalized) throw new Error('服务地址不能为空')
    savedServerAddress.value = await setApiBaseUrl(normalized)
    serverAddress.value = savedServerAddress.value
    showServerConfig.value = false
    window.location.reload()
  } catch (err) {
    configError.value = err instanceof Error ? err.message : '服务地址保存失败'
  }
}
</script>

<template>
  <div class="app-shell">
    <section v-if="checkingConfig" class="server-config-page">
      <p class="empty-state">正在准备应用...</p>
    </section>
    <section v-else-if="showServerConfig" class="server-config-page">
      <div class="auth-card server-config-card">
        <p class="eyebrow dark">DEVICE SETUP</p>
        <h1>配置服务地址</h1>
        <p class="config-intro">请输入做饭助手后端服务地址。家庭局域网示例：<code>http://192.168.1.100:8000</code></p>
        <form class="form-stack" @submit.prevent="saveServerConfig">
          <label>服务地址<input v-model="serverAddress" type="url" inputmode="url" autocomplete="url" placeholder="http://192.168.1.100:8000" required /></label>
          <p v-if="configError" class="error-message">{{ configError }}</p>
          <button class="primary-button" type="submit">保存并开始使用</button>
        </form>
        <p class="config-hint">手机和服务端需要连接同一个家庭网络。服务端地址变更后，可在顶部“服务地址”中重新修改。</p>
      </div>
    </section>
    <template v-else>
      <header class="topbar">
        <RouterLink class="brand" to="/">🍳 做饭助手</RouterLink>
        <div class="topbar-actions">
          <nav class="nav-links">
            <RouterLink to="/recipes">菜谱库</RouterLink>
            <RouterLink to="/favorites">收藏</RouterLink>
            <RouterLink to="/preferences">偏好</RouterLink>
            <RouterLink to="/account">账户</RouterLink>
            <RouterLink to="/admin/recipes">管理端</RouterLink>
            <RouterLink to="/admin/catalog">基础数据</RouterLink>
          </nav>
          <button v-if="isNativePlatform" class="server-config-trigger" type="button" @click="openServerConfig">服务地址</button>
        </div>
      </header>
      <main class="page-shell">
        <RouterView />
      </main>
      <nav class="mobile-tabbar" aria-label="移动端主导航">
        <RouterLink to="/">
          <span aria-hidden="true">⌂</span>
          <small>首页</small>
        </RouterLink>
        <RouterLink to="/recipes">
          <span aria-hidden="true">▤</span>
          <small>菜谱</small>
        </RouterLink>
        <RouterLink to="/favorites">
          <span aria-hidden="true">♡</span>
          <small>收藏</small>
        </RouterLink>
        <RouterLink to="/account">
          <span aria-hidden="true">◯</span>
          <small>我的</small>
        </RouterLink>
      </nav>
    </template>
  </div>
</template>
