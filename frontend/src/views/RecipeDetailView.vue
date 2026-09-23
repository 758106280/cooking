<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { api, type RecipeDetail } from '../api'

const route = useRoute()
const router = useRouter()
const recipe = ref<RecipeDetail | null>(null)
const error = ref('')
const isFavorite = ref(false)
const favoriteError = ref('')
const servings = ref(2)

const servingLabel = computed(() => `${servings.value} 人份`)

onMounted(async () => {
  try {
    recipe.value = await api.getRecipe(route.params.id as string)
    servings.value = recipe.value.servings
    const recent = JSON.parse(localStorage.getItem('cooking_recent_recipes') || '[]') as number[]
    localStorage.setItem('cooking_recent_recipes', JSON.stringify([recipe.value.id, ...recent.filter(id => id !== recipe.value?.id)].slice(0, 8)))
    try {
      isFavorite.value = (await api.favoriteStatus(Number(route.params.id))).is_favorite
    } catch {
      isFavorite.value = false
    }
  } catch (err) {
    error.value = err instanceof Error ? err.message : '菜谱加载失败'
  }
})

async function toggleFavorite() {
  favoriteError.value = ''
  try {
    if (isFavorite.value) {
      await api.removeFavorite(Number(route.params.id))
      isFavorite.value = false
    } else {
      await api.addFavorite(Number(route.params.id))
      isFavorite.value = true
    }
  } catch (err) {
    favoriteError.value = err instanceof Error ? err.message : '请先登录后收藏'
  }
}

async function shareRecipe() {
  if (!recipe.value) return
  const shareData = { title: recipe.value.name, text: recipe.value.description || '做饭助手菜谱', url: window.location.href }
  if (navigator.share) await navigator.share(shareData)
  else await navigator.clipboard.writeText(window.location.href)
}

function scaledAmount(amount: number | null) {
  if (amount === null || !recipe.value) return ''
  const value = amount * servings.value / recipe.value.servings
  return Number.isInteger(value) ? value : value.toFixed(1)
}
</script>

<template>
  <p v-if="error" class="error-message">{{ error }}</p>
  <section v-else-if="recipe" class="detail-page">
    <div class="detail-cover"><img v-if="recipe.cover_image" :src="recipe.cover_image" :alt="recipe.name" /><span v-else>🍳</span></div>
    <div class="detail-content">
      <p class="eyebrow dark">{{ recipe.meal_type }}</p>
      <h1>{{ recipe.name }}</h1>
      <p class="detail-description">{{ recipe.description }}</p>
      <div class="meta-row">
        <span>{{ recipe.cooking_time }} 分钟</span>
        <span>{{ recipe.difficulty }}</span>
        <span class="serving-control"><button type="button" @click="servings = Math.max(1, servings - 1)">−</button>{{ servingLabel }}<button type="button" @click="servings++">＋</button></span>
      </div>
      <div class="detail-actions">
        <button class="secondary-button" @click="toggleFavorite">{{ isFavorite ? '★ 已收藏' : '☆ 收藏菜谱' }}</button>
        <button class="secondary-button" @click="shareRecipe">分享</button>
        <button class="primary-button" @click="router.push(`/recipes/${recipe.id}/cook`)">开始烹饪</button>
      </div>
      <p v-if="favoriteError" class="error-message">{{ favoriteError }}</p>

      <div class="detail-section">
        <h2>食材</h2>
        <ul class="ingredient-list">
          <li v-for="ingredient in recipe.ingredients" :key="ingredient.id">
            <span>{{ ingredient.name }}{{ ingredient.note ? `（${ingredient.note}）` : '' }}</span>
            <strong>{{ scaledAmount(ingredient.amount) }} {{ ingredient.unit ?? '' }}</strong>
          </li>
        </ul>
      </div>

      <div class="detail-section">
        <h2>制作步骤</h2>
        <ol class="step-list">
          <li v-for="step in recipe.steps" :key="step.id">
            <span class="step-number">{{ step.step_no }}</span>
            <div>{{ step.description }}</div>
          </li>
        </ol>
      </div>

      <div v-if="recipe.tips" class="tip-box"><strong>小贴士：</strong>{{ recipe.tips }}</div>
      <div v-if="recipe.nutrition" class="nutrition-box">
        <h2>营养信息</h2>
        <div class="nutrition-grid"><span v-for="(value, key) in recipe.nutrition" :key="key"><strong>{{ key }}</strong>{{ value }}</span></div>
      </div>
    </div>
  </section>
  <section v-if="recipe?.related_recipes.length" class="section-block">
    <div class="section-heading"><h2>你可能还喜欢</h2></div>
    <div class="recipe-grid">
      <RouterLink v-for="item in recipe.related_recipes" :key="item.id" class="recipe-card" :to="`/recipes/${item.id}`">
        <div class="recipe-cover"><img v-if="item.cover_image" :src="item.cover_image" :alt="item.name" /><span v-else>🍳</span></div>
        <div class="recipe-card-body"><h3>{{ item.name }}</h3><p>{{ item.description || '一道家常菜' }}</p><small>{{ item.cooking_time }} 分钟</small></div>
      </RouterLink>
    </div>
  </section>
</template>
