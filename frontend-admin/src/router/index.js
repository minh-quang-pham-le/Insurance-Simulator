import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

import LoginView from '../views/LoginView.vue'
import DashboardView from '../views/DashboardView.vue'

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', component: LoginView, meta: { layout: 'blank' } },
  {
    path: '/dashboard',
    component: DashboardView,
    meta: { requiresAuth: true }
  },
  {
  path: '/products',
  name: 'admin-products',
  component: () => import('../views/ProductsView.vue')
  },
  {
  path: '/products/new',
  name: 'admin-product-new',
  component: () => import('../views/ProductFormView.vue')
  },
  {
  path: '/products/edit/:id',
  name: 'admin-product-edit',
  component: () => import('../views/ProductFormView.vue')
  },
  ]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Route guard for authentication
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else if (to.path === '/login' && authStore.isAuthenticated) {
    next('/dashboard')
  } else {
    next()
  }
})

export default router
