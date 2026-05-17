<template>
  <div class="bg-gray-50 rounded-xl p-5 border border-gray-200 mt-6">
    <h3 class="text-lg font-bold text-gray-900 mb-4">Bảng Tính Phí Bảo Hiểm</h3>
    
    <div v-if="isLoading" class="flex justify-center py-4">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
    </div>

    <div v-else-if="calcResult" class="space-y-4">
      <div class="bg-white p-4 rounded-lg border border-blue-100 shadow-sm">
        <div class="flex justify-between items-center mb-2">
          <span class="text-sm text-gray-600 font-medium">Xác suất rủi ro (AI dự báo):</span>
          <span class="font-bold text-red-600">{{ calcResult.risk_score.toFixed(1) }}%</span>
        </div>
        <div class="flex justify-between items-center mb-2">
          <span class="text-sm text-gray-600 font-medium">Hệ số điều chỉnh rủi ro:</span>
          <span class="font-bold text-orange-500">x{{ calcResult.breakdown.risk_multiplier.toFixed(2) }}</span>
        </div>
        <div class="flex justify-between items-center mb-2">
          <span class="text-sm text-gray-600 font-medium">Thời hạn bảo vệ:</span>
          <span class="font-bold text-gray-900">{{ calcResult.duration_days }} Ngày</span>
        </div>
        <div class="flex justify-between items-center pt-2 border-t border-gray-100">
          <span class="text-sm text-gray-600 font-medium">Mức đền bù tối đa:</span>
          <span class="font-bold text-green-600">{{ calcResult.payout_amount }} SC</span>
        </div>
      </div>

      <div class="flex items-center justify-between bg-blue-600 text-white p-4 rounded-lg shadow-inner">
        <span class="font-bold">Phí Bảo Hiểm:</span>
        <span class="text-2xl font-extrabold">{{ calcResult.premium }} SC</span>
      </div>

      <div v-if="error" class="text-red-600 text-sm bg-red-50 p-3 rounded text-center">
        {{ error }}
      </div>

      <button 
        @click="handlePurchase" 
        :disabled="isPurchasing"
        class="w-full bg-green-500 hover:bg-green-600 text-white font-bold py-3 px-4 rounded-lg transition-colors disabled:opacity-50 mt-2"
      >
        {{ isPurchasing ? 'Đang xử lý giao dịch...' : 'Xác Nhận Mua & Trừ Tiền Ví' }}
      </button>
    </div>

    <div v-else class="text-center text-gray-500 py-4 text-sm">
      Vui lòng điền thông tin và bấm "Tính Toán Phí Bảo Hiểm" để xem kết quả AI.
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import policyService from '../../services/policyService'
import { useWalletStore } from '../../stores/wallet'

const props = defineProps({
  productId: {
    type: String,
    required: true
  },
  formData: {
    type: Object,
    default: null
  }
})

const router = useRouter()
const walletStore = useWalletStore()

const isLoading = ref(false)
const isPurchasing = ref(false)
const calcResult = ref(null)
const error = ref(null)
const currentPayload = ref(null)

// Method này sẽ được component cha gọi khi form submit
const calculate = async (durationDays, params) => {
  isLoading.value = true
  error.value = null
  try {
    currentPayload.value = {
      product_id: props.productId,
      duration_days: parseInt(durationDays),
      parameters: params
    }
    const result = await policyService.calculatePremium(currentPayload.value)
    calcResult.value = result
  } catch (err) {
    error.value = err.response?.data?.detail || 'Lỗi khi tính toán phí'
  } finally {
    isLoading.value = false
  }
}

const handlePurchase = async () => {
  isPurchasing.value = true
  error.value = null
  try {
    await policyService.purchasePolicy(currentPayload.value)
    
    // Cập nhật lại ví
    if (walletStore.fetchBalance) await walletStore.fetchBalance()
    
    alert('Mua bảo hiểm thành công!')
    router.push('/my-policies') // Chuyển hướng sang trang quản lý hợp đồng
  } catch (err) {
    error.value = err.response?.data?.detail || 'Lỗi giao dịch. Bạn đã xác thực KYC và đủ tiền trong ví chưa?'
  } finally {
    isPurchasing.value = false
  }
}

// Bộc lộ hàm calculate để component cha (InsuranceDetailView) có thể gọi
defineExpose({ calculate })
</script>