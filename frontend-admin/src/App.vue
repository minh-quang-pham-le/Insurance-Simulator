<template>
  <div class="min-h-screen bg-gray-100">
    <AdminHeader v-if="authStore.isAuthenticated" />
    <div class="flex" v-if="authStore.isAuthenticated">
      <AdminSidebar />
      <main class="flex-1">
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
import AdminHeader from './components/AdminHeader.vue'
import AdminSidebar from './components/AdminSidebar.vue'

const authStore = useAuthStore()
</script>
