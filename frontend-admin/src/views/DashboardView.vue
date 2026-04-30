<template>
  <div class="p-6">
    <h1 class="text-3xl font-bold mb-6">Admin Dashboard</h1>
    
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
      <div class="bg-white rounded-lg shadow p-6">
        <h3 class="text-gray-600 text-sm font-semibold mb-2">Active Users</h3>
        <p class="text-3xl font-bold text-purple-600">--</p>
      </div>
      <div class="bg-white rounded-lg shadow p-6">
        <h3 class="text-gray-600 text-sm font-semibold mb-2">Active Policies</h3>
        <p class="text-3xl font-bold text-purple-600">--</p>
      </div>
      <div class="bg-white rounded-lg shadow p-6">
        <h3 class="text-gray-600 text-sm font-semibold mb-2">Pending Claims</h3>
        <p class="text-3xl font-bold text-purple-600">--</p>
      </div>
      <div class="bg-white rounded-lg shadow p-6">
        <h3 class="text-gray-600 text-sm font-semibold mb-2">Total Revenue</h3>
        <p class="text-3xl font-bold text-purple-600">-- SC</p>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div class="lg:col-span-2 bg-white rounded-lg shadow p-6">
        <h2 class="text-xl font-semibold mb-4">Pending KYC Verifications</h2>
        <p class="text-gray-600 text-center py-8">
          KYC management will be implemented in Slice 7
        </p>
      </div>

      <div class="bg-white rounded-lg shadow p-6">
        <h2 class="text-xl font-semibold mb-4">Quick Links</h2>
        <nav class="space-y-2">
          <a href="#" class="block px-4 py-2 text-purple-600 hover:bg-purple-50 rounded">
            Products
          </a>
          <a href="#" class="block px-4 py-2 text-purple-600 hover:bg-purple-50 rounded">
            Policies
          </a>
          <a href="#" class="block px-4 py-2 text-purple-600 hover:bg-purple-50 rounded">
            Claims
          </a>
          <a href="#" class="block px-4 py-2 text-purple-600 hover:bg-purple-50 rounded">
            Users
          </a>
        </nav>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
</script>
