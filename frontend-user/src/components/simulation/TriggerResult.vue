<template>
  <!-- Not yet checked -->
  <div v-if="!checked" class="mt-6 border-2 border-dashed border-gray-200 rounded-2xl p-6 text-center">
    <div class="text-4xl mb-2">🎯</div>
    <p class="text-sm font-semibold text-gray-500">Adjust sliders to simulate a scenario</p>
    <p class="text-xs text-gray-400 mt-1">Results will appear here automatically</p>
  </div>

  <!-- TRIGGERED -->
  <Transition name="result-pop">
    <div v-if="checked && triggered" class="mt-6 rounded-2xl overflow-hidden border-2 border-rose-400 shadow-lg shadow-rose-100">
      <!-- Header band -->
      <div class="bg-gradient-to-r from-rose-500 to-orange-500 px-5 py-4 flex items-center gap-3">
        <span class="text-3xl">🚨</span>
        <div>
          <h3 class="text-lg font-extrabold text-white leading-tight">Insurance Activated!</h3>
          <p class="text-rose-100 text-xs">Trigger conditions are met in this scenario</p>
        </div>
      </div>

      <!-- Payout amount -->
      <div class="bg-white px-5 py-4">
        <p class="text-xs text-gray-500 uppercase tracking-wider text-center mb-1">Estimated payout</p>
        <div class="text-center mb-4">
          <span class="text-5xl font-black text-emerald-600 tabular-nums">{{ payoutAmount.toLocaleString() }}</span>
          <span class="text-2xl font-bold text-emerald-400 ml-2">SC</span>
          <p v-if="payoutMultiplier !== 1.0" class="text-xs text-gray-400 mt-1">
            × {{ payoutMultiplier }} multiplier applied
          </p>
        </div>

        <!-- Which rules fired -->
        <div v-if="triggeredRules.length > 0" class="space-y-2">
          <p class="text-xs font-semibold text-gray-500 uppercase tracking-wider">What triggered:</p>
          <div
            v-for="(rule, i) in triggeredRules"
            :key="i"
            class="flex items-start gap-2.5 bg-rose-50 border border-rose-200 rounded-xl px-3 py-2.5"
          >
            <span class="text-rose-500 mt-0.5 shrink-0">⚡</span>
            <span class="text-sm text-rose-700 font-medium leading-snug">{{ rule.description }}</span>
          </div>
        </div>
      </div>
    </div>
  </Transition>

  <!-- SAFE -->
  <div v-if="checked && !triggered" class="mt-6 rounded-2xl overflow-hidden border-2 border-emerald-300">
    <!-- Header band -->
    <div class="bg-gradient-to-r from-emerald-500 to-teal-500 px-5 py-4 flex items-center gap-3">
      <span class="text-3xl">✅</span>
      <div>
        <h3 class="text-base font-bold text-white leading-tight">No Trigger — Safe Zone</h3>
        <p class="text-emerald-100 text-xs">Current conditions don't meet any threshold</p>
      </div>
    </div>

    <!-- Condition checklist -->
    <div class="bg-white px-5 py-4">
      <p class="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">Conditions checked:</p>
      <div class="space-y-2">
        <div
          v-for="(rule, i) in allRules"
          :key="i"
          class="flex items-start gap-2.5 bg-emerald-50 border border-emerald-100 rounded-xl px-3 py-2.5"
        >
          <span class="text-emerald-500 mt-0.5 shrink-0 font-bold">✓</span>
          <span class="text-sm text-gray-600 leading-snug">{{ rule.description }}</span>
        </div>
      </div>
      <p class="text-xs text-gray-400 text-center mt-4">
        Try moving sliders toward the ⚡ trigger thresholds
      </p>
    </div>
  </div>
</template>

<script setup>
defineProps({
  triggered: { type: Boolean, default: false },
  checked: { type: Boolean, default: false },
  payoutAmount: { type: Number, default: 0 },
  payoutMultiplier: { type: Number, default: 1.0 },
  triggeredRules: { type: Array, default: () => [] },
  allRules: { type: Array, default: () => [] },
})
</script>

<style scoped>
.result-pop-enter-active {
  animation: pop-in 0.35s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.result-pop-leave-active {
  animation: pop-in 0.2s ease reverse;
}
@keyframes pop-in {
  0% { transform: scale(0.85) translateY(8px); opacity: 0; }
  100% { transform: scale(1) translateY(0); opacity: 1; }
}
</style>
