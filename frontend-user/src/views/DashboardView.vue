<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <h1 class="text-3xl font-extrabold text-gray-900 mb-6">Tổng Quan Tài Khoản</h1>

    <div class="bg-white rounded-2xl shadow-sm border border-gray-200 p-6 mb-8">
      <div class="flex justify-between items-center mb-6">
        <h2 class="text-xl font-bold text-gray-800">Hồ sơ cá nhân</h2>
        <span
          class="px-4 py-1.5 rounded-full text-sm font-bold uppercase tracking-wide border"
          :class="{
            'bg-green-50 text-green-700 border-green-200': authStore.user?.kyc_status === 'VERIFIED',
            'bg-yellow-50 text-yellow-700 border-yellow-200': authStore.user?.kyc_status === 'PENDING',
            'bg-red-50 text-red-700 border-red-200': authStore.user?.kyc_status === 'REJECTED',
            'bg-gray-50 text-gray-700 border-gray-200': authStore.user?.kyc_status === 'NOT_SUBMITTED'
          }"
        >
          KYC: {{ formatKycStatus(authStore.user?.kyc_status) }}
        </span>
      </div>
      
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div class="bg-gray-50 p-4 rounded-xl border border-gray-100">
          <p class="text-gray-500 text-sm mb-1">Họ và tên</p>
          <p class="font-bold text-gray-900 text-lg">{{ authStore.user?.full_name }}</p>
        </div>
        <div class="bg-gray-50 p-4 rounded-xl border border-gray-100">
          <p class="text-gray-500 text-sm mb-1">Email</p>
          <p class="font-bold text-gray-900 text-lg">{{ authStore.user?.email }}</p>
        </div>
        <div class="bg-gray-50 p-4 rounded-xl border border-gray-100">
          <p class="text-gray-500 text-sm mb-1">Số điện thoại</p>
          <p class="font-bold text-gray-900 text-lg">{{ authStore.user?.phone_number || 'Chưa cung cấp' }}</p>
        </div>
      </div>

      <div class="mt-6">
        <div v-if="authStore.user?.kyc_status !== 'VERIFIED'" class="bg-blue-50 border border-blue-200 rounded-xl p-5 flex flex-col sm:flex-row justify-between items-center gap-4">
          <p class="text-blue-900 text-sm">
            <strong class="font-bold text-base block mb-1">⚠️ Quan trọng:</strong> 
            Bạn cần hoàn thành xác minh danh tính (KYC) để sử dụng chức năng nạp tiền và mua bảo hiểm.
          </p>
          <router-link to="/kyc" class="whitespace-nowrap bg-blue-600 text-white px-5 py-2.5 rounded-lg font-bold hover:bg-blue-700 transition shadow-sm">
            Xác minh ngay
          </router-link>
        </div>
        <div v-else class="bg-green-50 border border-green-200 rounded-xl p-4">
          <p class="text-green-800 font-medium">
            ✓ Chúc mừng! Tài khoản của bạn đã được xác minh toàn bộ tính năng.
          </p>
        </div>
      </div>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
      <div class="bg-blue-600 rounded-2xl p-6 text-white shadow-lg relative overflow-hidden">
        <div class="relative z-10">
          <p class="text-blue-100 font-medium mb-1">Số dư khả dụng</p>
          <h2 class="text-4xl font-black mb-4">
            <span v-if="walletStore.isLoading">...</span>
            <span v-else>{{ walletStore.balance }} SC</span>
          </h2>
          <div class="flex gap-3">
            <router-link
              v-if="authStore.user?.kyc_status === 'VERIFIED'"
              to="/wallet"
              class="bg-white text-blue-600 px-5 py-2 rounded-lg font-bold text-sm hover:bg-blue-50 transition-colors shadow"
            >
              Nạp Tiền
            </router-link>
            <button 
              v-else 
              disabled 
              class="bg-blue-400 text-blue-100 px-5 py-2 rounded-lg font-bold text-sm cursor-not-allowed"
            >
              Nạp Tiền (Cần KYC)
            </button>
          </div>
        </div>
        <div class="absolute -right-6 -bottom-6 opacity-20 text-9xl">💰</div>
      </div>

      <div class="bg-white rounded-2xl p-6 border border-gray-200 shadow-sm flex flex-col justify-center">
        <div class="flex justify-between items-start">
          <div>
            <p class="text-gray-500 font-medium mb-1">Hợp đồng đang bảo vệ</p>
            <h2 class="text-4xl font-black text-gray-900">
              {{ activePoliciesCount }}
            </h2>
          </div>
          <div class="w-12 h-12 bg-indigo-50 rounded-full flex items-center justify-center text-2xl">
            🛡️
          </div>
        </div>
        <router-link to="/my-policies" class="mt-4 text-sm text-indigo-600 font-bold hover:underline inline-block">
          Xem tất cả hợp đồng →
        </router-link>
      </div>
    </div>

    <div class="bg-indigo-50 border border-indigo-100 rounded-2xl p-8 text-center mt-8">
      <h2 class="text-2xl font-bold text-indigo-900 mb-3">Bạn đang cần bảo vệ điều gì?</h2>
      <p class="text-indigo-700 mb-6">Hệ thống AI của chúng tôi sẽ tính toán rủi ro và đền bù tự động cho bạn ngay khi sự kiện xảy ra.</p>
      <router-link to="/insurance" class="inline-block bg-indigo-600 hover:bg-indigo-700 text-white font-bold px-8 py-3.5 rounded-xl transition-transform hover:scale-105 shadow-md text-lg">
        Khám Phá Danh Mục Bảo Hiểm
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useWalletStore } from '../stores/wallet'
import { usePolicyStore } from '../stores/policy'

const authStore = useAuthStore()
const walletStore = useWalletStore()
const policyStore = usePolicyStore()

onMounted(() => {
  // Chỉ gọi lấy ví và policy nếu user đã đăng nhập
  if (authStore.accessToken) {
    if (walletStore.fetchBalance) walletStore.fetchBalance()
    if (policyStore.fetchMyPolicies) policyStore.fetchMyPolicies()
  }
})

const activePoliciesCount = computed(() => {
  if (!policyStore.myPolicies) return 0
  return policyStore.myPolicies.filter(p => p.status === 'ACTIVE').length
})

const formatKycStatus = (status) => {
  const map = {
    'VERIFIED': 'Đã Xác Minh',
    'PENDING': 'Đang Chờ Duyệt',
    'NOT_SUBMITTED': 'Chưa Xác Minh',
    'REJECTED': 'Bị Từ Chối'
  }
  return map[status] || 'Không Xác Định'
}
</script>