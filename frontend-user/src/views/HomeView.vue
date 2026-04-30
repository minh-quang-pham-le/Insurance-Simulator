<template>
  <div class="min-h-screen bg-gradient-to-r from-blue-500 to-blue-600 flex items-center justify-center">
    <div class="text-center text-white">
      <h1 class="text-5xl font-bold mb-4">Insurance Simulator</h1>
      <p class="text-xl mb-8">Explore risk management through micro-insurance</p>
      <div class="flex gap-4 justify-center">
        <router-link
          v-if="!authStore.isAuthenticated"
          to="/register"
          class="px-8 py-3 bg-white text-blue-600 font-semibold rounded-lg hover:bg-gray-100 transition"
        >
          Get Started
        </router-link>
        <router-link
          v-if="!authStore.isAuthenticated"
          to="/login"
          class="px-8 py-3 bg-blue-400 text-white font-semibold rounded-lg hover:bg-blue-500 transition"
        >
          Login
        </router-link>
        <router-link
          v-else
          to="/dashboard"
          class="px-8 py-3 bg-white text-blue-600 font-semibold rounded-lg hover:bg-gray-100 transition"
        >
          Go to Dashboard
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
</script>
