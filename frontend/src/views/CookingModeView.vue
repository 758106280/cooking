<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { api, type RecipeDetail } from '../api'

const route = useRoute()
const router = useRouter()
const recipe = ref<RecipeDetail | null>(null)
const currentStep = ref(0)
const secondsLeft = ref(0)
let timer: number | undefined

function startTimer(seconds: number | null) {
  if (!seconds) return
  secondsLeft.value = seconds
  window.clearInterval(timer)
  timer = window.setInterval(() => {
    if (secondsLeft.value <= 1) {
      secondsLeft.value = 0
      window.clearInterval(timer)
      timer = undefined
    } else {
      secondsLeft.value -= 1
    }
  }, 1000)
}

onMounted(async () => {
  recipe.value = await api.getRecipe(route.params.id as string)
  const duration = recipe.value.steps[0]?.duration_seconds
  if (duration) startTimer(duration)
})

onUnmounted(() => window.clearInterval(timer))
</script>

<template>
  <section v-if="recipe" class="cook-mode">
    <button class="text-button" @click="router.back()">← 返回菜谱</button>
    <p class="eyebrow dark">COOKING MODE</p>
    <h1>{{ recipe.name }}</h1>
    <div class="cook-progress">步骤 {{ currentStep + 1 }} / {{ recipe.steps.length }}</div>
    <article v-if="recipe.steps[currentStep]" class="current-step">
      <span class="step-number">{{ recipe.steps[currentStep].step_no }}</span>
      <p>{{ recipe.steps[currentStep].description }}</p>
      <div v-if="secondsLeft" class="timer">{{ Math.floor(secondsLeft / 60).toString().padStart(2, '0') }}:{{ (secondsLeft % 60).toString().padStart(2, '0') }}</div>
      <button v-if="recipe.steps[currentStep].duration_seconds && !secondsLeft" class="text-button" @click="startTimer(recipe.steps[currentStep].duration_seconds)">重新计时</button>
    </article>
    <div class="cook-actions">
      <button class="secondary-button" :disabled="currentStep === 0" @click="currentStep--">上一步</button>
      <button v-if="currentStep < recipe.steps.length - 1" class="primary-button" @click="currentStep++">完成，下一步</button>
      <button v-else class="primary-button" @click="router.push(`/recipes/${recipe.id}`)">完成烹饪</button>
    </div>
  </section>
</template>
