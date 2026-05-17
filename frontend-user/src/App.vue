<template>
  <div class="min-h-screen bg-gray-50">
    <AppHeader v-if="authStore.isAuthenticated" />
    <main>
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import { useAuthStore } from './stores/auth'
import AppHeader from './components/AppHeader.vue'

const authStore = useAuthStore()
</script>

<style scoped>
main {
  min-height: calc(100vh - 64px);
}
</style>
