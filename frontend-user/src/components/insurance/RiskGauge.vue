<template>
  <div class="flex flex-col gap-1">
    <div class="flex justify-between items-center text-sm">
      <span class="font-medium text-gray-700">Mức độ rủi ro:</span>
      <span :class="['font-bold', riskColorClass]">{{ riskLabel }} ({{ score }}/10)</span>
    </div>
    
    <div class="w-full bg-gray-200 rounded-full h-2.5 overflow-hidden">
      <div 
        class="h-2.5 rounded-full transition-all duration-500 ease-out"
        :class="riskBgClass"
        :style="{ width: `${(score / 10) * 100}%` }"
      ></div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  score: {
    type: Number,
    required: true,
    default: 1.0
  }
})

// Logic chia mức độ rủi ro theo SPEC
const riskLevel = computed(() => {
  if (props.score <= 3.9) return 'LOW'
  if (props.score <= 6.9) return 'MODERATE'
  return 'HIGH'
})

const riskLabel = computed(() => {
  const labels = {
    'LOW': 'Thấp',
    'MODERATE': 'Trung bình',
    'HIGH': 'Cao'
  }
  return labels[riskLevel.value]
})

const riskColorClass = computed(() => {
  const classes = {
    'LOW': 'text-green-600',
    'MODERATE': 'text-yellow-600',
    'HIGH': 'text-red-600'
  }
  return classes[riskLevel.value]
})

const riskBgClass = computed(() => {
  const classes = {
    'LOW': 'bg-green-500',
    'MODERATE': 'bg-yellow-500',
    'HIGH': 'bg-red-500'
  }
  return classes[riskLevel.value]
})
</script>