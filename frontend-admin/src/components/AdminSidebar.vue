<template>
  <aside class="w-60 bg-slate-900 min-h-screen flex flex-col flex-shrink-0">

    <!-- Logo -->
    <div class="px-5 py-5 border-b border-slate-800/60">
      <div class="flex items-center gap-2.5">
        <div class="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center flex-shrink-0">
          <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 3l8 3v6c0 4.418-3.582 8-8 9-4.418-1-8-4.582-8-9V6l8-3z"/>
            <path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4"/>
          </svg>
        </div>
        <div>
          <p class="text-white text-sm font-extrabold leading-tight tracking-tight">Insurance Sim</p>
          <p class="text-indigo-400 text-[10px] font-semibold uppercase tracking-widest">Admin Portal</p>
        </div>
      </div>
    </div>

    <!-- Navigation -->
    <nav class="flex-1 px-3 py-4 space-y-0.5 overflow-y-auto">

      <p class="section-label">Tổng quan</p>

      <router-link to="/dashboard" class="nav-item" active-class="nav-active">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="1.75" viewBox="0 0 24 24">
          <rect x="3" y="3" width="7" height="7" rx="1.5"/>
          <rect x="14" y="3" width="7" height="7" rx="1.5"/>
          <rect x="3" y="14" width="7" height="7" rx="1.5"/>
          <rect x="14" y="14" width="7" height="7" rx="1.5"/>
        </svg>
        Dashboard
      </router-link>

      <p class="section-label mt-4">Quản lý</p>

      <router-link to="/products" class="nav-item" active-class="nav-active">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="1.75" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10"/>
        </svg>
        Sản phẩm
      </router-link>

      <router-link to="/admin-policies" class="nav-item" active-class="nav-active">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="1.75" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 3l8 3v6c0 4.418-3.582 8-8 9-4.418-1-8-4.582-8-9V6l8-3z"/>
        </svg>
        Hợp đồng
      </router-link>

      <router-link to="/claims" class="nav-item" active-class="nav-active">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="1.75" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
        </svg>
        Bồi thường
      </router-link>

      <router-link to="/users" class="nav-item" active-class="nav-active">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="1.75" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"/>
        </svg>
        Người dùng
      </router-link>

      <router-link to="/kyc-review" class="nav-item" active-class="nav-active">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="1.75" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M10 6H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V8a2 2 0 00-2-2h-5m-4 0V5a2 2 0 114 0v1m-4 0a2 2 0 104 0M15 13l-3 3-1.5-1.5"/>
        </svg>
        KYC Review
      </router-link>

      <p class="section-label mt-4">Phân tích</p>

      <router-link to="/risk-analytics" class="nav-item" active-class="nav-active">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="1.75" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
        </svg>
        Risk Analytics
      </router-link>

      <router-link to="/api-monitor" class="nav-item" active-class="nav-active">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="1.75" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M8.111 16.404a5.5 5.5 0 017.778 0M12 20h.01m-7.08-7.071c3.904-3.905 10.236-3.905 14.14 0M1.394 9.393c5.857-5.857 15.355-5.857 21.213 0"/>
        </svg>
        API Monitor
      </router-link>

    </nav>

    <!-- User + Logout -->
    <div class="px-3 pb-4 border-t border-slate-800/60 pt-3">
      <div class="flex items-center gap-2.5 px-3 py-2.5 rounded-xl">
        <div class="w-8 h-8 bg-indigo-500/20 border border-indigo-500/30 rounded-lg flex items-center justify-center flex-shrink-0">
          <svg class="w-4 h-4 text-indigo-400" fill="none" stroke="currentColor" stroke-width="1.75" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
          </svg>
        </div>
        <div class="flex-1 min-w-0">
          <p class="text-white text-xs font-semibold truncate leading-tight">{{ authStore.user?.full_name || 'Admin' }}</p>
          <p class="text-slate-500 text-[10px] truncate">{{ authStore.user?.email }}</p>
        </div>
        <button
          @click="handleLogout"
          title="Đăng xuất"
          class="text-slate-600 hover:text-red-400 transition-colors p-1 rounded-lg hover:bg-slate-800"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/>
          </svg>
        </button>
      </div>
    </div>

  </aside>
</template>

<script setup>
import { useAuthStore } from '../stores/auth'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()

function handleLogout() {
  authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.section-label {
  @apply text-[10px] font-bold text-slate-600 uppercase tracking-widest px-3 mb-1.5;
}
.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 12px;
  border-radius: 10px;
  color: rgb(148 163 184);
  font-size: 13.5px;
  font-weight: 500;
  text-decoration: none;
  transition: all 0.15s ease;
}
.nav-item:hover {
  color: white;
  background-color: rgb(30 41 59);
}
.nav-active {
  background-color: rgb(79 70 229) !important;
  color: white !important;
}
</style>
