<template>
  <div class="bg-white rounded-xl shadow-md border border-gray-100 p-5 hover:shadow-lg transition-shadow flex flex-col h-full">
    <div class="flex items-start gap-4 mb-3">
      <div class="w-12 h-12 bg-blue-50 rounded-lg flex items-center justify-center text-2xl flex-shrink-0">
        {{ getCategoryIcon(product.category) }}
      </div>
      <div>
        <h3 class="text-lg font-bold text-gray-900 leading-tight">{{ product.name }}</h3>
        <span class="inline-block px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded mt-1 font-medium">
          {{ formatCategory(product.category) }}
        </span>
      </div>
    </div>

    <p class="text-gray-600 text-sm mb-5 flex-grow">
      {{ product.short_description || product.description.substring(0, 100) + '...' }}
    </p>

    <div class="bg-blue-50/50 p-3 rounded-lg mb-5 border border-blue-100">
      <div class="text-sm text-gray-600">Mức bồi thường cơ bản</div>
      <div class="text-xl font-bold text-blue-700">{{ product.base_payout }} SC</div>
    </div>

    <div class="mb-6">
      <RiskGauge :score="product.risk_score || 5.0" />
    </div>

    <router-link 
      :to="`/insurance/${product.id}`"
      class="mt-auto block w-full text-center bg-gray-900 hover:bg-blue-700 text-white font-semibold py-2.5 px-4 rounded-lg transition-colors"
    >
      Xem Chi Tiết
    </router-link>
  </div>
</template>

<script setup>
import RiskGauge from './RiskGauge.vue'

defineProps({
  product: {
    type: Object,
    required: true
  }
})

// Helper maps
const getCategoryIcon = (category) => {
  const icons = {
    'FLIGHT_DELAY': '✈️',
    'CROP_WEATHER': '🌾',
    'GADGET': '📱',
    'NATURAL_DISASTER': '🌪️',
    'RAINFALL_EVENT': '☔'
  }
  return icons[category] || '🛡️'
}

const formatCategory = (category) => {
  const names = {
    'FLIGHT_DELAY': 'Trễ Chuyến Bay',
    'CROP_WEATHER': 'Thời Tiết Nông Nghiệp',
    'GADGET': 'Thiết Bị Điện Tử',
    'NATURAL_DISASTER': 'Thiên Tai',
    'RAINFALL_EVENT': 'Sự Kiện Ngoài Trời'
  }
  return names[category] || category
}
</script>