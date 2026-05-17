<template>
  <div class="p-6">
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-bold text-gray-900">Quản Lý Sản Phẩm Bảo Hiểm</h1>
      <router-link 
        to="/products/new" 
        class="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
      >
        + Thêm Sản Phẩm Mới
      </router-link>
    </div>

    <div v-if="store.isLoading" class="py-10 text-center">
      <div class="animate-spin inline-block w-8 h-8 border-4 border-indigo-600 border-t-transparent rounded-full"></div>
    </div>
    
    <div v-else-if="store.error" class="bg-red-50 text-red-600 p-4 rounded-lg">
      {{ store.error }}
    </div>

    <ProductTable 
      v-else 
      :products="store.products" 
      @toggle-status="store.toggleProductStatus" 
    />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useAdminInsuranceStore } from '../stores/insurance'
import ProductTable from '../components/products/ProductTable.vue'

const store = useAdminInsuranceStore()

onMounted(() => {
  store.fetchProducts()
})
</script>