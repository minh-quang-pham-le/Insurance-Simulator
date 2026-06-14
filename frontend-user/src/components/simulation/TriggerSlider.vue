<template>
  <div class="mb-6 last:mb-0">
    <!-- Label row -->
    <div class="flex justify-between items-center mb-2.5">
      <div class="flex items-center gap-2">
        <label class="text-sm font-semibold text-gray-800">{{ slider.label }}</label>
        <span v-if="isTriggered" class="text-xs font-bold text-rose-600 bg-rose-100 rounded-full px-2 py-0.5 flex items-center gap-1">
          <span class="w-1.5 h-1.5 rounded-full bg-rose-500 animate-pulse"></span>
          Triggered
        </span>
      </div>
      <span class="text-sm font-bold tabular-nums px-2.5 py-1 rounded-lg transition-all" :class="valueColorClass">
        {{ displayValue }}<span v-if="unitSuffix" class="font-normal ml-0.5 text-xs">{{ unitSuffix }}</span>
      </span>
    </div>

    <!-- Toggle (Yes/No) -->
    <div v-if="slider.unit === 'toggle'" class="grid grid-cols-2 gap-2">
      <button
        @click="$emit('update:modelValue', 0)"
        :class="['py-2.5 rounded-xl text-sm font-semibold transition-all border-2', modelValue === 0
          ? 'bg-emerald-500 text-white border-emerald-500 shadow-sm shadow-emerald-100'
          : 'bg-gray-50 text-gray-400 border-gray-200 hover:border-gray-300']"
      >
        No
      </button>
      <button
        @click="$emit('update:modelValue', 1)"
        :class="['py-2.5 rounded-xl text-sm font-semibold transition-all border-2', modelValue === 1
          ? 'bg-rose-500 text-white border-rose-500 shadow-sm shadow-rose-100'
          : 'bg-gray-50 text-gray-400 border-gray-200 hover:border-gray-300']"
      >
        Yes
      </button>
    </div>

    <!-- Direction toggle -->
    <div v-else-if="slider.unit === 'direction'" class="grid grid-cols-2 gap-2">
      <button
        v-for="opt in (slider.options || [{value:0,label:'Above threshold'},{value:1,label:'Below threshold'}])"
        :key="opt.value"
        @click="$emit('update:modelValue', opt.value)"
        :class="['py-2.5 rounded-xl text-sm font-semibold transition-all border-2', modelValue === opt.value
          ? 'bg-violet-600 text-white border-violet-600 shadow-sm shadow-violet-100'
          : 'bg-gray-50 text-gray-400 border-gray-200 hover:border-gray-300']"
      >
        {{ opt.label }}
      </button>
    </div>

    <!-- Numeric slider -->
    <div v-else>
      <!-- Track container -->
      <div class="relative" style="height: 40px; margin: 2px 0;">
        <!-- Zone background (vertically centered) -->
        <div class="absolute inset-x-0 rounded-full overflow-hidden" style="height: 12px; top: 50%; transform: translateY(-50%);">
          <div class="h-full flex">
            <div class="h-full bg-emerald-300" :style="{ width: greenWidth + '%' }"></div>
            <div v-if="slider.threshold != null" class="h-full bg-amber-300" :style="{ width: yellowWidth + '%' }"></div>
            <div class="h-full flex-1" :class="isTriggered ? 'bg-rose-400' : 'bg-rose-300'"></div>
          </div>
        </div>

        <!-- Threshold marker line -->
        <div v-if="effectiveThreshold != null"
             class="absolute pointer-events-none top-0 bottom-0 z-10"
             :style="{ left: thresholdPercent + '%' }">
          <div class="absolute top-0 bottom-0 w-0.5 bg-gray-700/70 left-0"></div>
        </div>

        <!-- Range input (invisible but interactive) -->
        <input
          type="range"
          :min="slider.min_value"
          :max="slider.max_value"
          :step="slider.step"
          :value="modelValue"
          @input="$emit('update:modelValue', parseFloat($event.target.value))"
          class="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-20"
        />

        <!-- Custom visible thumb -->
        <div
          class="absolute pointer-events-none z-10 w-5 h-5 rounded-full border-2 border-white shadow-md transition-colors"
          :class="thumbBgClass"
          :style="{ left: valuePercent + '%', top: '50%', transform: 'translate(-50%, -50%)' }"
        ></div>
      </div>

      <!-- Scale and threshold label row -->
      <div class="flex justify-between items-center text-xs mt-0.5">
        <span class="text-gray-400">{{ slider.min_value }}{{ unitSuffix }}</span>
        <span v-if="effectiveThreshold != null" class="text-gray-600 font-semibold flex items-center gap-1">
          <span>⚡</span>Trigger at {{ effectiveThreshold }}{{ unitSuffix }}
        </span>
        <span class="text-gray-400">{{ slider.max_value }}{{ unitSuffix }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  slider: { type: Object, required: true },
  modelValue: { type: Number, required: true },
  isTriggered: { type: Boolean, default: false },
  dynamicThreshold: { type: Number, default: null },
})

defineEmits(['update:modelValue'])

// dynamicThreshold overrides the static threshold baked into slider config
// (used when threshold is itself a user-controlled slider, e.g. Crop Weather)
const effectiveThreshold = computed(() =>
  props.dynamicThreshold !== null && props.dynamicThreshold !== undefined
    ? props.dynamicThreshold
    : props.slider.threshold
)

const unitSuffix = computed(() => {
  const u = props.slider.unit
  if (!u || u === 'toggle' || u === 'direction') return ''
  return ` ${u}`
})

const range = computed(() => props.slider.max_value - props.slider.min_value)

const thresholdPercent = computed(() => {
  if (effectiveThreshold.value == null || range.value === 0) return 50
  return ((effectiveThreshold.value - props.slider.min_value) / range.value) * 100
})

const greenWidth = computed(() => {
  if (effectiveThreshold.value == null) return 100
  return thresholdPercent.value * 0.8
})

const yellowWidth = computed(() => {
  if (effectiveThreshold.value == null) return 0
  return thresholdPercent.value * 0.2
})

const valuePercent = computed(() => {
  if (range.value === 0) return 0
  return ((props.modelValue - props.slider.min_value) / range.value) * 100
})

const isNearThreshold = computed(() => {
  if (effectiveThreshold.value == null) return false
  return valuePercent.value >= thresholdPercent.value * 0.8 && valuePercent.value < thresholdPercent.value
})

const isAboveThreshold = computed(() => {
  if (effectiveThreshold.value == null) return false
  return valuePercent.value >= thresholdPercent.value
})

const thumbBgClass = computed(() => {
  if (props.slider.unit === 'toggle') return 'bg-gray-400'
  if (props.slider.unit === 'direction') return 'bg-violet-600'
  if (props.slider.threshold == null) return 'bg-violet-600'
  if (isAboveThreshold.value) return 'bg-rose-600'
  if (isNearThreshold.value) return 'bg-amber-500'
  return 'bg-emerald-500'
})

const valueColorClass = computed(() => {
  if (props.slider.unit === 'toggle') {
    return props.modelValue === 1 ? 'text-rose-700 bg-rose-50' : 'text-emerald-700 bg-emerald-50'
  }
  if (props.slider.unit === 'direction') return 'text-violet-700 bg-violet-50'
  if (props.slider.threshold == null) return 'text-gray-700 bg-gray-100'
  if (isAboveThreshold.value) return 'text-rose-700 bg-rose-50'
  if (isNearThreshold.value) return 'text-amber-700 bg-amber-50'
  return 'text-emerald-700 bg-emerald-50'
})

const displayValue = computed(() => {
  if (props.slider.unit === 'toggle') return props.modelValue === 1 ? 'Yes' : 'No'
  if (props.slider.unit === 'direction') {
    const opts = props.slider.options || []
    const match = opts.find(o => o.value === props.modelValue)
    return match ? match.label : (props.modelValue === 0 ? 'Above' : 'Below')
  }
  return Number.isInteger(props.modelValue) ? props.modelValue : props.modelValue.toFixed(1)
})
</script>
