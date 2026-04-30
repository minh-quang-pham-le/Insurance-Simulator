<template>
  <div class="max-w-4xl mx-auto p-6">
    <h1 class="text-3xl font-bold mb-6">Dashboard</h1>

    <div class="bg-white rounded-lg shadow p-6 mb-6">
      <h2 class="text-xl font-semibold mb-4">Profile</h2>
      <div class="grid grid-cols-2 gap-4">
        <div>
          <p class="text-gray-600 text-sm">Name</p>
          <p class="text-lg font-semibold">{{ authStore.user?.full_name }}</p>
        </div>
        <div>
          <p class="text-gray-600 text-sm">Email</p>
          <p class="text-lg font-semibold">{{ authStore.user?.email }}</p>
        </div>
        <div>
          <p class="text-gray-600 text-sm">KYC Status</p>
          <p
            class="text-lg font-semibold"
            :class="{
              'text-green-600': authStore.user?.kyc_status === 'VERIFIED',
              'text-yellow-600': authStore.user?.kyc_status === 'PENDING',
              'text-red-600': authStore.user?.kyc_status === 'REJECTED',
              'text-gray-600': authStore.user?.kyc_status === 'NOT_SUBMITTED'
            }"
          >
            {{ authStore.user?.kyc_status }}
          </p>
        </div>
        <div>
          <p class="text-gray-600 text-sm">Phone</p>
          <p class="text-lg font-semibold">{{ authStore.user?.phone_number || 'Not provided' }}</p>
        </div>
      </div>
    </div>

    <div v-if="authStore.user?.kyc_status !== 'VERIFIED'" class="bg-blue-50 border border-blue-200 rounded-lg p-6">
      <p class="text-blue-900 mb-4">
        <strong>Important:</strong> You must complete KYC verification before you can use wallet and insurance features.
      </p>
      <router-link
        to="/kyc"
        class="inline-block px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
      >
        Complete KYC Verification
      </router-link>
    </div>

    <div v-else class="bg-green-50 border border-green-200 rounded-lg p-6">
      <p class="text-green-900">
        ✓ Your KYC is verified! You can now use all features.
      </p>
    </div>
  </div>
</template>

<script setup>
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
</script>
