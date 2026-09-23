import { clearAuthToken, getApiBaseUrl, getAuthToken, setAuthToken } from './platform'

export interface Category {
  id: number
  name: string
  type: string
  sort_order: number
  is_active: boolean
}

export interface RecipeSummary {
  id: number
  name: string
  description: string | null
  cover_image: string | null
  meal_type: string
  difficulty: string
  cooking_time: number
  servings: number
  status: string
  category: Category | null
  created_at: string
}

export interface RecipeDetail extends RecipeSummary {
  tips: string | null
  nutrition: Record<string, number> | null
  ingredients: {
    id: number
    name: string
    amount: number | null
    unit: string | null
    note: string | null
  }[]
  steps: {
    id: number
    step_no: number
    description: string
    duration_seconds: number | null
    image: string | null
  }[]
  tags: { id: number; name: string; type: string | null }[]
  related_recipes: RecipeSummary[]
}

export interface PageResult<T> {
  items: T[]
  total: number
  page: number
  page_size: number
}

export interface Preferences {
  preferred_cuisines: string[]
  disliked_ingredients: string[]
  allergies: string[]
  cooking_level: string | null
  appliances: string[]
  default_servings: number
}

export interface UserProfile {
  id: number
  username: string
  nickname: string | null
  avatar: string | null
  role: string
}

export interface IngredientCatalog {
  id: number
  name: string
  category: string | null
}

async function resolveApiUrl(url: string) {
  if (/^https?:\/\//i.test(url)) return url
  const apiBaseUrl = await getApiBaseUrl()
  return apiBaseUrl ? `${apiBaseUrl}${url}` : url
}

async function request<T>(url: string, options: RequestInit = {}): Promise<T> {
  const headers = new Headers(options.headers)
  const authToken = await getAuthToken()
  if (!(options.body instanceof FormData)) {
    headers.set('Content-Type', 'application/json')
  }
  if (authToken) headers.set('Authorization', `Bearer ${authToken}`)
  const response = await fetch(await resolveApiUrl(url), {
    ...options,
    credentials: 'include',
    headers,
  })
  const result = await response.json().catch(() => ({})) as { data?: T; message?: string; detail?: string }
  if (!response.ok) {
    if (response.status === 401) await clearAuthToken()
    throw new Error(result.detail ?? result.message ?? '请求失败')
  }
  return (result.data ?? result) as T
}

export const api = {
  listRecipes(params: Record<string, string | number | undefined> = {}) {
    const search = new URLSearchParams()
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== '') search.set(key, String(value))
    })
    return request<{ items: RecipeSummary[]; total: number; page: number; page_size: number }>(
      `/api/recipes?${search.toString()}`,
    )
  },
  getRecipe(id: string | number) {
    return request<RecipeDetail>(`/api/recipes/${id}`)
  },
  getCategories() {
    return request<Category[]>('/api/categories')
  },
  getTags() {
    return request<{ id: number; name: string; type: string | null }[]>('/api/tags')
  },
  login(username: string, password: string) {
    return request<UserProfile & { access_token?: string }>('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    }).then(async user => {
      if (user.access_token) await setAuthToken(user.access_token)
      return user
    })
  },
  register(username: string, password: string, nickname: string) {
    return request<UserProfile & { access_token?: string }>('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify({ username, password, nickname }),
    }).then(async user => {
      if (user.access_token) await setAuthToken(user.access_token)
      return user
    })
  },
  logout() {
    return request('/api/auth/logout', { method: 'POST' }).finally(clearAuthToken)
  },
  me() {
    return request<UserProfile>('/api/auth/me')
  },
  updateProfile(payload: { nickname?: string; avatar?: string }) {
    return request<UserProfile>('/api/auth/profile', {
      method: 'PUT',
      body: JSON.stringify(payload),
    })
  },
  listFavorites() {
    return request<{ items: RecipeSummary[]; total: number; page: number; page_size: number }>('/api/favorites')
  },
  favoriteStatus(id: number) {
    return request<{ is_favorite: boolean }>(`/api/favorites/${id}/status`)
  },
  addFavorite(id: number) {
    return request(`/api/favorites/${id}`, { method: 'POST' })
  },
  removeFavorite(id: number) {
    return request(`/api/favorites/${id}`, { method: 'DELETE' })
  },
  getPreferences() {
    return request<Preferences>('/api/preferences')
  },
  updatePreferences(payload: Partial<Preferences>) {
    return request<Preferences>('/api/preferences', {
      method: 'PATCH',
      body: JSON.stringify(payload),
    })
  },
  adminListRecipes() {
    return request<{ items: RecipeSummary[]; total: number; page: number; page_size: number }>('/api/admin/recipes')
  },
  adminGetRecipe(id: number) {
    return request<RecipeDetail>(`/api/admin/recipes/${id}`)
  },
  createRecipe(payload: object) {
    return request<RecipeDetail>('/api/admin/recipes', {
      method: 'POST',
      body: JSON.stringify(payload),
    })
  },
  updateRecipe(id: number, payload: object) {
    return request<RecipeDetail>(`/api/admin/recipes/${id}`, {
      method: 'PUT',
      body: JSON.stringify(payload),
    })
  },
  publishRecipe(id: number) {
    return request(`/api/admin/recipes/${id}/publish`, { method: 'POST' })
  },
  archiveRecipe(id: number) {
    return request(`/api/admin/recipes/${id}/archive`, { method: 'POST' })
  },
  adminCategories() {
    return request<Category[]>('/api/admin/categories')
  },
  createCategory(payload: { name: string; type: string; sort_order: number }) {
    return request<Category>('/api/admin/categories', { method: 'POST', body: JSON.stringify(payload) })
  },
  deleteCategory(id: number) {
    return request(`/api/admin/categories/${id}`, { method: 'DELETE' })
  },
  updateCategory(id: number, payload: { name: string; type: string; sort_order: number; is_active: boolean }) {
    return request<Category>(`/api/admin/categories/${id}`, { method: 'PUT', body: JSON.stringify(payload) })
  },
  adminTags() {
    return request<{ id: number; name: string; type: string | null }[]>('/api/admin/tags')
  },
  createTag(payload: { name: string; type: string; sort_order: number }) {
    return request<{ id: number; name: string; type: string | null }>('/api/admin/tags', { method: 'POST', body: JSON.stringify(payload) })
  },
  deleteTag(id: number) {
    return request(`/api/admin/tags/${id}`, { method: 'DELETE' })
  },
  updateTag(id: number, payload: { name: string; type: string; sort_order: number; is_active: boolean }) {
    return request<{ id: number; name: string; type: string | null }>(`/api/admin/tags/${id}`, { method: 'PUT', body: JSON.stringify(payload) })
  },
  adminIngredients() {
    return request<IngredientCatalog[]>('/api/admin/ingredients')
  },
  createIngredient(payload: { name: string; type: string; sort_order: number }) {
    return request<IngredientCatalog>('/api/admin/ingredients', { method: 'POST', body: JSON.stringify(payload) })
  },
  deleteIngredient(id: number) {
    return request(`/api/admin/ingredients/${id}`, { method: 'DELETE' })
  },
  updateIngredient(id: number, payload: { name: string; type: string; sort_order: number; is_active: boolean }) {
    return request<IngredientCatalog>(`/api/admin/ingredients/${id}`, { method: 'PUT', body: JSON.stringify(payload) })
  },
  uploadImage(file: File, kind: 'recipe_cover' | 'recipe_step' = 'recipe_cover') {
    const form = new FormData()
    form.append('file', file)
    form.append('kind', kind)
    return request<{ path: string; url: string }>('/api/admin/uploads', {
      method: 'POST',
      body: form,
      headers: {},
    })
  },
  deleteRecipe(id: number) {
    return request(`/api/admin/recipes/${id}`, { method: 'DELETE' })
  },
}
