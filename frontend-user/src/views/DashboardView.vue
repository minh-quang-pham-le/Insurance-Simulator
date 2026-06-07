<template>
  <div class="min-h-screen bg-slate-50">
    <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">

      <!-- Welcome -->
      <div>
        <h1 class="text-2xl font-extrabold text-slate-900 tracking-tight">
          Xin chào, {{ firstName }} 👋
        </h1>
        <p class="text-slate-500 text-sm mt-0.5">Đây là tổng quan tài khoản của bạn.</p>
      </div>

      <!-- KYC banner -->
      <div
        v-if="authStore.user?.kyc_status !== 'VERIFIED'"
        class="bg-amber-50 border border-amber-200 rounded-2xl p-5 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4"
      >
        <div>
          <p class="font-bold text-amber-900 text-sm mb-1">⚠️ Xác minh danh tính (KYC) chưa hoàn thành</p>
          <p class="text-amber-700 text-sm">Hoàn thành KYC để nạp tiền và mua bảo hiểm.</p>
        </div>
        <router-link
          to="/kyc"
          class="whitespace-nowrap bg-amber-500 hover:bg-amber-600 text-white font-bold px-5 py-2.5 rounded-xl text-sm transition-colors"
        >
          Xác minh ngay →
        </router-link>
      </div>
      <div
        v-else
        class="bg-emerald-50 border border-emerald-200 rounded-2xl p-4 flex items-center gap-3"
      >
        <span class="text-emerald-500 text-lg font-bold">✓</span>
        <p class="text-emerald-800 text-sm font-medium">
          Tài khoản đã xác minh — toàn bộ tính năng đã được mở khoá.
        </p>
      </div>

      <!-- Stats row -->
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <!-- Balance -->
        <div
          class="bg-gradient-to-br from-blue-700 to-blue-900 rounded-2xl p-6 text-white shadow-lg relative overflow-hidden"
        >
          <div class="relative z-10">
            <p class="text-blue-200 text-xs font-semibold uppercase tracking-wider mb-2">
              Số dư khả dụng
            </p>
            <div class="flex items-baseline gap-2 mb-4">
              <span class="text-4xl font-black tabular-nums">
                {{ walletStore.isLoading ? '···' : walletStore.balance.toLocaleString('vi-VN') }}
              </span>
              <span class="text-lg font-bold text-blue-200">SC</span>
            </div>
            <router-link
              v-if="authStore.user?.kyc_status === 'VERIFIED'"
              to="/wallet"
              class="inline-block bg-white text-blue-700 hover:bg-blue-50 font-bold px-4 py-2 rounded-xl text-sm transition-colors"
            >
              Nạp tiền →
            </router-link>
            <span
              v-else
              class="inline-block bg-blue-400/30 text-blue-100 px-4 py-2 rounded-xl text-sm font-semibold cursor-not-allowed"
            >
              Cần KYC để nạp tiền
            </span>
          </div>
          <div class="absolute -right-3 -bottom-3 text-[6rem] opacity-10 select-none">🪙</div>
        </div>

        <!-- Active policies -->
        <div
          class="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm flex flex-col justify-between"
        >
          <div class="flex items-start justify-between">
            <div>
              <p class="text-slate-400 text-xs font-semibold uppercase tracking-wider mb-2">
                Đang bảo vệ
              </p>
              <p class="text-4xl font-black text-slate-900 tabular-nums">
                {{ activePoliciesCount }}
              </p>
              <p class="text-slate-400 text-sm mt-1">hợp đồng đang hoạt động</p>
            </div>
            <div
              class="w-12 h-12 bg-blue-50 rounded-xl flex items-center justify-center text-2xl flex-shrink-0"
            >
              🛡️
            </div>
          </div>
          <router-link
            to="/my-policies"
            class="mt-4 text-sm text-blue-600 font-bold hover:text-blue-700 transition-colors"
          >
            Xem tất cả hợp đồng →
          </router-link>
        </div>
      </div>

      <!-- Profile -->
      <div class="bg-white rounded-2xl border border-slate-200 p-6">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-base font-bold text-slate-900">Hồ sơ cá nhân</h2>
          <span
            class="px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wide border"
            :class="kycChip"
          >
            {{ formatKycStatus(authStore.user?.kyc_status) }}
          </span>
        </div>
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div class="bg-slate-50 p-4 rounded-xl border border-slate-100">
            <p class="text-slate-400 text-xs mb-1">Họ và tên</p>
            <p class="font-bold text-slate-900 text-sm">{{ authStore.user?.full_name }}</p>
          </div>
          <div class="bg-slate-50 p-4 rounded-xl border border-slate-100">
            <p class="text-slate-400 text-xs mb-1">Email</p>
            <p class="font-bold text-slate-900 text-sm truncate">{{ authStore.user?.email }}</p>
          </div>
          <div class="bg-slate-50 p-4 rounded-xl border border-slate-100">
            <p class="text-slate-400 text-xs mb-1">Số điện thoại</p>
            <p class="font-bold text-slate-900 text-sm">
              {{ authStore.user?.phone_number || 'Chưa cung cấp' }}
            </p>
          </div>
        </div>
      </div>

      <!-- CTA -->
      <div class="bg-gradient-to-br from-blue-600 to-indigo-700 rounded-2xl p-8 text-center text-white">
        <h2 class="text-xl font-extrabold mb-2">Bạn muốn bảo vệ điều gì?</h2>
        <p class="text-blue-100 text-sm mb-5">
          AI tính toán rủi ro và chi trả tự động khi sự kiện xảy ra — không cần khai báo thủ công.
        </p>
        <router-link
          to="/insurance"
          class="inline-block bg-white text-blue-700 hover:bg-blue-50 font-bold px-7 py-3 rounded-xl transition-all hover:scale-105 text-sm shadow-md"
        >
          Khám Phá Danh Mục Bảo Hiểm →
        </router-link>
      </div>

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
  if (authStore.accessToken) {
    if (walletStore.fetchBalance) walletStore.fetchBalance()
    if (policyStore.fetchMyPolicies) policyStore.fetchMyPolicies()
  }
})

const firstName = computed(() => {
  const name = authStore.user?.full_name
  if (!name) return 'bạn'
  return name.split(' ').pop()
})

const activePoliciesCount = computed(() => {
  if (!policyStore.myPolicies) return 0
  return policyStore.myPolicies.filter((p) => p.status === 'ACTIVE').length
})

const kycChip = computed(() => {
  const s = authStore.user?.kyc_status
  if (s === 'VERIFIED') return 'bg-emerald-100 text-emerald-700 border-emerald-200'
  if (s === 'PENDING')  return 'bg-amber-100 text-amber-700 border-amber-200'
  if (s === 'REJECTED') return 'bg-red-100 text-red-700 border-red-200'
  return 'bg-slate-100 text-slate-600 border-slate-200'
})

const formatKycStatus = (status) => {
  const map = {
    VERIFIED:      'Đã Xác Minh',
    PENDING:       'Đang Chờ Duyệt',
    NOT_SUBMITTED: 'Chưa Xác Minh',
    REJECTED:      'Bị Từ Chối',
  }
  return map[status] || 'Không xác định'
}
</script>
