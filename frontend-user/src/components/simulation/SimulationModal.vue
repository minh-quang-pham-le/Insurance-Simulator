<template>
  <Teleport to="body">
    <div class="fixed inset-0 z-50 flex items-center justify-center p-4">
      <!-- Backdrop -->
      <div class="absolute inset-0 bg-black/60 backdrop-blur-sm" @click="$emit('close')"></div>

      <!-- Modal -->
      <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-hidden flex flex-col">

        <!-- Header -->
        <div class="bg-gradient-to-br from-violet-700 via-indigo-700 to-blue-700 text-white px-6 pt-5 pb-4 shrink-0">
          <div class="flex items-start justify-between gap-4">
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2 mb-0.5">
                <span class="text-xl">⚡</span>
                <h2 class="text-base font-bold">Trigger Simulator</h2>
                <!-- Live checking badge -->
                <span v-if="isLive" class="flex items-center gap-1 text-xs bg-white/20 rounded-full px-2 py-0.5">
                  <span class="w-1.5 h-1.5 rounded-full bg-white animate-pulse"></span>
                  Simulating...
                </span>
              </div>
              <p class="text-indigo-200 text-sm font-semibold truncate">{{ productName }}</p>
              <p class="text-indigo-300 text-xs mt-1.5 leading-relaxed">
                Drag the sliders to simulate real-world conditions — see exactly when your policy would pay out.
              </p>
            </div>
            <button @click="$emit('close')" class="hover:bg-white/20 rounded-xl p-2 transition shrink-0 -mr-1">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        <!-- Body -->
        <div class="flex-1 overflow-y-auto px-6 py-5">

          <!-- Loading -->
          <div v-if="loading" class="flex flex-col items-center justify-center py-14 gap-3">
            <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-violet-600"></div>
            <p class="text-sm text-gray-400">Loading simulation...</p>
          </div>

          <!-- Error -->
          <div v-else-if="error" class="text-center py-10">
            <div class="text-4xl mb-3">😞</div>
            <p class="text-red-500 font-medium text-sm">{{ error }}</p>
            <button @click="loadConfig" class="mt-3 px-4 py-2 bg-red-50 text-red-600 rounded-xl text-sm font-medium hover:bg-red-100 transition">
              Try again
            </button>
          </div>

          <!-- Manual claim -->
          <div v-else-if="config?.is_manual" class="text-center py-10">
            <div class="text-5xl mb-3">📱</div>
            <h3 class="text-lg font-bold text-gray-800 mb-2">Manual Claim Product</h3>
            <p class="text-gray-500 text-sm max-w-sm mx-auto mb-5 leading-relaxed">
              {{ config.manual_info?.description }}
            </p>
            <div class="bg-gradient-to-r from-emerald-50 to-teal-50 border border-emerald-200 rounded-2xl p-5 inline-block">
              <p class="text-xs text-gray-500 uppercase tracking-wider mb-1">Base Payout</p>
              <p class="text-3xl font-black text-emerald-600 tabular-nums">
                {{ config.base_payout?.toLocaleString() }} <span class="text-xl font-bold text-emerald-400">SC</span>
              </p>
            </div>
          </div>

          <!-- Sliders + Result -->
          <div v-else-if="config">
            <!-- How-it-works hint -->
            <div class="flex items-start gap-2.5 mb-5 p-3.5 bg-violet-50 rounded-xl border border-violet-100">
              <span class="text-violet-500 mt-0.5 shrink-0">💡</span>
              <p class="text-xs text-violet-700 leading-relaxed">
                <strong>How it works:</strong> Set slider values to match a scenario (e.g. a storm with 120mm rainfall).
                The simulator instantly checks if those conditions would trigger your insurance payout.
              </p>
            </div>

            <!-- Weather product: per-metric cards -->
            <template v-if="isWeatherProduct">
              <div class="space-y-3">
                <div
                  v-for="slider in conditionSliders"
                  :key="slider.name"
                  class="border-2 rounded-xl p-4 transition-colors"
                  :class="isSliderTriggered(slider.name) ? 'border-rose-300 bg-rose-50/40' : 'border-gray-200 bg-white'"
                >
                  <!-- Card header -->
                  <div class="flex items-center justify-between mb-3">
                    <span class="text-sm font-bold text-gray-700">{{ slider.label }}</span>
                    <span v-if="isSliderTriggered(slider.name)" class="text-xs font-bold text-rose-600 flex items-center gap-1">
                      <span class="w-1.5 h-1.5 rounded-full bg-rose-500 animate-pulse"></span>Triggered
                    </span>
                  </div>

                  <!-- Simulate: slider with dynamic zones -->
                  <div class="mb-3">
                    <div class="flex justify-between items-center mb-1.5">
                      <span class="text-xs text-gray-400">Simulate</span>
                      <span class="text-sm font-bold tabular-nums transition-colors" :class="metricValueColorClass(slider)">
                        {{ sliderValues[slider.name] }} {{ slider.unit }}
                      </span>
                    </div>
                    <div class="relative" style="height: 40px;">
                      <!-- Zone track -->
                      <div class="absolute inset-x-0 rounded-full overflow-hidden" style="height: 12px; top: 50%; transform: translateY(-50%);">
                        <div class="h-full flex">
                          <div class="h-full transition-colors" :class="metricLeftZoneClass(slider)"
                               :style="{ width: metricThresholdPercent(slider) + '%' }"></div>
                          <div class="h-full flex-1 transition-colors" :class="metricRightZoneClass(slider)"></div>
                        </div>
                      </div>
                      <!-- Threshold marker -->
                      <div class="absolute top-0 bottom-0 w-0.5 bg-gray-700/60 z-10 pointer-events-none"
                           :style="{ left: metricThresholdPercent(slider) + '%' }"></div>
                      <!-- Range input (invisible) -->
                      <input type="range"
                        :min="slider.min_value" :max="slider.max_value" :step="slider.step"
                        :value="sliderValues[slider.name]"
                        @input="sliderValues[slider.name] = parseFloat($event.target.value) || 0"
                        class="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-20"
                      />
                      <!-- Custom thumb -->
                      <div class="absolute pointer-events-none z-10 w-5 h-5 rounded-full border-2 border-white shadow-md transition-colors"
                           :class="metricThumbClass(slider)"
                           :style="{ left: metricValuePercent(slider) + '%', top: '50%', transform: 'translate(-50%, -50%)' }">
                      </div>
                    </div>
                    <div class="flex justify-between text-xs text-gray-300 mt-0.5">
                      <span>{{ slider.min_value }}</span>
                      <span>{{ slider.max_value }}</span>
                    </div>
                  </div>

                  <!-- Trigger: direction buttons + threshold number input -->
                  <div class="flex items-center gap-2 pt-2.5 border-t border-gray-100">
                    <span class="text-xs text-gray-400 shrink-0">Trigger</span>
                    <button
                      @click="sliderValues[`${slider.name}_dir`] = 0"
                      :class="['px-2.5 py-1.5 rounded-lg text-xs font-semibold border-2 transition-all shrink-0',
                        getMetricDir(slider.name) === 0
                          ? 'bg-rose-500 text-white border-rose-500'
                          : 'text-gray-400 border-gray-200 hover:border-rose-300 hover:text-rose-500']"
                    >↑ Above</button>
                    <button
                      @click="sliderValues[`${slider.name}_dir`] = 1"
                      :class="['px-2.5 py-1.5 rounded-lg text-xs font-semibold border-2 transition-all shrink-0',
                        getMetricDir(slider.name) === 1
                          ? 'bg-blue-500 text-white border-blue-500'
                          : 'text-gray-400 border-gray-200 hover:border-blue-300 hover:text-blue-500']"
                    >↓ Below</button>
                    <div class="flex items-center flex-1 border-2 border-violet-200 rounded-xl overflow-hidden focus-within:border-violet-500 bg-white transition-colors">
                      <input
                        type="number"
                        :value="getMetricThreshold(slider.name)"
                        @input="sliderValues[`${slider.name}_threshold`] = parseFloat($event.target.value) || 0"
                        min="0" :max="slider.max_value" :step="slider.step"
                        class="flex-1 px-3 py-1.5 text-sm font-bold text-violet-700 text-right tabular-nums focus:outline-none min-w-0"
                      />
                      <span class="px-2.5 text-xs text-violet-400 font-medium shrink-0 border-l border-violet-100">{{ slider.unit }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </template>

            <!-- Other products: flat list -->
            <template v-else>
              <TriggerSlider
                v-for="slider in config.sliders"
                :key="slider.name"
                :slider="slider"
                :isTriggered="isSliderTriggered(slider.name)"
                v-model="sliderValues[slider.name]"
              />
            </template>

            <!-- Result panel -->
            <TriggerResult
              :triggered="triggerResult?.triggered || false"
              :checked="hasChecked"
              :payoutAmount="triggerResult?.payout_amount || 0"
              :payoutMultiplier="triggerResult?.payout_multiplier || 1.0"
              :triggeredRules="triggerResult?.triggered_rules || []"
              :allRules="config.trigger_rules || []"
            />
          </div>
        </div>

        <!-- Footer -->
        <div v-if="config && !config.is_manual" class="border-t border-gray-100 px-6 py-3 bg-gray-50 shrink-0 flex justify-between items-center">
          <button @click="resetSliders" class="flex items-center gap-1.5 text-sm text-gray-400 hover:text-gray-600 transition">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Reset
          </button>
          <button
            @click="checkTrigger"
            :disabled="isLive"
            class="flex items-center gap-2 px-5 py-2 bg-violet-600 text-white rounded-xl font-semibold text-sm hover:bg-violet-700 disabled:opacity-60 transition"
          >
            <span v-if="isLive" class="w-3.5 h-3.5 rounded-full border-2 border-white/40 border-t-white animate-spin"></span>
            <span>{{ isLive ? 'Simulating...' : 'Run Simulation' }}</span>
          </button>
        </div>

      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import simulationService from '../../services/simulationService'
import TriggerSlider from './TriggerSlider.vue'
import TriggerResult from './TriggerResult.vue'

const props = defineProps({
  productId: { type: String, required: true },
  productName: { type: String, default: '' },
})

defineEmits(['close'])

const loading = ref(true)
const error = ref(null)
const config = ref(null)
const sliderValues = reactive({})
const triggerResult = ref(null)
const hasChecked = ref(false)
const checking = ref(false)
const pendingCheck = ref(false)

const isLive = computed(() => checking.value || pendingCheck.value)

// Detect Crop Weather style: has a user-controlled "threshold" slider
const isWeatherProduct = computed(() =>
  config.value?.sliders.some(s => s.name === 'threshold') ?? false
)

const POLICY_SLIDER_NAMES = ['threshold', 'comparison']

const conditionSliders = computed(() =>
  config.value?.sliders.filter(s => !POLICY_SLIDER_NAMES.includes(s.name)) ?? []
)

function getMetricDir(sliderName) {
  return sliderValues[`${sliderName}_dir`] ?? 0
}

function getMetricThreshold(sliderName) {
  return sliderValues[`${sliderName}_threshold`] ?? 50
}

function metricThresholdPercent(slider) {
  const th = getMetricThreshold(slider.name)
  const range = slider.max_value - slider.min_value
  if (range === 0) return 50
  return Math.min(100, Math.max(0, ((th - slider.min_value) / range) * 100))
}

function metricValuePercent(slider) {
  const range = slider.max_value - slider.min_value
  if (range === 0) return 0
  return Math.min(100, Math.max(0, ((sliderValues[slider.name] - slider.min_value) / range) * 100))
}

// Zone colors flip based on direction: Above → left=safe, right=danger; Below → left=danger, right=safe
function metricLeftZoneClass(slider) {
  return getMetricDir(slider.name) === 1 ? 'bg-rose-300' : 'bg-emerald-300'
}

function metricRightZoneClass(slider) {
  return getMetricDir(slider.name) === 0 ? 'bg-rose-300' : 'bg-emerald-300'
}

function metricThumbClass(slider) {
  const vp = metricValuePercent(slider)
  const tp = metricThresholdPercent(slider)
  const isAbove = getMetricDir(slider.name) === 0
  if (isAbove) {
    if (vp >= tp) return 'bg-rose-600'
    if (vp >= tp * 0.8) return 'bg-amber-500'
    return 'bg-emerald-500'
  } else {
    if (vp <= tp) return 'bg-rose-600'
    if (vp <= tp * 1.25) return 'bg-amber-500'
    return 'bg-emerald-500'
  }
}

function metricValueColorClass(slider) {
  const vp = metricValuePercent(slider)
  const tp = metricThresholdPercent(slider)
  const isAbove = getMetricDir(slider.name) === 0
  if (isAbove) {
    if (vp >= tp) return 'text-rose-600'
    if (vp >= tp * 0.8) return 'text-amber-600'
    return 'text-emerald-600'
  } else {
    if (vp <= tp) return 'text-rose-600'
    if (vp <= tp * 1.25) return 'text-amber-600'
    return 'text-emerald-600'
  }
}

onMounted(() => {
  loadConfig()
})

async function loadConfig() {
  loading.value = true
  error.value = null
  try {
    const { data } = await simulationService.getConfig(props.productId)
    config.value = data
    const globalThresholdDefault = data.sliders.find(s => s.name === 'threshold')?.default_value ?? 50
    for (const slider of data.sliders || []) {
      sliderValues[slider.name] = slider.default_value
      if (!POLICY_SLIDER_NAMES.includes(slider.name)) {
        sliderValues[`${slider.name}_dir`] = 0
        sliderValues[`${slider.name}_threshold`] = globalThresholdDefault
      }
    }
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to load simulation config'
  } finally {
    loading.value = false
  }
}

function resetSliders() {
  if (!config.value) return
  const globalThresholdDefault = config.value.sliders.find(s => s.name === 'threshold')?.default_value ?? 50
  for (const slider of config.value.sliders || []) {
    sliderValues[slider.name] = slider.default_value
    if (!POLICY_SLIDER_NAMES.includes(slider.name)) {
      sliderValues[`${slider.name}_dir`] = 0
      sliderValues[`${slider.name}_threshold`] = globalThresholdDefault
    }
  }
  triggerResult.value = null
  hasChecked.value = false
}

async function checkTrigger() {
  checking.value = true
  pendingCheck.value = false
  try {
    const { data } = await simulationService.checkTrigger(props.productId, { ...sliderValues })
    triggerResult.value = data
    hasChecked.value = true
    simulationService.logSession(props.productId, { ...sliderValues }, data).catch(() => {})
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to check trigger'
  } finally {
    checking.value = false
  }
}

function isSliderTriggered(sliderName) {
  if (!triggerResult.value?.triggered_rules) return false
  return triggerResult.value.triggered_rules.some(tr => tr.field === sliderName)
}

// Auto-check on slider change (debounced)
let debounceTimer = null
watch(sliderValues, () => {
  if (!config.value || config.value.is_manual) return
  pendingCheck.value = true
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    checkTrigger()
  }, 300)
}, { deep: true })
</script>
