import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import DashboardView from '../views/DashboardView.vue'
import KycView from '../views/KycView.vue'
import WalletView from '../views/WalletView.vue'

const routes = [
  { path: '/', component: HomeView },
  { path: '/login', component: LoginView, meta: { layout: 'blank' } },
  { path: '/register', component: RegisterView, meta: { layout: 'blank' } },
  {
    path: '/dashboard',
    component: DashboardView,
    meta: { requiresAuth: true }
  },
  {
    path: '/kyc',
    component: KycView,
    meta: { requiresAuth: true }
  },
  {
    path: '/wallet',
    component: WalletView,
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
  } else if ((to.path === '/login' || to.path === '/register') && authStore.isAuthenticated) {
    next('/dashboard')
  } else {
    next()
  }
})

export default router
