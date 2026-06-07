<template>
  <div class="min-h-screen bg-slate-50">
    <!-- Hero banner -->
    <div class="bg-gradient-to-br from-blue-800 via-blue-700 to-blue-900 pt-12 pb-10 px-4">
      <div class="max-w-7xl mx-auto">
        <div class="max-w-2xl">
          <!-- Live pill -->
          <div
            class="inline-flex items-center gap-2 bg-white/15 backdrop-blur-sm text-white text-xs font-semibold px-3 py-1.5 rounded-full mb-5 border border-white/20"
          >
            <span class="w-2 h-2 bg-emerald-400 rounded-full animate-pulse"></span>
            Tham số hóa · Tự động chi trả · Dữ liệu API thực
          </div>

          <h1 class="text-4xl font-extrabold text-white leading-tight tracking-tight mb-3">
            Bảo Hiểm Thông Minh<br />
            <span class="text-blue-200">Cho Thời Đại Số</span>
          </h1>
          <p class="text-blue-100 text-base leading-relaxed">
            Bảo vệ bạn trước rủi ro thực tế. Chi trả tự động khi điều kiện kích hoạt —
            không cần paperwork, không cần chờ duyệt.
          </p>
        </div>

        <!-- Trust stats -->
        <div class="flex flex-wrap gap-6 mt-8 pt-8 border-t border-white/10">
          <div
            v-for="stat in trustStats"
            :key="stat.label"
            class="flex items-center gap-3 text-white"
          >
            <span class="text-2xl">{{ stat.icon }}</span>
            <div>
              <div class="text-base font-extrabold leading-none">{{ stat.value }}</div>
              <div class="text-blue-200 text-xs mt-0.5">{{ stat.label }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Product grid -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <div class="flex items-center justify-between mb-6">
        <div>
          <h2 class="text-xl font-bold text-slate-800">
            Các Gói Bảo Hiểm
            <span
              v-if="!insuranceStore.isLoading"
              class="ml-2 text-sm font-normal text-slate-400"
            >
              ({{ insuranceStore.products.length }} gói)
            </span>
          </h2>
          <p class="text-slate-500 text-sm mt-0.5">
            Chọn gói phù hợp và mua ngay — tất cả đều tự động kích hoạt.
          </p>
        </div>
      </div>

      <!-- Loading -->
      <div v-if="insuranceStore.isLoading" class="flex justify-center items-center py-24">
        <div class="animate-spin rounded-full h-12 w-12 border-4 border-blue-100 border-t-blue-600"></div>
      </div>

      <!-- Error -->
      <div
        v-else-if="insuranceStore.error"
        class="bg-red-50 text-red-600 p-4 rounded-xl border border-red-100 text-sm"
      >
        {{ insuranceStore.error }}
      </div>

      <!-- Grid -->
      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <ProductCard
          v-for="product in insuranceStore.products"
          :key="product.id"
          :product="product"
        />
      </div>

      <!-- Empty state -->
      <div
        v-if="!insuranceStore.isLoading && !insuranceStore.error && insuranceStore.products.length === 0"
        class="text-center py-16 text-slate-400"
      >
        <div class="text-5xl mb-4">🛡️</div>
        <p class="font-semibold">Chưa có sản phẩm bảo hiểm nào.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useInsuranceStore } from '../stores/insurance'
import ProductCard from '../components/insurance/ProductCard.vue'

const insuranceStore = useInsuranceStore()

const trustStats = [
  { icon: '⚡', value: 'Tự động 100%', label: 'Chi trả không cần khai báo' },
  { icon: '🛡️', value: 'Minh bạch', label: 'Tham số hóa rõ ràng' },
  { icon: '🌐', value: 'Thời gian thực', label: 'Dữ liệu từ API bên thứ ba' },
  { icon: '🪙', value: 'SimCoin', label: 'Đồng tiền mô phỏng an toàn' },
]

onMounted(() => {
  insuranceStore.fetchProducts()
})
</script>
