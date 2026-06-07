<template>
  <div
    class="group relative bg-white rounded-2xl overflow-hidden border border-slate-200 hover:border-blue-300 hover:shadow-xl transition-all duration-300 hover:-translate-y-1 flex flex-col"
  >
    <!-- Category color bar -->
    <div class="h-1.5 w-full" :class="categoryGradient"></div>

    <div class="p-6 flex flex-col flex-grow">
      <!-- Header row -->
      <div class="flex items-start justify-between mb-4">
        <div class="flex items-center gap-3">
          <div
            class="w-10 h-10 rounded-xl flex items-center justify-center text-xl flex-shrink-0"
            :class="categoryBg"
          >
            {{ categoryIcon }}
          </div>
          <span class="text-xs font-semibold px-2.5 py-1 rounded-full" :class="categoryChip">
            {{ categoryLabel }}
          </span>
        </div>

        <!-- Risk score badge -->
        <div v-if="product.risk_score" class="flex flex-col items-center min-w-[36px]">
          <span class="text-[11px] text-slate-400 leading-none mb-0.5">Rủi ro</span>
          <span class="text-sm font-bold tabular-nums leading-none" :class="riskColor">
            {{ product.risk_score }}/10
          </span>
        </div>
      </div>

      <!-- Title -->
      <h3
        class="text-base font-bold text-slate-900 leading-snug mb-2 group-hover:text-blue-700 transition-colors"
      >
        {{ product.name }}
      </h3>

      <!-- Description -->
      <p class="text-slate-500 text-sm leading-relaxed flex-grow mb-5">
        {{ product.short_description || product.description.substring(0, 110) + '…' }}
      </p>

      <!-- Stats row -->
      <div
        class="flex items-center justify-between py-3 px-4 bg-slate-50 rounded-xl mb-5 border border-slate-100"
      >
        <div>
          <div class="text-[11px] text-slate-400 mb-0.5">Bồi thường tối đa</div>
          <div class="text-lg font-extrabold text-blue-700 tabular-nums leading-none">
            {{ product.base_payout.toLocaleString() }}
            <span class="text-sm font-semibold text-blue-400">SC</span>
          </div>
        </div>
        <div class="text-right">
          <div class="text-[11px] text-slate-400 mb-0.5">Thời hạn</div>
          <div class="text-sm font-semibold text-slate-700 leading-none">
            {{ product.min_duration_days }}–{{ product.max_duration_days }} ngày
          </div>
        </div>
      </div>

      <!-- CTA button -->
      <router-link
        :to="`/insurance/${product.id}`"
        class="block w-full text-center bg-blue-600 hover:bg-blue-700 active:scale-95 text-white font-semibold py-2.5 px-4 rounded-xl transition-all duration-150 text-sm"
      >
        Khám phá &amp; Mua ngay →
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  product: { type: Object, required: true },
})

const CATEGORY_MAP = {
  FLIGHT_DELAY: {
    icon: '✈️',
    label: 'Trễ Chuyến Bay',
    gradient: 'bg-gradient-to-r from-blue-500 to-blue-400',
    bg: 'bg-blue-50',
    chip: 'bg-blue-100 text-blue-700',
  },
  CROP_WEATHER: {
    icon: '🌾',
    label: 'Thời Tiết',
    gradient: 'bg-gradient-to-r from-emerald-500 to-teal-400',
    bg: 'bg-emerald-50',
    chip: 'bg-emerald-100 text-emerald-700',
  },
}

const config = computed(
  () =>
    CATEGORY_MAP[props.product.category] ?? {
      icon: '🛡️',
      label: props.product.category,
      gradient: 'bg-gradient-to-r from-slate-400 to-slate-300',
      bg: 'bg-slate-50',
      chip: 'bg-slate-100 text-slate-600',
    },
)

const categoryIcon     = computed(() => config.value.icon)
const categoryLabel    = computed(() => config.value.label)
const categoryGradient = computed(() => config.value.gradient)
const categoryBg       = computed(() => config.value.bg)
const categoryChip     = computed(() => config.value.chip)

const riskColor = computed(() => {
  const s = props.product.risk_score
  if (!s) return 'text-slate-400'
  if (s <= 3) return 'text-emerald-600'
  if (s <= 6) return 'text-amber-600'
  return 'text-red-600'
})
</script>
