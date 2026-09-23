<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

import { api, type Category, type RecipeSummary } from '../api'

const router = useRouter()
const recipes = ref<RecipeSummary[]>([])
const categories = ref<Category[]>([])
const tags = ref<{ id: number; name: string; type: string | null }[]>([])
const error = ref('')
const message = ref('')
const editingId = ref<number | null>(null)
const ingredientText = ref('')
const stepText = ref('')
const nutritionText = ref('')
const form = reactive({
  name: '',
  description: '',
  cover_image: null as string | null,
  meal_type: 'dinner',
  category_id: null as number | null,
  difficulty: 'easy',
  cooking_time: 20,
  servings: 2,
  tips: '',
  status: 'published',
  tag_ids: [] as number[],
})

async function load() {
  try {
    const [recipeResult, categoryResult, tagResult] = await Promise.all([
      api.adminListRecipes(),
      api.adminCategories(),
      api.adminTags(),
    ])
    recipes.value = recipeResult.items
    categories.value = categoryResult
    tags.value = tagResult
  } catch {
    await router.push('/admin/login')
  }
}

function resetForm() {
  editingId.value = null
  Object.assign(form, {
    name: '', description: '', cover_image: null, meal_type: 'dinner', category_id: null,
    difficulty: 'easy', cooking_time: 20, servings: 2, tips: '', status: 'published', tag_ids: [],
  })
  ingredientText.value = ''
  stepText.value = ''
  nutritionText.value = ''
}

function parseIngredients() {
  return ingredientText.value.split('\n').map(line => line.trim()).filter(Boolean).map(line => {
    const [name, amount, unit, note] = line.split('|').map(item => item.trim())
    return { name, amount: amount ? Number(amount) : null, unit: unit || null, note: note || null }
  })
}

function parseSteps() {
  return stepText.value.split('\n').map(line => line.trim()).filter(Boolean).map((line, index) => {
    const [description, duration] = line.split('|').map(item => item.trim())
    return {
    step_no: index + 1,
    description,
    duration_seconds: duration ? Number(duration) : null,
    }
  })
}

function toPayload() {
  const nutrition = Object.fromEntries(
    nutritionText.value.split(',').map(item => item.trim()).filter(Boolean).map(item => {
      const [key, value] = item.split('=').map(part => part.trim())
      return [key, Number(value)]
    }).filter(([, value]) => Number.isFinite(value)),
  )
  return {
    ...form,
    nutrition: Object.keys(nutrition).length ? nutrition : null,
    ingredients: parseIngredients(),
    steps: parseSteps(),
  }
}

async function save() {
  error.value = ''
  message.value = ''
  try {
    if (editingId.value) {
      await api.updateRecipe(editingId.value, toPayload())
      message.value = '菜谱更新成功'
    } else {
      await api.createRecipe(toPayload())
      message.value = '菜谱创建成功'
    }
    resetForm()
    await load()
  } catch (err) {
    error.value = err instanceof Error ? err.message : '保存失败'
  }
}

async function edit(id: number) {
  error.value = ''
  const recipe = await api.adminGetRecipe(id)
  editingId.value = id
  Object.assign(form, {
    name: recipe.name,
    description: recipe.description || '',
    cover_image: recipe.cover_image,
    meal_type: recipe.meal_type,
    category_id: recipe.category?.id || null,
    difficulty: recipe.difficulty,
    cooking_time: recipe.cooking_time,
    servings: recipe.servings,
    tips: recipe.tips || '',
    status: recipe.status,
    tag_ids: recipe.tags.map(tag => tag.id),
  })
  ingredientText.value = recipe.ingredients.map(item => [item.name, item.amount ?? '', item.unit ?? '', item.note ?? ''].join('|')).join('\n')
  stepText.value = recipe.steps.map(step => [step.description, step.duration_seconds || ''].join('|')).join('\n')
  nutritionText.value = recipe.nutrition ? Object.entries(recipe.nutrition).map(([key, value]) => `${key}=${value}`).join(',') : ''
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

async function uploadCover(event: Event) {
  const file = (event.target as HTMLInputElement).files?.[0]
  if (!file) return
  try {
    form.cover_image = (await api.uploadImage(file)).path
  } catch (err) {
    error.value = err instanceof Error ? err.message : '图片上传失败'
  }
}

async function remove(id: number) {
  if (!window.confirm('确定删除这道菜谱吗？')) return
  await api.deleteRecipe(id)
  await load()
}

async function changeStatus(recipe: RecipeSummary) {
  if (recipe.status === 'published') await api.archiveRecipe(recipe.id)
  else await api.publishRecipe(recipe.id)
  await load()
}

onMounted(load)
</script>

<template>
  <section class="page-title">
    <p class="eyebrow dark">ADMIN</p>
    <h1>菜谱管理</h1>
    <p>录入、编辑和发布家庭菜谱。</p>
  </section>

  <div class="admin-layout">
    <form class="panel form-stack" @submit.prevent="save">
      <div class="section-heading"><h2>{{ editingId ? '编辑菜谱' : '新增菜谱' }}</h2><button v-if="editingId" class="text-button" type="button" @click="resetForm">取消编辑</button></div>
      <label>菜名<input v-model="form.name" required placeholder="例如：番茄炒蛋" /></label>
      <label>简介<textarea v-model="form.description" rows="2" /></label>
      <label>封面图片<input type="file" accept="image/jpeg,image/png,image/webp" @change="uploadCover" /><small v-if="form.cover_image">已上传：{{ form.cover_image }}</small></label>
      <div class="form-row">
        <label>餐次<select v-model="form.meal_type"><option value="breakfast">早餐</option><option value="lunch">午餐</option><option value="dinner">晚餐</option></select></label>
        <label>难度<select v-model="form.difficulty"><option value="easy">简单</option><option value="medium">中等</option><option value="hard">困难</option></select></label>
      </div>
      <div class="form-row">
        <label>分类<select v-model.number="form.category_id"><option :value="null">未分类</option><option v-for="category in categories" :key="category.id" :value="category.id">{{ category.name }}</option></select></label>
        <label>状态<select v-model="form.status"><option value="draft">草稿</option><option value="published">已发布</option><option value="archived">已下架</option></select></label>
      </div>
      <div class="form-row">
        <label>时间（分钟）<input v-model.number="form.cooking_time" type="number" min="0" /></label>
        <label>份数<input v-model.number="form.servings" type="number" min="1" /></label>
      </div>
      <fieldset class="tag-field"><legend>标签</legend><label v-for="tag in tags" :key="tag.id" class="checkbox-label"><input v-model="form.tag_ids" type="checkbox" :value="tag.id" />{{ tag.name }}</label></fieldset>
      <label>食材（每行：名称|数量|单位|备注）<textarea v-model="ingredientText" rows="4" placeholder="番茄|2|个|切块&#10;鸡蛋|3|个|打散" /></label>
      <label>步骤（每行：描述|计时秒数）<textarea v-model="stepText" rows="5" placeholder="番茄切块，鸡蛋打散。|30&#10;鸡蛋炒熟后盛出。" /></label>
      <label>小贴士<textarea v-model="form.tips" rows="2" /></label>
      <label>营养信息（可选，格式：calories=450,protein=20,carbs=50,fat=15）<input v-model="nutritionText" placeholder="calories=450,protein=20" /></label>
      <p v-if="error" class="error-message">{{ error }}</p>
      <p v-if="message" class="success-message">{{ message }}</p>
      <button class="primary-button" type="submit">{{ editingId ? '保存修改' : '创建菜谱' }}</button>
    </form>

    <section class="panel">
      <div class="section-heading"><h2>已有菜谱</h2><button class="text-button" @click="load">刷新</button></div>
      <p v-if="recipes.length === 0" class="empty-state">暂无菜谱。</p>
      <ul v-else class="admin-list">
        <li v-for="recipe in recipes" :key="recipe.id">
          <div><strong>{{ recipe.name }}</strong><small>{{ recipe.status }} · {{ recipe.meal_type }}</small></div>
          <div class="admin-actions"><button class="text-button" @click="edit(recipe.id)">编辑</button><button class="text-button" @click="changeStatus(recipe)">{{ recipe.status === 'published' ? '下架' : '发布' }}</button><button class="danger-button" @click="remove(recipe.id)">删除</button></div>
        </li>
      </ul>
    </section>
  </div>
</template>
