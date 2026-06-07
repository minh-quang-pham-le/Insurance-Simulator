<template>
  <div class="min-h-screen bg-slate-50">
    <!-- Loading -->
    <div v-if="insuranceStore.isLoading" class="flex justify-center items-center py-32">
      <div class="animate-spin rounded-full h-12 w-12 border-4 border-blue-100 border-t-blue-600"></div>
    </div>

    <div v-else-if="product">
      <!-- Product hero header -->
      <div :class="heroBg" class="py-10 px-4">
        <div class="max-w-4xl mx-auto">
          <router-link
            to="/insurance"
            class="inline-flex items-center gap-1.5 text-sm text-white/70 hover:text-white mb-5 transition-colors"
          >
            ← Quay lại danh sách
          </router-link>

          <div class="flex items-center gap-4 mb-4">
            <div
              class="w-14 h-14 bg-white/20 backdrop-blur-sm rounded-2xl flex items-center justify-center text-3xl flex-shrink-0 border border-white/30"
            >
              {{ catConfig.icon }}
            </div>
            <div>
              <div class="text-white/70 text-xs font-semibold uppercase tracking-widest mb-1">
                {{ catConfig.label }}
              </div>
              <h1 class="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
                {{ product.name }}
              </h1>
            </div>
          </div>

          <p class="text-white/80 text-sm leading-relaxed max-w-xl mb-6">
            {{ product.description }}
          </p>

          <!-- Key stat pills -->
          <div class="flex flex-wrap gap-3">
            <div
              class="bg-white/15 backdrop-blur-sm border border-white/20 rounded-xl px-4 py-2.5 text-white"
            >
              <div class="text-[11px] text-white/60 mb-0.5">Bồi thường tối đa</div>
              <div class="text-lg font-extrabold tabular-nums leading-none">
                {{ product.base_payout.toLocaleString() }}
                <span class="text-sm font-semibold text-white/70">SC</span>
              </div>
            </div>
            <div
              class="bg-white/15 backdrop-blur-sm border border-white/20 rounded-xl px-4 py-2.5 text-white"
            >
              <div class="text-[11px] text-white/60 mb-0.5">Thời hạn</div>
              <div class="text-lg font-extrabold leading-none">
                {{ product.min_duration_days }}–{{ product.max_duration_days }} ngày
              </div>
            </div>
            <div
              class="bg-white/15 backdrop-blur-sm border border-white/20 rounded-xl px-4 py-2.5 text-white"
            >
              <div class="text-[11px] text-white/60 mb-0.5">Kiểu bồi thường</div>
              <div class="text-lg font-extrabold leading-none">Tự động</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Main content -->
      <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">

          <!-- Left: Info cards -->
          <div class="lg:col-span-2 space-y-5">

            <!-- Simulation card -->
            <div class="bg-gradient-to-br from-blue-600 to-indigo-700 rounded-2xl p-6 text-white">
              <div class="flex items-start justify-between gap-4">
                <div>
                  <div
                    class="text-blue-200 text-[11px] font-bold uppercase tracking-widest mb-1.5"
                  >
                    Tính năng tương tác
                  </div>
                  <h3 class="text-xl font-bold mb-2">Mô Phỏng Rủi Ro</h3>
                  <p class="text-blue-100 text-sm leading-relaxed max-w-xs">
                    Kéo thử các ngưỡng và xem điều kiện bảo hiểm kích hoạt như thế nào trên dữ liệu thực.
                  </p>
                </div>
                <span class="text-5xl flex-shrink-0 mt-1">🔮</span>
              </div>
              <button
                @click="showSimulation = true"
                class="mt-5 bg-white text-blue-700 hover:bg-blue-50 active:scale-95 font-bold px-5 py-2.5 rounded-xl text-sm transition-all"
              >
                Thử Mô Phỏng →
              </button>
            </div>

            <!-- How it works -->
            <div class="bg-white rounded-2xl border border-slate-200 p-6">
              <h3 class="font-bold text-slate-900 mb-4 flex items-center gap-2">
                <span
                  class="w-6 h-6 bg-blue-100 rounded-lg flex items-center justify-center text-blue-600 text-xs font-bold"
                >?</span>
                Cách hoạt động
              </h3>
              <div class="space-y-4">
                <div v-for="(step, i) in howItWorks" :key="i" class="flex gap-3">
                  <div
                    class="w-6 h-6 rounded-full bg-blue-600 text-white font-bold text-xs flex items-center justify-center flex-shrink-0 mt-0.5"
                  >
                    {{ i + 1 }}
                  </div>
                  <p class="text-slate-600 text-sm leading-relaxed">{{ step }}</p>
                </div>
              </div>
            </div>

            <!-- Trust anchors -->
            <div class="grid grid-cols-3 gap-3">
              <div
                v-for="anchor in trustAnchors"
                :key="anchor.text"
                class="bg-white rounded-xl border border-slate-200 p-3 text-center"
              >
                <div class="text-2xl mb-1.5">{{ anchor.icon }}</div>
                <div class="text-xs font-semibold text-slate-700 leading-snug">{{ anchor.text }}</div>
              </div>
            </div>
          </div>

          <!-- Right: Sticky purchase form -->
          <div class="lg:col-span-1">
            <div class="bg-white rounded-2xl shadow-lg border border-slate-200 p-6 sticky top-6">
              <div class="flex items-center gap-2 mb-5 pb-4 border-b border-slate-100">
                <span class="w-2 h-2 bg-emerald-400 rounded-full animate-pulse"></span>
                <h2 class="text-base font-bold text-slate-900">Tính phí &amp; Mua bảo hiểm</h2>
              </div>

              <DynamicForm
                :schema="product.parameters_schema"
                @submit="handleCalculatePremium"
              />
              <PremiumCalculator ref="calculatorRef" :productId="product.id" />
            </div>
          </div>

        </div>
      </div>
    </div>

    <!-- Chat Widget -->
    <ChatWidget v-if="product" :productId="route.params.id" />

    <!-- Simulation Modal -->
    <SimulationModal
      v-if="showSimulation && product"
      :productId="route.params.id"
      :productName="product.name"
      @close="showSimulation = false"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { useInsuranceStore } from '../stores/insurance'
import DynamicForm from '../components/insurance/DynamicForm.vue'
import PremiumCalculator from '../components/insurance/PremiumCalculator.vue'
import ChatWidget from '../components/chat/ChatWidget.vue'
import SimulationModal from '../components/simulation/SimulationModal.vue'

const route = useRoute()
const insuranceStore = useInsuranceStore()

const product = computed(() => insuranceStore.currentProduct)
const calculatorRef = ref(null)
const showSimulation = ref(false)

const CATEGORY_MAP = {
  FLIGHT_DELAY: { icon: '✈️', label: 'Trễ Chuyến Bay', hero: 'bg-gradient-to-r from-blue-800 to-blue-600' },
  CROP_WEATHER: { icon: '🌾', label: 'Thời Tiết',       hero: 'bg-gradient-to-r from-emerald-800 to-teal-600' },
}

const catConfig = computed(() => {
  if (!product.value) return { icon: '🛡️', label: '', hero: 'bg-gradient-to-r from-slate-700 to-slate-500' }
  return (
    CATEGORY_MAP[product.value.category] ?? {
      icon: '🛡️',
      label: product.value.category,
      hero: 'bg-gradient-to-r from-slate-700 to-slate-500',
    }
  )
})

const heroBg = computed(() => catConfig.value.hero)

const HOW_IT_WORKS = {
  FLIGHT_DELAY: [
    'Bạn cung cấp số hiệu chuyến bay, ngày bay và ngưỡng chậm trễ mong muốn.',
    'Hệ thống theo dõi trạng thái chuyến bay liên tục qua API AviationStack.',
    'Nếu chuyến bay trễ vượt ngưỡng hoặc bị huỷ, bồi thường tự động chuyển vào ví SimCoin.',
  ],
  CROP_WEATHER: [
    'Bạn chọn địa điểm, chỉ số thời tiết cần bảo vệ và ngưỡng kích hoạt.',
    'Hệ thống kiểm tra dữ liệu OpenWeatherMap mỗi 6 giờ tại tọa độ của bạn.',
    'Khi chỉ số vượt ngưỡng đã thiết lập, bồi thường được phát tự động.',
  ],
}

const howItWorks = computed(() => {
  if (!product.value) return []
  return (
    HOW_IT_WORKS[product.value.category] ?? [
      'Điền thông tin hợp đồng và tính toán phí bảo hiểm.',
      'Hệ thống theo dõi điều kiện kích hoạt liên tục.',
      'Bồi thường được phát tự động khi điều kiện đáp ứng.',
    ]
  )
})

const trustAnchors = [
  { icon: '🔒', text: 'Giao dịch bảo mật' },
  { icon: '⚡', text: 'Chi trả tự động' },
  { icon: '📊', text: 'Minh bạch tham số' },
]

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
