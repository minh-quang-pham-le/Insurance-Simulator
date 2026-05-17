<template>
  <header class="bg-blue-600 text-white shadow">
    <div class="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
      <div class="flex items-center gap-8">
        <router-link to="/" class="text-2xl font-bold hover:text-blue-100">
          Insurance Simulator
        </router-link>
        <nav class="hidden md:flex gap-6">
          <router-link to="/dashboard" class="hover:text-blue-100 transition">Dashboard</router-link>
          <router-link to="/insurance" class="hover:text-blue-100 transition">Insurance</router-link>
          <router-link to="/wallet" class="hover:text-blue-100 transition">Wallet</router-link>
          <router-link to="/my-policies" class="hover:text-blue-100 transition">Policies</router-link>
        </nav>
      </div>

      <div class="flex items-center gap-4">
        <!-- Notifications Bell -->
        <NotificationBell />

        <!-- User Dropdown -->
        <div class="relative user-dropdown">
          <button
            @click="showDropdown = !showDropdown"
            class="flex items-center gap-2 hover:text-blue-100 transition px-3 py-2 rounded-lg hover:bg-blue-500"
          >
            <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clip-rule="evenodd"></path>
            </svg>
            <span>{{ authStore.user?.full_name || 'User' }}</span>
            <svg
              class="w-4 h-4 transition"
              :class="{ 'rotate-180': showDropdown }"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 14l-7 7m0 0l-7-7m7 7V3"></path>
            </svg>
          </button>

          <div
            v-if="showDropdown"
            class="absolute right-0 mt-2 w-48 bg-white text-gray-800 rounded-lg shadow-lg z-10"
          >
            <router-link
              to="/dashboard"
              class="block px-4 py-2 hover:bg-gray-100 first:rounded-t-lg"
              @click="showDropdown = false"
            >
              Profile
            </router-link>
            <router-link
              to="/kyc"
              class="block px-4 py-2 hover:bg-gray-100"
              @click="showDropdown = false"
            >
              KYC Verification
            </router-link>
            <router-link
              to="/notifications"
              class="block px-4 py-2 hover:bg-gray-100"
              @click="showDropdown = false"
            >
              Notifications
            </router-link>
            <button
              @click="handleLogout"
              class="w-full text-left px-4 py-2 hover:bg-gray-100 last:rounded-b-lg border-t"
            >
              Logout
            </button>
          </div>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import NotificationBell from './NotificationBell.vue'

const authStore = useAuthStore()
const router = useRouter()
const showDropdown = ref(false)

function handleLogout() {
  authStore.logout()
  router.push('/login')
  showDropdown.value = false
}

function handleClickOutside(event) {
  const dropdown = document.querySelector('.user-dropdown')
  if (dropdown && !dropdown.contains(event.target)) {
    showDropdown.value = false
  }
}

onMounted(() => document.addEventListener('click', handleClickOutside))
onUnmounted(() => document.removeEventListener('click', handleClickOutside))
</script>
