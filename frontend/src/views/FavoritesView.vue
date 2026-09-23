<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import { api, type RecipeSummary } from '../api'

const router = useRouter()
const recipes = ref<RecipeSummary[]>([])
const error = ref('')

onMounted(async () => {
  try {
    recipes.value = (await api.listFavorites()).items
  } catch (err) {
    if (err instanceof Error) error.value = err.message
    if (error.value.includes('登录')) await router.push('/admin/login')
  }
})
</script>

<template>
  <section class="page-title">
    <p class="eyebrow dark">FAVORITES</p>
    <h1>我的收藏</h1>
    <p>把想做的菜留在这里。</p>
  </section>
  <p v-if="error" class="error-message">{{ error }}</p>
  <p v-else-if="recipes.length === 0" class="empty-state">还没有收藏菜谱。</p>
  <div v-else class="recipe-grid">
    <RouterLink v-for="recipe in recipes" :key="recipe.id" class="recipe-card" :to="`/recipes/${recipe.id}`">
      <div class="recipe-cover"><img v-if="recipe.cover_image" :src="recipe.cover_image" :alt="recipe.name" /><span v-else>🍳</span></div>
      <div class="recipe-card-body">
        <h3>{{ recipe.name }}</h3>
        <p>{{ recipe.description || '一道简单的家常菜' }}</p>
        <small>{{ recipe.cooking_time }} 分钟 · {{ recipe.difficulty }}</small>
      </div>
    </RouterLink>
  </div>
</template>
