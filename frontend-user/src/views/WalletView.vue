<template>
  <div class="min-h-screen bg-slate-50">
    <div class="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">

      <div class="mb-6">
        <h1 class="text-2xl font-extrabold text-slate-900 tracking-tight">Ví SimCoin</h1>
        <p class="text-slate-500 text-sm mt-0.5">Quản lý số dư và lịch sử giao dịch của bạn.</p>
      </div>

      <!-- Balance card -->
      <BalanceCard class="mb-6" />

      <!-- Top-up section -->
      <div class="bg-white rounded-2xl border border-slate-200 p-6 mb-6">
        <h2 class="text-base font-bold text-slate-900 mb-4 flex items-center gap-2">
          <span
            class="w-6 h-6 bg-blue-100 rounded-lg flex items-center justify-center text-blue-600 text-sm font-bold"
          >+</span>
          Nạp tiền
        </h2>
        <TopUpForm @topup-success="handleTopUpSuccess" />
      </div>

      <!-- Transaction history -->
      <div class="bg-white rounded-2xl border border-slate-200 p-6">
        <h2 class="text-base font-bold text-slate-900 mb-4 flex items-center gap-2">
          <span
            class="w-6 h-6 bg-slate-100 rounded-lg flex items-center justify-center text-slate-500 text-sm"
          >≡</span>
          Lịch sử giao dịch
        </h2>
        <TransactionList />
      </div>

      <!-- Error banner -->
      <div
        v-if="error"
        class="mt-4 bg-red-50 border border-red-100 text-red-600 p-4 rounded-xl flex justify-between items-center text-sm"
      >
        <span>{{ error }}</span>
        <button @click="walletStore.clearError" class="font-bold hover:text-red-800 ml-4">✕</button>
      </div>

    </div>
  </div>
</template>

<script setup>
import { onMounted, computed } from 'vue'
import { useWalletStore } from '@/stores/wallet'
import BalanceCard from '@/components/BalanceCard.vue'
import TopUpForm from '@/components/TopUpForm.vue'
import TransactionList from '@/components/TransactionList.vue'

const walletStore = useWalletStore()
const error = computed(() => walletStore.error)

onMounted(async () => {
  await walletStore.fetchBalance()
  await walletStore.fetchTransactions()
})

const handleTopUpSuccess = async () => {}
</script>
