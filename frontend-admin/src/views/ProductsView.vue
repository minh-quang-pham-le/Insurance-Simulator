<template>
  <div class="px-8 py-8">

    <!-- Page header -->
    <div class="flex items-center justify-between mb-8">
      <div>
        <h1 class="text-2xl font-extrabold text-slate-900 tracking-tight">Sản phẩm bảo hiểm</h1>
        <p class="text-slate-500 text-sm mt-0.5">Quản lý danh mục sản phẩm và tham số rủi ro.</p>
      </div>
      <router-link
        to="/products/new"
        class="inline-flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 active:scale-95 text-white px-4 py-2.5 rounded-xl text-sm font-semibold transition-all"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4"/>
        </svg>
        Thêm sản phẩm
      </router-link>
    </div>

    <!-- Loading -->
    <div v-if="store.isLoading" class="flex items-center justify-center py-24">
      <svg class="animate-spin w-8 h-8 text-indigo-600" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
        <path stroke-linecap="round" d="M12 3a9 9 0 1 0 9 9"/>
      </svg>
    </div>

    <!-- Error -->
    <div v-else-if="store.error" class="bg-red-50 border border-red-100 text-red-600 p-4 rounded-2xl text-sm flex items-center gap-2">
      <svg class="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v4m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/>
      </svg>
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
