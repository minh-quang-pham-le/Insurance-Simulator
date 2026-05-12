<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <div class="mb-8">
      <h1 class="text-3xl font-extrabold text-gray-900 tracking-tight">Khám Phá Bảo Hiểm</h1>
      <p class="mt-2 text-lg text-gray-600">Bảo vệ bạn trước những rủi ro nhỏ nhất với quy trình hoàn toàn tự động.</p>
    </div>

    <div v-if="insuranceStore.isLoading" class="flex justify-center items-center py-20">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
    </div>

    <div v-else-if="insuranceStore.error" class="bg-red-50 text-red-600 p-4 rounded-lg">
      {{ insuranceStore.error }}
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <ProductCard 
        v-for="product in insuranceStore.products" 
        :key="product.id" 
        :product="product" 
      />
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useInsuranceStore } from '../stores/insurance'
import ProductCard from '../components/insurance/ProductCard.vue'

const insuranceStore = useInsuranceStore()

onMounted(() => {
  insuranceStore.fetchProducts()
})
</script>