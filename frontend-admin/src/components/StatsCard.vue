<template>
  <div :class="['rounded-xl border p-5 shadow-sm', bgClass]">
    <div class="flex items-center justify-between">
      <div>
        <p class="text-sm font-medium text-gray-500">{{ label }}</p>
        <h3 class="text-2xl font-black mt-1" :class="valueClass">
          {{ formattedValue }}
        </h3>
      </div>
      <div :class="['w-12 h-12 rounded-full flex items-center justify-center text-2xl', iconBg]">
        {{ icon }}
      </div>
    </div>
    <p v-if="subtext" class="text-xs text-gray-400 mt-2">{{ subtext }}</p>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  label: String,
  value: [Number, String],
  icon: { type: String, default: '📊' },
  format: { type: String, default: 'number' }, // number, currency, percent
  bgClass: { type: String, default: 'bg-white border-gray-200' },
  valueClass: { type: String, default: 'text-gray-900' },
  iconBg: { type: String, default: 'bg-gray-100' },
  subtext: { type: String, default: null },
})

const formattedValue = computed(() => {
  if (props.value === null || props.value === undefined) return '—'
  if (props.format === 'currency') return `${Number(props.value).toLocaleString('vi-VN')} SC`
  if (props.format === 'percent') return `${(Number(props.value) * 100).toFixed(1)}%`
  return Number(props.value).toLocaleString('vi-VN')
})
</script>
