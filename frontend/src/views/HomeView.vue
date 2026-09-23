<script setup lang="ts">
import { onMounted, ref } from 'vue'

import { api, type RecipeDetail, type RecipeSummary } from '../api'

const recipes = ref<RecipeSummary[]>([])
const recentRecipes = ref<RecipeSummary[]>([])
const loading = ref(true)

onMounted(async () => {
  try {
    const result = await api.listRecipes({ page_size: 6 })
    recipes.value = result.items
    const ids = JSON.parse(localStorage.getItem('cooking_recent_recipes') || '[]') as number[]
    const details = await Promise.all(ids.slice(0, 4).map(id => api.getRecipe(id).catch(() => null)))
    recentRecipes.value = details.filter((item): item is RecipeDetail => item !== null)
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <section class="hero-card">
    <p class="eyebrow">COOKING ASSISTANT</p>
    <h1>今天吃什么？</h1>
    <p class="intro">按三餐找到适合你的家常菜，打开菜谱就能照着做。</p>
    <RouterLink class="primary-button" to="/recipes">浏览全部菜谱</RouterLink>
  </section>

  <section class="section-block">
    <div class="section-heading">
      <div>
        <p class="eyebrow dark">MEALS</p>
        <h2>从一餐开始</h2>
      </div>
    </div>
    <div class="meal-grid">
      <RouterLink v-for="meal in [{ name: '早餐', value: 'breakfast', icon: '☀️' }, { name: '午餐', value: 'lunch', icon: '🍱' }, { name: '晚餐', value: 'dinner', icon: '🌙' }]" :key="meal.value" class="meal-card" :to="`/recipes?meal_type=${meal.value}`">
        <span class="meal-icon">{{ meal.icon }}</span>
        <h3>{{ meal.name }}</h3>
        <p>查看{{ meal.name }}推荐</p>
      </RouterLink>
    </div>
  </section>

  <section class="section-block">
    <div class="section-heading">
      <div>
        <p class="eyebrow dark">RECIPES</p>
        <h2>最新菜谱</h2>
      </div>
      <RouterLink class="text-link" to="/recipes">查看全部 →</RouterLink>
    </div>
    <p v-if="loading" class="empty-state">正在加载菜谱...</p>
    <p v-else-if="recipes.length === 0" class="empty-state">还没有已发布菜谱，请先在管理端录入。</p>
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
  </section>

  <section v-if="recentRecipes.length" class="section-block">
    <div class="section-heading"><div><p class="eyebrow dark">RECENT</p><h2>最近浏览</h2></div></div>
    <div class="recipe-grid">
      <RouterLink v-for="recipe in recentRecipes" :key="recipe.id" class="recipe-card" :to="`/recipes/${recipe.id}`">
        <div class="recipe-cover"><img v-if="recipe.cover_image" :src="recipe.cover_image" :alt="recipe.name" /><span v-else>🍳</span></div>
        <div class="recipe-card-body"><h3>{{ recipe.name }}</h3><p>{{ recipe.description || '一道家常菜' }}</p><small>{{ recipe.cooking_time }} 分钟</small></div>
      </RouterLink>
    </div>
  </section>
</template>
