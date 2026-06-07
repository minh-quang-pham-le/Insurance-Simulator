<template>
  <div class="min-h-screen bg-slate-50">
    <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">

      <div class="flex items-start justify-between mb-6">
        <div>
          <h1 class="text-2xl font-extrabold text-slate-900 tracking-tight">Hợp Đồng Của Tôi</h1>
          <p class="text-slate-500 text-sm mt-0.5">Quản lý các gói bảo hiểm bạn đã tham gia.</p>
        </div>
        <router-link
          to="/insurance"
          class="bg-blue-600 hover:bg-blue-700 active:scale-95 text-white px-4 py-2.5 rounded-xl font-bold text-sm transition-all"
        >
          + Mua mới
        </router-link>
      </div>

      <!-- Loading -->
      <div v-if="policyStore.isLoading" class="flex justify-center py-20">
        <div class="animate-spin rounded-full h-12 w-12 border-4 border-blue-100 border-t-blue-600"></div>
      </div>

      <!-- Error -->
      <div
        v-else-if="policyStore.error"
        class="bg-red-50 text-red-600 p-4 rounded-xl border border-red-100 text-sm"
      >
        {{ policyStore.error }}
      </div>

      <!-- Empty -->
      <div
        v-else-if="policyStore.myPolicies.length === 0"
        class="text-center py-20 bg-white rounded-2xl border border-slate-200"
      >
        <div class="text-5xl mb-4">📄</div>
        <h3 class="text-base font-bold text-slate-800">Chưa có hợp đồng nào</h3>
        <p class="text-slate-500 text-sm mt-1 mb-5">Hãy khám phá các gói bảo hiểm vi mô của chúng tôi.</p>
        <router-link
          to="/insurance"
          class="inline-block bg-blue-600 hover:bg-blue-700 text-white font-bold px-6 py-2.5 rounded-xl text-sm transition-colors"
        >
          Khám phá ngay →
        </router-link>
      </div>

      <!-- Policy list -->
      <div v-else class="space-y-4">
        <div
          v-for="policy in policyStore.myPolicies"
          :key="policy.id"
          class="bg-white rounded-2xl border border-slate-200 p-6 transition-all"
          :class="{ 'opacity-60': policy.status === 'CANCELLED' || policy.status === 'EXPIRED' }"
        >
          <!-- Header -->
          <div class="flex items-start justify-between gap-4 mb-5">
            <div class="flex items-center gap-3">
              <div
                class="w-10 h-10 bg-blue-50 rounded-xl flex items-center justify-center text-xl flex-shrink-0"
              >
                {{ getCategoryIcon(policy.product_category) }}
              </div>
              <div>
                <h3 class="text-base font-bold text-slate-900 leading-tight">
                  {{ policy.product_name || 'Gói Bảo Hiểm' }}
                </h3>
                <p class="text-slate-400 text-xs mt-0.5 font-mono">
                  #{{ policy.id.substring(0, 8).toUpperCase() }}
                </p>
              </div>
            </div>
            <span
              class="px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wide flex-shrink-0"
              :class="getStatusChip(policy.status)"
            >
              {{ formatStatus(policy.status) }}
            </span>
          </div>

          <!-- Stats grid -->
          <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-5">
            <div class="bg-slate-50 rounded-xl p-3 border border-slate-100">
              <p class="text-slate-400 text-[11px] mb-0.5">Phí đóng</p>
              <p class="font-bold text-slate-800 text-sm tabular-nums">
                {{ policy.premium_paid.toLocaleString() }} SC
              </p>
            </div>
            <div class="bg-slate-50 rounded-xl p-3 border border-slate-100">
              <p class="text-slate-400 text-[11px] mb-0.5">Mức bồi thường</p>
              <p class="font-bold text-emerald-600 text-sm tabular-nums">
                {{ policy.payout_amount.toLocaleString() }} SC
              </p>
            </div>
            <div class="bg-slate-50 rounded-xl p-3 border border-slate-100">
              <p class="text-slate-400 text-[11px] mb-0.5">Ngày bắt đầu</p>
              <p class="font-semibold text-slate-800 text-sm">{{ formatDate(policy.start_date) }}</p>
            </div>
            <div class="bg-slate-50 rounded-xl p-3 border border-slate-100">
              <p class="text-slate-400 text-[11px] mb-0.5">Ngày kết thúc</p>
              <p class="font-semibold text-slate-800 text-sm">{{ formatDate(policy.end_date) }}</p>
            </div>
          </div>

          <!-- Cancel action -->
          <div
            v-if="policy.status === 'ACTIVE'"
            class="flex items-center justify-between pt-4 border-t border-slate-100"
          >
            <p class="text-xs text-slate-400">Hoàn 80% phí khi huỷ</p>
            <button
              @click="handleCancel(policy.id)"
              :disabled="cancellingId === policy.id"
              class="text-red-500 hover:text-red-700 font-semibold text-sm transition-colors disabled:opacity-40"
            >
              {{ cancellingId === policy.id ? 'Đang xử lý...' : 'Huỷ hợp đồng' }}
            </button>
          </div>
        </div>
      </div>

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
  if (!confirm('Bạn có chắc muốn huỷ hợp đồng này? Phí hoàn lại là 80%.')) return
  cancellingId.value = id
  try {
    await policyStore.cancelPolicy(id)
    alert('Đã huỷ hợp đồng thành công. Tiền đã được hoàn về ví.')
  } catch (error) {
    alert(error.message)
  } finally {
    cancellingId.value = null
  }
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString('vi-VN')
}

const getCategoryIcon = (category) => {
  const icons = { FLIGHT_DELAY: '✈️', CROP_WEATHER: '🌾' }
  return icons[category] || '🛡️'
}

const getStatusChip = (status) => {
  const map = {
    ACTIVE:    'bg-emerald-100 text-emerald-700',
    EXPIRED:   'bg-slate-100 text-slate-500',
    CLAIMED:   'bg-blue-100 text-blue-700',
    CANCELLED: 'bg-red-100 text-red-500',
  }
  return map[status] || 'bg-slate-100 text-slate-600'
}

const formatStatus = (status) => {
  const names = {
    ACTIVE:    'Đang bảo vệ',
    EXPIRED:   'Hết hạn',
    CLAIMED:   'Đã bồi thường',
    CANCELLED: 'Đã huỷ',
  }
  return names[status] || status
}
</script>
