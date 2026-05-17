<template>
  <aside class="w-64 bg-gray-900 text-white min-h-screen">
    <div class="p-6">
      <h2 class="text-xl font-bold text-white mb-1">Admin Panel</h2>
      <p class="text-gray-400 text-xs">Insurance Simulator</p>
    </div>
    <nav class="px-4 space-y-1">
      <router-link
        to="/dashboard"
        class="nav-link"
        active-class="bg-indigo-600 text-white"
      >
        <span class="mr-3">📊</span> Dashboard
      </router-link>
      <router-link
        to="/products"
        class="nav-link"
        active-class="bg-indigo-600 text-white"
      >
        <span class="mr-3">📦</span> Products
      </router-link>
      <router-link
        to="/admin-policies"
        class="nav-link"
        active-class="bg-indigo-600 text-white"
      >
        <span class="mr-3">🛡️</span> Policies
      </router-link>
      <router-link
        to="/claims"
        class="nav-link"
        active-class="bg-indigo-600 text-white"
      >
        <span class="mr-3">📑</span> Claims
      </router-link>
      <router-link
        to="/users"
        class="nav-link"
        active-class="bg-indigo-600 text-white"
      >
        <span class="mr-3">👥</span> Users
      </router-link>
      <router-link
        to="/kyc-review"
        class="nav-link"
        active-class="bg-indigo-600 text-white"
      >
        <span class="mr-3">📋</span> KYC Review
      </router-link>

      <div class="border-t border-gray-700 my-4"></div>

      <a href="#" class="nav-link opacity-50 cursor-not-allowed">
        <span class="mr-3">📈</span> Risk Analytics
      </a>
      <a href="#" class="nav-link opacity-50 cursor-not-allowed">
        <span class="mr-3">🔌</span> API Monitor
      </a>
    </nav>
  </aside>
</template>

<script setup>
</script>

<style scoped>
.nav-link {
  @apply block px-4 py-3 rounded-lg hover:bg-gray-700 transition font-medium text-sm;
}
</style>
