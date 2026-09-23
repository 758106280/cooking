<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { api, type Category, type RecipeSummary } from '../api'

const route = useRoute()
const router = useRouter()
const keyword = ref('')
const mealType = ref(typeof route.query.meal_type === 'string' ? route.query.meal_type : '')
const difficulty = ref('')
const maxCookingTime = ref('')
const categoryId = ref('')
const categories = ref<Category[]>([])
const recipes = ref<RecipeSummary[]>([])
const loading = ref(false)
const error = ref('')
const mealTypes = [
  { label: '早餐', value: 'breakfast' },
  { label: '午餐', value: 'lunch' },
  { label: '晚餐', value: 'dinner' },
]
const cuisineCategories = computed(() => categories.value.filter(category => category.type === 'cuisine'))

async function updateMealType() {
  await router.replace({
    query: {
      ...route.query,
      meal_type: mealType.value || undefined,
    },
  })
}

async function loadRecipes() {
  loading.value = true
  error.value = ''
  try {
    recipes.value = (await api.listRecipes({
      keyword: keyword.value,
      meal_type: mealType.value,
      difficulty: difficulty.value,
      max_cooking_time: maxCookingTime.value,
      category_id: categoryId.value,
      page_size: 100,
    })).items
  } catch (err) {
    error.value = err instanceof Error ? err.message : '加载失败'
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  categories.value = await api.getCategories()
  await loadRecipes()
})
watch(() => route.query.meal_type, value => {
  mealType.value = typeof value === 'string' ? value : ''
  loadRecipes()
})
</script>

<template>
  <section class="section-block page-title">
    <p class="eyebrow dark">RECIPES</p>
    <h1>菜谱库</h1>
    <p>按名称、餐次找到今天想做的菜。</p>
  </section>

  <form class="search-bar" @submit.prevent="loadRecipes">
    <input v-model="keyword" placeholder="搜索菜名或食材，例如：番茄、鸡蛋" />
    <select v-model="mealType" aria-label="餐次" @change="updateMealType">
      <option value="">全部餐次</option>
      <option v-for="meal in mealTypes" :key="meal.value" :value="meal.value">{{ meal.label }}</option>
    </select>
    <select v-model="difficulty" @change="loadRecipes">
      <option value="">全部难度</option>
      <option value="easy">简单</option>
      <option value="medium">中等</option>
      <option value="hard">困难</option>
    </select>
    <select v-model="maxCookingTime" @change="loadRecipes">
      <option value="">不限时间</option>
      <option value="15">15 分钟内</option>
      <option value="30">30 分钟内</option>
      <option value="60">60 分钟内</option>
    </select>
    <select v-model="categoryId" @change="loadRecipes">
      <option value="">全部分类</option>
      <option v-for="category in cuisineCategories" :key="category.id" :value="category.id">{{ category.name }}</option>
    </select>
    <button class="primary-button" type="submit">搜索</button>
  </form>

  <p v-if="loading" class="empty-state">正在加载...</p>
  <p v-else-if="error" class="error-message">{{ error }}</p>
  <p v-else-if="recipes.length === 0" class="empty-state">没有找到匹配的菜谱。</p>
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
