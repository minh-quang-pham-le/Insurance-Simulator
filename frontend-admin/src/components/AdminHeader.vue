<template>
  <header class="bg-purple-600 text-white shadow">
    <div class="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
      <div class="text-2xl font-bold">
        Insurance Simulator — Admin
      </div>

      <div class="flex items-center gap-4">
        <div class="relative admin-dropdown">
          <button
            @click="showDropdown = !showDropdown"
            class="flex items-center gap-2 hover:text-purple-100 transition px-3 py-2 rounded-lg hover:bg-purple-500"
          >
            <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clip-rule="evenodd"></path>
            </svg>
            <span>{{ authStore.user?.full_name || 'Admin' }}</span>
            <span class="bg-purple-500 text-xs px-2 py-1 rounded-full">ADMIN</span>
          </button>

          <div
            v-if="showDropdown"
            class="absolute right-0 mt-2 w-48 bg-white text-gray-800 rounded-lg shadow-lg z-10"
          >
            <div class="px-4 py-3 border-b text-sm">
              <p class="font-semibold">{{ authStore.user?.full_name }}</p>
              <p class="text-gray-600">{{ authStore.user?.email }}</p>
            </div>
            <button
              @click="handleLogout"
              class="w-full text-left px-4 py-2 hover:bg-gray-100"
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

const authStore = useAuthStore()
const router = useRouter()
const showDropdown = ref(false)

function handleLogout() {
  authStore.logout()
  router.push('/login')
  showDropdown.value = false
}

function handleClickOutside(event) {
  const dropdown = document.querySelector('.admin-dropdown')
  if (dropdown && !dropdown.contains(event.target)) {
    showDropdown.value = false
  }
}

onMounted(() => document.addEventListener('click', handleClickOutside))
onUnmounted(() => document.removeEventListener('click', handleClickOutside))
</script>
