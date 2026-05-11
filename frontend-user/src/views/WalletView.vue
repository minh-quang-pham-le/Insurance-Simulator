<template>
  <div class="wallet-container">
    <!-- Balance Card -->
    <BalanceCard v-if="!loading" />

    <!-- Top-up Section -->
    <div class="topup-section">
      <h2>Top-up Wallet</h2>
      <TopUpForm @topup-success="handleTopUpSuccess" />
    </div>

    <!-- Transaction History -->
    <div class="transactions-section">
      <h2>Transaction History</h2>
      <TransactionList />
    </div>

    <!-- Loading -->
    <div v-if="loading" class="loading">
      <p>Loading wallet data...</p>
    </div>

    <!-- Error -->
    <div v-if="error" class="error-alert">
      <p>{{ error }}</p>
      <button @click="walletStore.clearError">Dismiss</button>
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

const loading = computed(() => walletStore.loading)
const error = computed(() => walletStore.error)

onMounted(async () => {
  await walletStore.fetchBalance()
  await walletStore.fetchTransactions()
})

const handleTopUpSuccess = async () => {
  // Transactions are refreshed automatically after top-up
  // Just wait a moment and then could show a success message
}
</script>

<style scoped>
.wallet-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 20px;
}

.topup-section,
.transactions-section {
  background: white;
  border-radius: 8px;
  padding: 20px;
  margin-top: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

h2 {
  font-size: 18px;
  margin-top: 0;
  color: #333;
}

.loading,
.error-alert {
  text-align: center;
  padding: 20px;
  margin-top: 20px;
  border-radius: 8px;
}

.loading {
  background: #f0f0f0;
  color: #666;
}

.error-alert {
  background: #fee;
  color: #c33;
  border: 1px solid #fcc;
}

.error-alert button {
  margin-top: 10px;
  padding: 8px 16px;
  background: #c33;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.error-alert button:hover {
  background: #a22;
}
</style>
