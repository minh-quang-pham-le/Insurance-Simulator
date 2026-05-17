<template>
  <Teleport to="body">
    <div class="fixed inset-0 z-50 flex items-center justify-center p-4">
      <!-- Backdrop -->
      <div class="absolute inset-0 bg-black/50 backdrop-blur-sm" @click="$emit('close')"></div>

      <!-- Modal -->
      <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-hidden flex flex-col">
        <!-- Header -->
        <div class="bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-6 py-4 flex items-center justify-between shrink-0">
          <div>
            <h2 class="text-lg font-bold">Trigger Explorer</h2>
            <p class="text-blue-200 text-sm">{{ productName }}</p>
          </div>
          <button @click="$emit('close')" class="hover:bg-white/20 rounded-lg p-1.5 transition">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Body -->
        <div class="flex-1 overflow-y-auto px-6 py-5">
          <!-- Loading -->
          <div v-if="loading" class="flex justify-center py-12">
            <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600"></div>
          </div>

          <!-- Error -->
          <div v-else-if="error" class="text-center py-8 text-red-500">
            <p>{{ error }}</p>
            <button @click="loadConfig" class="mt-3 text-blue-600 underline text-sm">Retry</button>
          </div>

          <!-- Manual claim info -->
          <div v-else-if="config?.is_manual" class="text-center py-8">
            <div class="text-5xl mb-3">📱</div>
            <h3 class="text-lg font-bold text-gray-800 mb-2">Manual Claim Product</h3>
            <p class="text-gray-600 text-sm max-w-sm mx-auto">
              {{ config.manual_info?.description }}
            </p>
            <div class="mt-4 bg-gray-50 rounded-lg p-4 inline-block">
              <p class="text-xs text-gray-500 uppercase tracking-wider">Base Payout</p>
              <p class="text-xl font-bold text-green-600">{{ config.base_payout }} SC</p>
            </div>
          </div>

          <!-- Sliders -->
          <div v-else-if="config">
            <p class="text-sm text-gray-500 mb-5">
              Adjust the sliders below to explore different scenarios and see when your insurance would activate.
            </p>

            <!-- Trigger rules summary -->
            <div class="bg-gray-50 rounded-lg p-3 mb-5">
              <p class="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">Trigger Conditions</p>
              <div v-for="(rule, i) in config.trigger_rules" :key="i" class="flex items-center gap-2 text-sm text-gray-700 py-0.5">
                <span class="w-1.5 h-1.5 rounded-full" :class="isRuleTriggered(rule) ? 'bg-red-500' : 'bg-gray-300'"></span>
                <span :class="isRuleTriggered(rule) ? 'text-red-600 font-medium' : ''">{{ rule.description }}</span>
              </div>
            </div>

            <TriggerSlider
              v-for="slider in config.sliders"
              :key="slider.name"
              :slider="slider"
              v-model="sliderValues[slider.name]"
            />

            <TriggerResult
              :triggered="triggerResult?.triggered || false"
              :checked="hasChecked"
              :payoutAmount="triggerResult?.payout_amount || 0"
              :payoutMultiplier="triggerResult?.payout_multiplier || 1.0"
              :triggeredRules="triggerResult?.triggered_rules || []"
            />
          </div>
        </div>

        <!-- Footer -->
        <div v-if="config && !config.is_manual" class="border-t border-gray-100 px-6 py-3 bg-gray-50 shrink-0 flex justify-between items-center">
          <button @click="resetSliders" class="text-sm text-gray-500 hover:text-gray-700 transition">
            Reset values
          </button>
          <button
            @click="checkTrigger"
            :disabled="checking"
            class="px-5 py-2 bg-blue-600 text-white rounded-lg font-medium text-sm hover:bg-blue-700 disabled:opacity-50 transition"
          >
            {{ checking ? 'Checking...' : 'Check Trigger' }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
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

onMounted(() => {
  loadConfig()
})

async function loadConfig() {
  loading.value = true
  error.value = null
  try {
    const { data } = await simulationService.getConfig(props.productId)
    config.value = data
    // Initialize slider values to defaults
    for (const slider of data.sliders || []) {
      sliderValues[slider.name] = slider.default_value
    }
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to load simulation config'
  } finally {
    loading.value = false
  }
}

function resetSliders() {
  if (!config.value) return
  for (const slider of config.value.sliders || []) {
    sliderValues[slider.name] = slider.default_value
  }
  triggerResult.value = null
  hasChecked.value = false
}

async function checkTrigger() {
  checking.value = true
  try {
    const { data } = await simulationService.checkTrigger(props.productId, { ...sliderValues })
    triggerResult.value = data
    hasChecked.value = true

    // Log session if triggered
    if (data.triggered) {
      simulationService.logSession(props.productId, { ...sliderValues }, data).catch(() => {})
    }
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to check trigger'
  } finally {
    checking.value = false
  }
}

// Auto-check when sliders change (debounced)
let debounceTimer = null
watch(sliderValues, () => {
  if (!config.value || config.value.is_manual) return
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    checkTrigger()
  }, 300)
}, { deep: true })

function isRuleTriggered(rule) {
  if (!triggerResult.value?.triggered_rules) return false
  return triggerResult.value.triggered_rules.some(tr => tr.field === rule.field)
}
</script>
