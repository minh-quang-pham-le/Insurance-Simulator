<template>
  <Transition name="result-pop">
    <div v-if="triggered" class="mt-4 bg-red-50 border-2 border-red-300 rounded-xl p-5 text-center animate-pulse-once">
      <div class="text-4xl mb-2">🚨</div>
      <h3 class="text-xl font-bold text-red-700 mb-1">Insurance Activated!</h3>
      <p class="text-red-600 text-sm mb-3">
        Your policy would trigger a payout based on current conditions.
      </p>
      <div class="bg-white rounded-lg p-3 inline-block shadow-sm">
        <p class="text-xs text-gray-500 uppercase tracking-wider">Payout Amount</p>
        <p class="text-2xl font-bold text-green-600">{{ payoutAmount.toLocaleString() }} SC</p>
        <p v-if="payoutMultiplier !== 1.0" class="text-xs text-gray-500">
          x{{ payoutMultiplier }} multiplier applied
        </p>
      </div>
      <div v-if="triggeredRules.length > 0" class="mt-3 space-y-1">
        <p v-for="(rule, i) in triggeredRules" :key="i" class="text-xs text-red-500">
          {{ rule.description }}
        </p>
      </div>
    </div>
  </Transition>

  <div v-if="!triggered && checked" class="mt-4 bg-green-50 border border-green-200 rounded-xl p-4 text-center">
    <div class="text-3xl mb-1">✅</div>
    <p class="text-green-700 font-medium text-sm">Safe — No trigger conditions met</p>
    <p class="text-green-600 text-xs mt-1">Adjust the sliders to explore different scenarios.</p>
  </div>
</template>

<script setup>
defineProps({
  triggered: { type: Boolean, default: false },
  checked: { type: Boolean, default: false },
  payoutAmount: { type: Number, default: 0 },
  payoutMultiplier: { type: Number, default: 0 },
  triggeredRules: { type: Array, default: () => [] },
})
</script>

<style scoped>
.result-pop-enter-active {
  animation: pop-in 0.4s ease;
}
.result-pop-leave-active {
  animation: pop-in 0.2s ease reverse;
}
@keyframes pop-in {
  0% { transform: scale(0.8); opacity: 0; }
  60% { transform: scale(1.05); }
  100% { transform: scale(1); opacity: 1; }
}
.animate-pulse-once {
  animation: pulse-highlight 1s ease;
}
@keyframes pulse-highlight {
  0%, 100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
  50% { box-shadow: 0 0 0 8px rgba(239, 68, 68, 0.15); }
}
</style>
