<template>
  <div class="max-w-md mx-auto p-6 mt-8">
    <h1 class="text-3xl font-bold mb-6">KYC Verification</h1>

    <div class="bg-white rounded-lg shadow p-6 mb-6">
      <h2 class="text-lg font-semibold mb-4">Status</h2>

      <div
        class="p-4 rounded-lg mb-4"
        :class="{
          'bg-green-50 border border-green-200': kycStatus === 'VERIFIED',
          'bg-yellow-50 border border-yellow-200': kycStatus === 'PENDING',
          'bg-red-50 border border-red-200': kycStatus === 'REJECTED',
          'bg-gray-50 border border-gray-200': kycStatus === 'NOT_SUBMITTED'
        }"
      >
        <p class="font-semibold mb-2" :class="{
          'text-green-900': kycStatus === 'VERIFIED',
          'text-yellow-900': kycStatus === 'PENDING',
          'text-red-900': kycStatus === 'REJECTED',
          'text-gray-900': kycStatus === 'NOT_SUBMITTED'
        }">
          {{ getStatusLabel(kycStatus) }}
        </p>

        <p v-if="kycStatus === 'VERIFIED'" class="text-green-700">
          ✓ Your KYC has been verified successfully!
        </p>
        <p v-if="kycStatus === 'PENDING'" class="text-yellow-700">
          Your KYC is under review by our admin team. You will be notified once it's processed.
        </p>
        <p v-if="kycStatus === 'REJECTED'" class="text-red-700">
          {{ authStore.user?.kyc_rejection_reason }}
        </p>
        <p v-if="kycStatus === 'NOT_SUBMITTED'" class="text-gray-700">
          Please submit your KYC information below to get started.
        </p>
      </div>
    </div>

    <form v-if="kycStatus !== 'VERIFIED'" @submit.prevent="handleSubmit" class="bg-white rounded-lg shadow p-6 space-y-4">
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">Phone Number *</label>
        <input
          v-model="phoneNumber"
          type="tel"
          required
          placeholder="+84901234567 or 0901234567"
          class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
        <p class="text-xs text-gray-500 mt-1">Format: +84... or numeric digits (10-20 chars)</p>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">Identity Details (optional)</label>
        <textarea
          v-model="identityDetails"
          placeholder="e.g., ID card number, passport number, or other identity information"
          class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          rows="4"
        ></textarea>
        <p class="text-xs text-gray-500 mt-1">Max 500 characters</p>
      </div>

      <div v-if="error" class="error-message">
        {{ error }}
      </div>

      <div v-if="success" class="success-message">
        {{ success }}
      </div>

      <button
        type="submit"
        :disabled="loading || kycStatus === 'VERIFIED' || kycStatus === 'PENDING'"
        class="w-full px-4 py-2 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <span v-if="!loading">Submit KYC</span>
        <span v-else class="flex items-center justify-center gap-2">
          <span class="spinner"></span>
          Submitting...
        </span>
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
const phoneNumber = ref('')
const identityDetails = ref('')
const kycStatus = ref(authStore.user?.kyc_status || 'NOT_SUBMITTED')
const loading = ref(false)
const error = ref('')
const success = ref('')

function getStatusLabel(status) {
  const labels = {
    'NOT_SUBMITTED': 'Not Submitted',
    'PENDING': 'Pending Review',
    'VERIFIED': 'Verified ✓',
    'REJECTED': 'Rejected'
  }
  return labels[status] || status
}

async function handleSubmit() {
  error.value = ''
  success.value = ''

  if (!phoneNumber.value) {
    error.value = 'Phone number is required'
    return
  }

  if (phoneNumber.value.length < 10) {
    error.value = 'Phone number must be at least 10 characters'
    return
  }

  loading.value = true

  try {
    await authStore.submitKyc(phoneNumber.value, identityDetails.value)
    kycStatus.value = authStore.user?.kyc_status
    success.value = 'KYC submitted successfully! Awaiting admin review...'
    phoneNumber.value = ''
    identityDetails.value = ''
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to submit KYC'
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  // Refresh user data
  try {
    await authStore.fetchMe()
    kycStatus.value = authStore.user?.kyc_status
  } catch (err) {
    console.error('Failed to fetch user data', err)
  }
})
</script>
