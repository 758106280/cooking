<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

import { api } from '../api'

const router = useRouter()
const message = ref('')
const error = ref('')
const form = reactive({
  preferred_cuisines: '',
  disliked_ingredients: '',
  allergies: '',
  cooking_level: 'easy',
  appliances: '',
  default_servings: 2,
})

onMounted(async () => {
  try {
    const preferences = await api.getPreferences()
    form.preferred_cuisines = preferences.preferred_cuisines.join('、')
    form.disliked_ingredients = preferences.disliked_ingredients.join('、')
    form.allergies = preferences.allergies.join('、')
    form.cooking_level = preferences.cooking_level || 'easy'
    form.appliances = preferences.appliances.join('、')
    form.default_servings = preferences.default_servings
  } catch (err) {
    error.value = err instanceof Error ? err.message : '请先登录'
    if (error.value.includes('登录')) await router.push('/admin/login')
  }
})

function split(value: string) {
  return value.split(/[、,，\n]/).map(item => item.trim()).filter(Boolean)
}

async function save() {
  error.value = ''
  message.value = ''
  try {
    await api.updatePreferences({
      preferred_cuisines: split(form.preferred_cuisines),
      disliked_ingredients: split(form.disliked_ingredients),
      allergies: split(form.allergies),
      cooking_level: form.cooking_level,
      appliances: split(form.appliances),
      default_servings: form.default_servings,
    })
    message.value = '偏好已保存'
  } catch (err) {
    error.value = err instanceof Error ? err.message : '保存失败'
  }
}
</script>

<template>
  <section class="auth-card preference-card">
    <p class="eyebrow dark">PREFERENCES</p>
    <h1>饮食偏好</h1>
    <form class="form-stack" @submit.prevent="save">
      <label>喜欢的菜系<input v-model="form.preferred_cuisines" placeholder="家常菜、川菜" /></label>
      <label>不喜欢的食材<input v-model="form.disliked_ingredients" placeholder="香菜、芹菜" /></label>
      <label>过敏食材<input v-model="form.allergies" placeholder="花生、虾" /></label>
      <label>烹饪水平<select v-model="form.cooking_level"><option value="easy">新手</option><option value="medium">熟悉家常菜</option><option value="hard">熟练</option></select></label>
      <label>常用厨具<input v-model="form.appliances" placeholder="炒锅、电饭煲、空气炸锅" /></label>
      <label>默认用餐人数<input v-model.number="form.default_servings" type="number" min="1" /></label>
      <p v-if="error" class="error-message">{{ error }}</p>
      <p v-if="message" class="success-message">{{ message }}</p>
      <button class="primary-button" type="submit">保存偏好</button>
    </form>
  </section>
</template>
