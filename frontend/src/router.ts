import { createRouter, createWebHistory } from 'vue-router'

import AdminLoginView from './views/AdminLoginView.vue'
import AdminRecipesView from './views/AdminRecipesView.vue'
import AdminCatalogView from './views/AdminCatalogView.vue'
import CookingModeView from './views/CookingModeView.vue'
import FavoritesView from './views/FavoritesView.vue'
import HomeView from './views/HomeView.vue'
import PreferencesView from './views/PreferencesView.vue'
import AccountView from './views/AccountView.vue'
import RecipeDetailView from './views/RecipeDetailView.vue'
import RecipeListView from './views/RecipeListView.vue'

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: HomeView },
    { path: '/recipes', component: RecipeListView },
    { path: '/recipes/:id', component: RecipeDetailView },
    { path: '/recipes/:id/cook', component: CookingModeView },
    { path: '/favorites', component: FavoritesView },
    { path: '/preferences', component: PreferencesView },
    { path: '/account', component: AccountView },
    { path: '/admin/login', component: AdminLoginView },
    { path: '/login', redirect: '/admin/login' },
    { path: '/admin/recipes', component: AdminRecipesView },
    { path: '/admin/catalog', component: AdminCatalogView },
  ],
  scrollBehavior: () => ({ top: 0 }),
})
