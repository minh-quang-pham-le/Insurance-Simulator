<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <div class="flex justify-between items-center mb-8">
      <div>
        <h1 class="text-3xl font-extrabold text-gray-900 tracking-tight">Hợp Đồng Của Tôi</h1>
        <p class="mt-2 text-sm text-gray-600">Quản lý các gói bảo hiểm bạn đã tham gia.</p>
      </div>
      <router-link to="/insurance" class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium transition-colors">
        + Mua Bảo Hiểm Mới
      </router-link>
    </div>

    <div v-if="policyStore.isLoading" class="flex justify-center py-20">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
    </div>

    <div v-else-if="policyStore.error" class="bg-red-50 text-red-600 p-4 rounded-lg">
      {{ policyStore.error }}
    </div>

    <div v-else-if="policyStore.myPolicies.length === 0" class="text-center py-20 bg-white rounded-xl border border-gray-200">
      <span class="text-5xl mb-4 block">📄</span>
      <h3 class="text-lg font-medium text-gray-900">Bạn chưa có hợp đồng nào</h3>
      <p class="text-gray-500 mt-1">Hãy khám phá các gói bảo hiểm vi mô của chúng tôi.</p>
    </div>

    <div v-else class="bg-white shadow overflow-hidden sm:rounded-lg border border-gray-200">
      <ul class="divide-y divide-gray-200">
        <li v-for="policy in policyStore.myPolicies" :key="policy.id" class="p-6 hover:bg-gray-50 transition-colors">
          <div class="flex items-center justify-between">
            <div class="flex-1">
              <div class="flex items-center justify-between">
                <h3 class="text-lg font-bold text-blue-900">{{ policy.product_name || 'Gói Bảo Hiểm' }}</h3>
                <span :class="getStatusClass(policy.status)" class="px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full uppercase tracking-wide">
                  {{ formatStatus(policy.status) }}
                </span>
              </div>
              
              <div class="mt-4 grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <p class="text-gray-500">Phí đã đóng</p>
                  <p class="font-semibold text-gray-900">{{ policy.premium_paid }} SC</p>
                </div>
                <div>
                  <p class="text-gray-500">Mức bồi thường</p>
                  <p class="font-semibold text-green-600">{{ policy.payout_amount }} SC</p>
                </div>
                <div>
                  <p class="text-gray-500">Ngày bắt đầu</p>
                  <p class="font-medium text-gray-900">{{ formatDate(policy.start_date) }}</p>
                </div>
                <div>
                  <p class="text-gray-500">Ngày kết thúc</p>
                  <p class="font-medium text-gray-900">{{ formatDate(policy.end_date) }}</p>
                </div>
              </div>
            </div>
          </div>
          
          <div class="mt-4 pt-4 border-t border-gray-100 flex justify-end" v-if="policy.status === 'ACTIVE'">
            <button 
              @click="handleCancel(policy.id)"
              :disabled="cancellingId === policy.id"
              class="text-red-600 hover:text-red-800 font-medium text-sm transition-colors disabled:opacity-50"
            >
              {{ cancellingId === policy.id ? 'Đang xử lý...' : 'Hủy hợp đồng (Hoàn 80%)' }}
            </button>
          </div>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { usePolicyStore } from '../stores/policy'

const policyStore = usePolicyStore()
const cancellingId = ref(null)

onMounted(() => {
  policyStore.fetchMyPolicies()
})

const handleCancel = async (id) => {
  if (!confirm('Bạn có chắc chắn muốn hủy hợp đồng này? Phí hoàn lại sẽ là 80%.')) return
  
  cancellingId.value = id
  try {
    await policyStore.cancelPolicy(id)
    alert('Đã hủy hợp đồng thành công. Tiền đã được hoàn về ví.')
  } catch (error) {
    alert(error.message)
  } finally {
    cancellingId.value = null
  }
}

// Helpers format
const formatDate = (dateString) => {
  if (!dateString) return ''
  const d = new Date(dateString)
  return d.toLocaleDateString('vi-VN')
}

const getStatusClass = (status) => {
  const classes = {
    'ACTIVE': 'bg-green-100 text-green-800',
    'EXPIRED': 'bg-gray-100 text-gray-800',
    'CLAIMED': 'bg-blue-100 text-blue-800',
    'CANCELLED': 'bg-red-100 text-red-800'
  }
  return classes[status] || 'bg-gray-100 text-gray-800'
}

const formatStatus = (status) => {
  const names = {
    'ACTIVE': 'Đang bảo vệ',
    'EXPIRED': 'Hết hạn',
    'CLAIMED': 'Đã bồi thường',
    'CANCELLED': 'Đã hủy'
  }
  return names[status] || status
}
</script>