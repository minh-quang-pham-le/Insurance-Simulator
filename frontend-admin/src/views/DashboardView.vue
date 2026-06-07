<template>
  <div class="px-8 py-8">

    <!-- Welcome banner -->
    <div class="bg-gradient-to-r from-indigo-600 to-violet-600 rounded-2xl p-6 mb-8 text-white relative overflow-hidden shadow-lg shadow-indigo-200">
      <div class="absolute -right-8 -top-8 w-40 h-40 bg-white/10 rounded-full pointer-events-none"></div>
      <div class="absolute right-24 bottom-0 w-24 h-24 bg-white/8 rounded-full pointer-events-none"></div>
      <div class="relative z-10 flex items-center justify-between">
        <div>
          <p class="text-indigo-200 text-sm font-medium mb-1">Xin chào, {{ adminName }} 👋</p>
          <h1 class="text-2xl font-extrabold tracking-tight">Admin Dashboard</h1>
          <p class="text-indigo-200 text-sm mt-1">{{ today }} · Hệ thống đang hoạt động bình thường</p>
        </div>
        <div class="hidden md:flex items-center gap-2 bg-white/15 border border-white/20 rounded-2xl px-4 py-3">
          <div class="w-2 h-2 bg-emerald-400 rounded-full animate-pulse"></div>
          <span class="text-sm font-semibold">Live</span>
        </div>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="adminStore.isLoadingDashboard" class="flex items-center justify-center py-24">
      <svg class="animate-spin w-8 h-8 text-indigo-600" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
        <path stroke-linecap="round" d="M12 3a9 9 0 1 0 9 9"/>
      </svg>
    </div>

    <template v-else-if="metrics">

      <!-- Row 1: Main KPIs — gradient cards -->
      <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4 mb-4">
        <StatsCard
          label="Tổng người dùng"
          :value="metrics.total_users"
          icon="users"
          color="blue"
          variant="gradient"
        />
        <StatsCard
          label="Hợp đồng hoạt động"
          :value="metrics.total_active_policies"
          icon="shield"
          color="indigo"
          variant="gradient"
        />
        <StatsCard
          label="Doanh thu (SC)"
          :value="metrics.revenue"
          format="currency"
          icon="currency"
          color="emerald"
          variant="gradient"
        />
        <StatsCard
          label="KYC chờ duyệt"
          :value="metrics.pending_kyc_count"
          icon="clipboard"
          color="amber"
          variant="gradient"
        />
      </div>

      <!-- Row 2: Financial — white left-border cards -->
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-4">
        <StatsCard
          label="Tổng phí thu được"
          :value="metrics.total_premiums_collected"
          format="currency"
          icon="trending-up"
          color="indigo"
        />
        <StatsCard
          label="Tổng bồi thường đã trả"
          :value="metrics.total_claims_paid"
          format="currency"
          icon="payout"
          color="red"
          valueClass="text-red-600"
        />
        <StatsCard
          label="Loss Ratio"
          :value="metrics.loss_ratio"
          format="percent"
          icon="chart"
          color="violet"
          :valueClass="metrics.loss_ratio > 0.7 ? 'text-red-600' : 'text-emerald-600'"
          :subtext="metrics.loss_ratio > 0.7 ? '⚠ Tỷ lệ tổn thất cao' : '✓ Tỷ lệ tổn thất ổn định'"
        />
      </div>

      <!-- Row 3: Activity — gradient cards -->
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-8">
        <StatsCard
          label="Đăng ký mới (30 ngày)"
          :value="metrics.new_registrations_30d"
          icon="user-plus"
          color="teal"
          variant="gradient"
        />
        <StatsCard
          label="Người dùng hoạt động"
          :value="metrics.active_users"
          icon="check-circle"
          color="emerald"
          variant="gradient"
        />
      </div>

      <!-- Quick Actions -->
      <div class="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
        <p class="text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-4">Hành động nhanh</p>
        <div class="flex flex-wrap gap-3">
          <router-link
            to="/kyc-review"
            class="inline-flex items-center gap-2 bg-amber-500 hover:bg-amber-600 active:scale-95 text-white px-4 py-2.5 rounded-xl font-semibold text-sm transition-all shadow-sm shadow-amber-200"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"/>
            </svg>
            Duyệt KYC
            <span class="bg-white/25 text-white text-xs font-bold px-1.5 py-0.5 rounded-lg">{{ metrics.pending_kyc_count }}</span>
          </router-link>
          <router-link
            to="/claims"
            class="inline-flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 active:scale-95 text-white px-4 py-2.5 rounded-xl font-semibold text-sm transition-all shadow-sm shadow-indigo-200"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
            Xem Claims
          </router-link>
          <router-link
            to="/users"
            class="inline-flex items-center gap-2 bg-slate-700 hover:bg-slate-800 active:scale-95 text-white px-4 py-2.5 rounded-xl font-semibold text-sm transition-all"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z"/>
            </svg>
            Quản lý Users
          </router-link>
          <router-link
            to="/admin-policies"
            class="inline-flex items-center gap-2 bg-emerald-600 hover:bg-emerald-700 active:scale-95 text-white px-4 py-2.5 rounded-xl font-semibold text-sm transition-all shadow-sm shadow-emerald-200"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 3l8 3v6c0 4.418-3.582 8-8 9-4.418-1-8-4.582-8-9V6l8-3z"/>
            </svg>
            Quản lý Policies
          </router-link>
        </div>
      </div>

    </template>
  </div>
</template>

<script setup>
import { onMounted, computed } from 'vue'
import { useAdminStore } from '../stores/admin'
import { useAuthStore } from '../stores/auth'
import StatsCard from '../components/StatsCard.vue'

const adminStore = useAdminStore()
const authStore = useAuthStore()
const metrics = computed(() => adminStore.dashboardMetrics)
const adminName = computed(() => authStore.user?.full_name?.split(' ').slice(-1)[0] || 'Admin')

const today = new Date().toLocaleDateString('vi-VN', {
  weekday: 'long', day: 'numeric', month: 'long', year: 'numeric'
})

onMounted(() => {
  adminStore.fetchDashboard()
})
</script>
