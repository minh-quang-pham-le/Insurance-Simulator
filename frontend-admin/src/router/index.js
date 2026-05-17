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
    component: () => import('../views/ProductsView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/products/new',
    name: 'admin-product-new',
    component: () => import('../views/ProductFormView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/products/edit/:id',
    name: 'admin-product-edit',
    component: () => import('../views/ProductFormView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/users',
    name: 'admin-users',
    component: () => import('../views/UsersView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/admin-policies',
    name: 'admin-policies',
    component: () => import('../views/PoliciesView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/claims',
    name: 'admin-claims',
    component: () => import('../views/ClaimsView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/kyc-review',
    name: 'admin-kyc-review',
    component: () => import('../views/KycReviewView.vue'),
    meta: { requiresAuth: true }
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
