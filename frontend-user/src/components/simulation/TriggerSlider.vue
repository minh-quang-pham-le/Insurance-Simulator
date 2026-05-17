<template>
  <div class="mb-5">
    <div class="flex justify-between items-center mb-1.5">
      <label class="text-sm font-medium text-gray-700">{{ slider.label }}</label>
      <span class="text-sm font-bold" :class="valueColor">
        {{ displayValue }}{{ slider.unit && slider.unit !== 'toggle' && slider.unit !== 'status' ? ` ${slider.unit}` : '' }}
      </span>
    </div>

    <!-- Toggle for boolean fields (Yes/No) -->
    <div v-if="slider.unit === 'toggle'" class="flex items-center gap-3">
      <button
        @click="$emit('update:modelValue', 0)"
        :class="['px-3 py-1.5 rounded-lg text-sm font-medium transition',
          modelValue === 0 ? 'bg-green-100 text-green-700 ring-2 ring-green-500' : 'bg-gray-100 text-gray-500']"
      >
        No
      </button>
      <button
        @click="$emit('update:modelValue', 1)"
        :class="['px-3 py-1.5 rounded-lg text-sm font-medium transition',
          modelValue === 1 ? 'bg-red-100 text-red-700 ring-2 ring-red-500' : 'bg-gray-100 text-gray-500']"
      >
        Yes
      </button>
    </div>

    <!-- Direction toggle (Above/Below for Crop Weather) -->
    <div v-else-if="slider.unit === 'direction'" class="flex items-center gap-3">
      <button
        v-for="opt in (slider.options || [{value:0,label:'Above'},{value:1,label:'Below'}])"
        :key="opt.value"
        @click="$emit('update:modelValue', opt.value)"
        :class="['px-3 py-1.5 rounded-lg text-sm font-medium transition',
          modelValue === opt.value ? 'bg-blue-100 text-blue-700 ring-2 ring-blue-500' : 'bg-gray-100 text-gray-500']"
      >
        {{ opt.label }}
      </button>
    </div>

    <!-- Slider for numeric fields -->
    <div v-else>
      <div class="relative h-2 bg-gray-200 rounded-full overflow-hidden">
        <!-- Green zone -->
        <div
          class="absolute h-full bg-green-400 rounded-full"
          :style="{ width: greenWidth + '%' }"
        ></div>
        <!-- Yellow zone -->
        <div
          v-if="slider.threshold != null"
          class="absolute h-full bg-yellow-400"
          :style="{ left: greenWidth + '%', width: yellowWidth + '%' }"
        ></div>
        <!-- Red zone -->
        <div
          v-if="slider.threshold != null"
          class="absolute h-full bg-red-400 rounded-r-full"
          :style="{ left: (greenWidth + yellowWidth) + '%', width: redWidth + '%' }"
        ></div>
      </div>

      <!-- Threshold marker -->
      <div v-if="slider.threshold != null" class="relative h-0">
        <div
          class="absolute -top-4 w-0.5 h-4 bg-gray-700"
          :style="{ left: thresholdPercent + '%' }"
        ></div>
      </div>

      <input
        type="range"
        :min="slider.min_value"
        :max="slider.max_value"
        :step="slider.step"
        :value="modelValue"
        @input="$emit('update:modelValue', parseFloat($event.target.value))"
        class="w-full mt-1 accent-blue-600 cursor-pointer"
      />

      <div class="flex justify-between text-xs text-gray-400 mt-0.5">
        <span>{{ slider.min_value }}</span>
        <span v-if="slider.threshold != null" class="text-gray-600 font-medium">
          Threshold: {{ slider.threshold }}
        </span>
        <span>{{ slider.max_value }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  slider: { type: Object, required: true },
  modelValue: { type: Number, required: true },
})

defineEmits(['update:modelValue'])

const range = computed(() => props.slider.max_value - props.slider.min_value)

const thresholdPercent = computed(() => {
  if (props.slider.threshold == null || range.value === 0) return 50
  return ((props.slider.threshold - props.slider.min_value) / range.value) * 100
})

// Green: 0 to 80% of threshold
const greenWidth = computed(() => {
  if (props.slider.threshold == null) return 100
  return thresholdPercent.value * 0.8
})

// Yellow: 80% to 100% of threshold
const yellowWidth = computed(() => {
  if (props.slider.threshold == null) return 0
  return thresholdPercent.value * 0.2
})

// Red: threshold to max
const redWidth = computed(() => {
  if (props.slider.threshold == null) return 0
  return 100 - thresholdPercent.value
})

const valuePercent = computed(() => {
  if (range.value === 0) return 0
  return ((props.modelValue - props.slider.min_value) / range.value) * 100
})

const valueColor = computed(() => {
  if (props.slider.unit === 'toggle') {
    return props.modelValue === 1 ? 'text-red-600' : 'text-green-600'
  }
  if (props.slider.unit === 'direction') return 'text-blue-600'
  if (props.slider.threshold == null) return 'text-gray-700'
  if (valuePercent.value >= thresholdPercent.value) return 'text-red-600'
  if (valuePercent.value >= thresholdPercent.value * 0.8) return 'text-yellow-600'
  return 'text-green-600'
})

const displayValue = computed(() => {
  if (props.slider.unit === 'toggle') {
    return props.modelValue === 1 ? 'YES' : 'NO'
  }
  if (props.slider.unit === 'direction') {
    const opts = props.slider.options || []
    const match = opts.find(o => o.value === props.modelValue)
    return match ? match.label : (props.modelValue === 0 ? 'Above' : 'Below')
  }
  return Number.isInteger(props.modelValue) ? props.modelValue : props.modelValue.toFixed(1)
})
</script>
