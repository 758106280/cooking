<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

import { api, type Category, type IngredientCatalog } from '../api'

const router = useRouter()
const categories = ref<Category[]>([])
const tags = ref<{ id: number; name: string; type: string | null }[]>([])
const ingredients = ref<IngredientCatalog[]>([])
const error = ref('')
const categoryForm = reactive({ name: '', type: 'cuisine' })
const tagForm = reactive({ name: '', type: 'feature' })
const ingredientForm = reactive({ name: '', type: 'general' })

async function load() {
  try {
    const result = await Promise.all([api.adminCategories(), api.adminTags(), api.adminIngredients()])
    categories.value = result[0]
    tags.value = result[1]
    ingredients.value = result[2]
  } catch {
    await router.push('/admin/login')
  }
}

async function addCategory() {
  await api.createCategory({ ...categoryForm, sort_order: categories.value.length })
  categoryForm.name = ''
  await load()
}

async function addTag() {
  await api.createTag({ ...tagForm, sort_order: 0 })
  tagForm.name = ''
  await load()
}

async function addIngredient() {
  await api.createIngredient({ ...ingredientForm, sort_order: 0 })
  ingredientForm.name = ''
  await load()
}

async function removeCategory(id: number) { await api.deleteCategory(id); await load() }
async function removeTag(id: number) { await api.deleteTag(id); await load() }
async function removeIngredient(id: number) { await api.deleteIngredient(id); await load() }
async function editIngredient(item: IngredientCatalog) {
  const name = window.prompt('修改食材名称', item.name)
  if (!name?.trim()) return
  const category = window.prompt('修改食材分类', item.category || 'general') || 'general'
  await api.updateIngredient(item.id, { name: name.trim(), type: category, sort_order: 0, is_active: true })
  await load()
}
async function editCategory(item: Category) {
  const name = window.prompt('修改分类名称', item.name)
  if (!name?.trim()) return
  await api.updateCategory(item.id, { name: name.trim(), type: item.type, sort_order: item.sort_order, is_active: item.is_active })
  await load()
}
async function editTag(item: { id: number; name: string; type: string | null }) {
  const name = window.prompt('修改标签名称', item.name)
  if (!name?.trim()) return
  await api.updateTag(item.id, { name: name.trim(), type: item.type || 'feature', sort_order: 0, is_active: true })
  await load()
}

onMounted(load)
</script>

<template>
  <section class="page-title">
    <p class="eyebrow dark">ADMIN</p>
    <h1>基础数据</h1>
    <p>管理菜谱分类、标签和常用食材。</p>
  </section>
  <p v-if="error" class="error-message">{{ error }}</p>
  <div class="catalog-grid">
    <section class="panel">
      <h2>分类</h2>
      <form class="inline-form" @submit.prevent="addCategory"><input v-model="categoryForm.name" required placeholder="分类名称" /><select v-model="categoryForm.type"><option value="meal">餐次</option><option value="cuisine">菜系</option><option value="general">其他</option></select><button class="primary-button">添加</button></form>
      <ul class="admin-list"><li v-for="item in categories" :key="item.id"><span>{{ item.name }} <small>{{ item.type }}</small></span><span class="admin-actions"><button class="text-button" @click="editCategory(item)">编辑</button><button class="danger-button" @click="removeCategory(item.id)">停用</button></span></li></ul>
    </section>
    <section class="panel">
      <h2>标签</h2>
      <form class="inline-form" @submit.prevent="addTag"><input v-model="tagForm.name" required placeholder="标签名称" /><select v-model="tagForm.type"><option value="feature">特点</option><option value="difficulty">难度</option></select><button class="primary-button">添加</button></form>
      <ul class="admin-list"><li v-for="item in tags" :key="item.id"><span>{{ item.name }} <small>{{ item.type }}</small></span><span class="admin-actions"><button class="text-button" @click="editTag(item)">编辑</button><button class="danger-button" @click="removeTag(item.id)">删除</button></span></li></ul>
    </section>
    <section class="panel">
      <h2>食材</h2>
      <form class="inline-form" @submit.prevent="addIngredient"><input v-model="ingredientForm.name" required placeholder="食材名称" /><input v-model="ingredientForm.type" placeholder="分类" /><button class="primary-button">添加</button></form>
      <ul class="admin-list"><li v-for="item in ingredients" :key="item.id"><span>{{ item.name }} <small>{{ item.category || '未分类' }}</small></span><span class="admin-actions"><button class="text-button" @click="editIngredient(item)">编辑</button><button class="danger-button" @click="removeIngredient(item.id)">删除</button></span></li></ul>
    </section>
  </div>
</template>
