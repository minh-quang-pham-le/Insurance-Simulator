<template>
  <div class="min-h-screen bg-slate-950 flex items-center justify-center px-4 py-12 relative overflow-hidden">

    <!-- Background blobs -->
    <div class="absolute top-0 left-1/2 -translate-x-1/2 w-[600px] h-[400px] bg-indigo-600/10 rounded-full blur-3xl pointer-events-none"></div>
    <div class="absolute bottom-0 right-0 w-80 h-80 bg-violet-600/8 rounded-full blur-3xl pointer-events-none"></div>

    <div class="relative z-10 w-full max-w-sm">

      <!-- Logo -->
      <div class="flex flex-col items-center mb-10">
        <div class="w-14 h-14 bg-indigo-600 rounded-2xl flex items-center justify-center shadow-xl shadow-indigo-900/50 mb-4">
          <svg class="w-7 h-7 text-white" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 3l8 3v6c0 4.418-3.582 8-8 9-4.418-1-8-4.582-8-9V6l8-3z"/>
            <path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4"/>
          </svg>
        </div>
        <h1 class="text-2xl font-extrabold text-white tracking-tight">Insurance Simulator</h1>
        <p class="text-slate-500 text-sm mt-1">Admin Portal — Restricted Access</p>
      </div>

      <!-- Card -->
      <div class="bg-slate-900 border border-slate-800 rounded-2xl p-8 shadow-2xl">
        <h2 class="text-lg font-bold text-white mb-6">Đăng nhập</h2>

        <form @submit.prevent="handleLogin" class="space-y-4">
          <!-- Email -->
          <div>
            <label class="block text-[11px] font-bold text-slate-500 mb-1.5 uppercase tracking-wider">Email</label>
            <div class="relative">
              <span class="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-600 pointer-events-none">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="1.75" viewBox="0 0 24 24">
                  <rect x="2" y="4" width="20" height="16" rx="2"/>
                  <path stroke-linecap="round" stroke-linejoin="round" d="m2 7 10 7 10-7"/>
                </svg>
              </span>
              <input
                v-model="email"
                type="email"
                required
                placeholder="admin@example.com"
                class="w-full bg-slate-800 border border-slate-700 text-white placeholder-slate-600 rounded-xl pl-10 pr-4 py-3 text-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none transition-colors"
              />
            </div>
          </div>

          <!-- Password -->
          <div>
            <label class="block text-[11px] font-bold text-slate-500 mb-1.5 uppercase tracking-wider">Mật khẩu</label>
            <div class="relative">
              <span class="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-600 pointer-events-none">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="1.75" viewBox="0 0 24 24">
                  <rect x="3" y="11" width="18" height="11" rx="2"/>
                  <path stroke-linecap="round" stroke-linejoin="round" d="M7 11V7a5 5 0 0 1 10 0v4"/>
                </svg>
              </span>
              <input
                v-model="password"
                type="password"
                required
                placeholder="••••••••"
                class="w-full bg-slate-800 border border-slate-700 text-white placeholder-slate-600 rounded-xl pl-10 pr-4 py-3 text-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none transition-colors"
              />
            </div>
          </div>

          <!-- Error -->
          <div v-if="error" class="bg-red-500/10 border border-red-500/20 rounded-xl p-3 flex items-start gap-2">
            <svg class="w-4 h-4 text-red-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v4m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/>
            </svg>
            <p class="text-red-400 text-xs">{{ error }}</p>
          </div>

          <!-- Submit -->
          <button
            type="submit"
            :disabled="loading"
            class="w-full bg-indigo-600 hover:bg-indigo-500 active:scale-[0.98] text-white font-bold py-3 rounded-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed text-sm mt-2"
          >
            <span v-if="!loading" class="flex items-center justify-center gap-2">
              Đăng nhập
              <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M13.5 4.5 21 12m0 0-7.5 7.5M21 12H3"/>
              </svg>
            </span>
            <span v-else class="flex items-center justify-center gap-2">
              <svg class="animate-spin w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path stroke-linecap="round" d="M12 3a9 9 0 1 0 9 9"/>
              </svg>
              Đang xử lý...
            </span>
          </button>
        </form>
      </div>

      <!-- Warning note -->
      <div class="mt-4 flex items-center justify-center gap-2 text-slate-600 text-xs">
        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <rect x="3" y="11" width="18" height="11" rx="2"/>
          <path stroke-linecap="round" d="M7 11V7a5 5 0 0 1 10 0v4"/>
        </svg>
        Chỉ dành cho tài khoản quản trị viên
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const email = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')
const router = useRouter()
const authStore = useAuthStore()

async function handleLogin() {
  error.value = ''
  loading.value = true
  try {
    await authStore.login(email.value, password.value)
    if (authStore.user?.role !== 'ADMIN') {
      error.value = 'Tài khoản này không có quyền truy cập admin.'
      authStore.logout()
      loading.value = false
      return
    }
    router.push('/dashboard')
  } catch (err) {
    error.value = err.response?.data?.detail || 'Đăng nhập thất bại. Vui lòng thử lại.'
  } finally {
    loading.value = false
  }
}
</script>
