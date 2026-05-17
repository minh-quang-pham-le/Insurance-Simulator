<template>
  <div class="p-6">
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-bold text-gray-900">Quản Lý Hợp Đồng</h1>
      <select
        v-model="statusFilter"
        @change="handleFilter"
        class="border border-gray-300 rounded-lg px-3 py-2 text-sm bg-white"
      >
        <option value="">Tất cả trạng thái</option>
        <option value="ACTIVE">ACTIVE</option>
        <option value="EXPIRED">EXPIRED</option>
        <option value="CLAIMED">CLAIMED</option>
        <option value="CANCELLED">CANCELLED</option>
      </select>
    </div>

    <div v-if="adminStore.isLoadingPolicies" class="flex justify-center py-20">
      <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-indigo-600"></div>
    </div>

    <div v-else>
      <div class="bg-white shadow rounded-lg overflow-hidden border border-gray-200">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Sản phẩm</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">User</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Phí (SC)</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Bồi thường (SC)</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Trạng thái</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Thời hạn</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="policy in adminStore.policies" :key="policy.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap font-medium text-gray-900">
                {{ policy.product_name || '—' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ policy.user_email || '—' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-semibold text-gray-900">
                {{ policy.premium_paid }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-semibold text-green-600">
                {{ policy.payout_amount }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="getStatusClass(policy.status)" class="px-2 py-1 text-xs font-semibold rounded-full">
                  {{ policy.status }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ formatDate(policy.start_date) }} — {{ formatDate(policy.end_date) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <p class="text-sm text-gray-500 mt-4">Tổng: {{ adminStore.policiesTotal }} hợp đồng</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAdminStore } from '../stores/admin'

const adminStore = useAdminStore()
const statusFilter = ref('')

onMounted(() => {
  adminStore.fetchPolicies()
})

const handleFilter = () => {
  adminStore.fetchPolicies(0, 50, statusFilter.value || null)
}

const getStatusClass = (s) => {
  const c = {
    'ACTIVE': 'bg-green-100 text-green-800',
    'EXPIRED': 'bg-gray-100 text-gray-800',
    'CLAIMED': 'bg-blue-100 text-blue-800',
    'CANCELLED': 'bg-red-100 text-red-800',
  }
  return c[s] || 'bg-gray-100 text-gray-800'
}

const formatDate = (d) => d ? new Date(d).toLocaleDateString('vi-VN') : ''
</script>
