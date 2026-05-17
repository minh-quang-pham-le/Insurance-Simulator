<template>
  <div class="p-6">
    <h1 class="text-2xl font-bold text-gray-900 mb-6">Admin Dashboard</h1>

    <div v-if="adminStore.isLoadingDashboard" class="flex justify-center py-20">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
    </div>

    <template v-else-if="metrics">
      <!-- Row 1: Main metrics -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <StatsCard
          label="Tổng người dùng"
          :value="metrics.total_users"
          icon="👥"
          iconBg="bg-blue-100"
        />
        <StatsCard
          label="Hợp đồng đang hoạt động"
          :value="metrics.total_active_policies"
          icon="🛡️"
          iconBg="bg-green-100"
        />
        <StatsCard
          label="Doanh thu (SC)"
          :value="metrics.revenue"
          format="currency"
          icon="💰"
          iconBg="bg-yellow-100"
          valueClass="text-green-700"
        />
        <StatsCard
          label="KYC chờ duyệt"
          :value="metrics.pending_kyc_count"
          icon="📋"
          iconBg="bg-orange-100"
          :valueClass="metrics.pending_kyc_count > 0 ? 'text-orange-600' : 'text-gray-900'"
        />
      </div>

      <!-- Row 2: Financial -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <StatsCard
          label="Tổng phí thu được"
          :value="metrics.total_premiums_collected"
          format="currency"
          icon="📈"
          iconBg="bg-indigo-100"
        />
        <StatsCard
          label="Tổng bồi thường đã trả"
          :value="metrics.total_claims_paid"
          format="currency"
          icon="💸"
          iconBg="bg-red-100"
          valueClass="text-red-600"
        />
        <StatsCard
          label="Loss Ratio"
          :value="metrics.loss_ratio"
          format="percent"
          icon="📊"
          iconBg="bg-purple-100"
          :valueClass="metrics.loss_ratio > 0.7 ? 'text-red-600' : 'text-green-600'"
          :subtext="metrics.loss_ratio > 0.7 ? '⚠️ Tỷ lệ tổn thất cao' : '✓ Tỷ lệ tổn thất ổn định'"
        />
      </div>

      <!-- Row 3: Activity -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <StatsCard
          label="Đăng ký mới (30 ngày)"
          :value="metrics.new_registrations_30d"
          icon="🆕"
          iconBg="bg-teal-100"
        />
        <StatsCard
          label="Người dùng hoạt động"
          :value="metrics.active_users"
          icon="✅"
          iconBg="bg-emerald-100"
        />
      </div>

      <!-- Quick Actions -->
      <div class="mt-8 bg-gray-50 rounded-xl border border-gray-200 p-6">
        <h2 class="text-lg font-bold text-gray-800 mb-4">Hành động nhanh</h2>
        <div class="flex flex-wrap gap-3">
          <router-link
            to="/kyc-review"
            class="bg-orange-500 hover:bg-orange-600 text-white px-5 py-2.5 rounded-lg font-medium transition-colors text-sm"
          >
            📋 Duyệt KYC ({{ metrics.pending_kyc_count }})
          </router-link>
          <router-link
            to="/claims"
            class="bg-indigo-600 hover:bg-indigo-700 text-white px-5 py-2.5 rounded-lg font-medium transition-colors text-sm"
          >
            📑 Xem Claims
          </router-link>
          <router-link
            to="/users"
            class="bg-blue-600 hover:bg-blue-700 text-white px-5 py-2.5 rounded-lg font-medium transition-colors text-sm"
          >
            👥 Quản lý Users
          </router-link>
          <router-link
            to="/admin-policies"
            class="bg-green-600 hover:bg-green-700 text-white px-5 py-2.5 rounded-lg font-medium transition-colors text-sm"
          >
            🛡️ Quản lý Policies
          </router-link>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { onMounted, computed } from 'vue'
import { useAdminStore } from '../stores/admin'
import StatsCard from '../components/StatsCard.vue'

const adminStore = useAdminStore()
const metrics = computed(() => adminStore.dashboardMetrics)

onMounted(() => {
  adminStore.fetchDashboard()
})
</script>
