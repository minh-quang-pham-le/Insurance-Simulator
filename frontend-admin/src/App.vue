<template>
  <div class="min-h-screen bg-slate-50">
    <div v-if="authStore.isAuthenticated" class="flex min-h-screen">
      <AdminSidebar />
      <main class="flex-1 overflow-auto min-w-0">
        <RouterView />
      </main>
    </div>
    <div v-else>
      <RouterView />
    </div>
  </div>
</template>

<script setup>
import { useAuthStore } from './stores/auth'
import AdminSidebar from './components/AdminSidebar.vue'

const authStore = useAuthStore()
</script>
