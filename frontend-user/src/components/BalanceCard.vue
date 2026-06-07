<template>
  <div
    class="bg-gradient-to-br from-blue-700 to-blue-900 rounded-2xl p-6 text-white shadow-lg relative overflow-hidden"
  >
    <div class="relative z-10">
      <div class="flex items-center justify-between mb-4">
        <p class="text-blue-200 text-xs font-semibold uppercase tracking-wider">Số dư khả dụng</p>
        <button
          @click="handleRefresh"
          :disabled="loading"
          class="bg-white/15 hover:bg-white/25 border border-white/20 text-white px-3 py-1.5 rounded-lg text-xs font-medium transition-all disabled:opacity-40"
        >
          ↻ Làm mới
        </button>
      </div>
      <div class="flex items-baseline gap-2 mb-1">
        <span class="text-5xl font-black tabular-nums">
          {{ loading ? '···' : balance.toLocaleString('vi-VN') }}
        </span>
        <span class="text-2xl font-bold text-blue-200">SC</span>
      </div>
      <p class="text-blue-300 text-xs mt-1">SimCoin — Đồng tiền mô phỏng</p>
    </div>
    <div class="absolute -right-4 -bottom-4 text-[7rem] opacity-10 select-none">🪙</div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useWalletStore } from '@/stores/wallet'

const walletStore = useWalletStore()

const balance = computed(() => walletStore.balance)
const loading = computed(() => walletStore.loading)

const handleRefresh = async () => {
  await walletStore.fetchBalance()
}
</script>
