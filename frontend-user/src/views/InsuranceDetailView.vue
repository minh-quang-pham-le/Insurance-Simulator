<template>
  <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <div v-if="insuranceStore.isLoading" class="flex justify-center items-center py-20">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
    </div>

    <div v-else-if="product" class="grid grid-cols-1 lg:grid-cols-3 gap-8">
      
      <div class="lg:col-span-2 space-y-6">
        <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h1 class="text-2xl font-bold text-gray-900 mb-2">{{ product.name }}</h1>
          <p class="text-gray-600 mb-6">{{ product.description }}</p>
          
          <div class="bg-gray-50 rounded-lg p-5 border border-gray-100">
            <h3 class="text-sm font-semibold text-gray-700 uppercase tracking-wider mb-4">Đánh Giá Rủi Ro Chuyên Sâu</h3>
            <RiskGauge :score="product.risk_score" />
            <p class="text-xs text-gray-500 mt-3">
              * Điểm số được AI tính toán dựa trên dữ liệu lịch sử các sự kiện tương tự.
            </p>
          </div>
        </div>

        <div class="bg-blue-50 border border-blue-100 rounded-xl p-6 flex flex-col items-center justify-center text-center">
          <span class="text-4xl mb-2">🔮</span>
          <h3 class="font-bold text-blue-900">Mô Phỏng Rủi Ro</h3>
          <p class="text-sm text-blue-700 mb-4">Tính năng chạy mô phỏng trực quan sẽ sớm ra mắt.</p>
          <button disabled class="bg-blue-200 text-blue-500 px-4 py-2 rounded-lg font-medium cursor-not-allowed">
            Thử Mô Phỏng
          </button>
        </div>
      </div>

      <div class="lg:col-span-1">
        <div class="bg-white rounded-xl shadow-lg border border-gray-100 p-6 sticky top-6">
          <h2 class="text-lg font-bold text-gray-900 mb-4">Tham Số Hợp Đồng</h2>
          <DynamicForm 
            :schema="product.parameters_schema" 
            @submit="handleCalculatePremium" 
          />
          <PremiumCalculator ref="calculatorRef" :productId="product.id" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { useInsuranceStore } from '../stores/insurance'
import RiskGauge from '../components/insurance/RiskGauge.vue'
import DynamicForm from '../components/insurance/DynamicForm.vue'
import PremiumCalculator from '../components/insurance/PremiumCalculator.vue'

const route = useRoute()
const insuranceStore = useInsuranceStore()

const product = computed(() => insuranceStore.currentProduct)
const calculatorRef = ref(null)

onMounted(() => {
  insuranceStore.fetchProductById(route.params.id)
})

onUnmounted(() => {
  insuranceStore.clearCurrentProduct()
})

const handleCalculatePremium = (formData) => {
  const params = { ...formData }
  const duration = params.duration_days || 7 
  delete params.duration_days

  if (calculatorRef.value) {
    calculatorRef.value.calculate(duration, params)
  }
}
</script>