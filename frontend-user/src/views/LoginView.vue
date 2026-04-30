<template>
  <div class="min-h-screen bg-gray-100 flex items-center justify-center px-4">
    <div class="bg-white p-8 rounded-lg shadow-lg w-full max-w-md">
      <h1 class="text-3xl font-bold mb-2 text-center text-gray-800">Login</h1>
      <p class="text-gray-600 text-center mb-6">Sign in to your account</p>

      <form @submit.prevent="handleLogin" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Email</label>
          <input
            v-model="email"
            type="email"
            required
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="you@example.com"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Password</label>
          <input
            v-model="password"
            type="password"
            required
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="••••••••"
          />
        </div>

        <div v-if="error" class="error-message">
          {{ error }}
        </div>

        <button
          type="submit"
          :disabled="loading"
          class="w-full bg-blue-600 text-white py-2 px-4 rounded-lg font-semibold hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <span v-if="!loading">Sign In</span>
          <span v-else class="flex items-center justify-center gap-2">
            <span class="spinner"></span>
            Signing in...
          </span>
        </button>
      </form>

      <p class="mt-6 text-center text-gray-600">
        Don't have an account?
        <router-link to="/register" class="text-blue-600 hover:text-blue-700 font-semibold">
          Register here
        </router-link>
      </p>
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
    router.push('/dashboard')
  } catch (err) {
    error.value = err.response?.data?.detail || 'Login failed. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>
