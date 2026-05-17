<template>
  <div class="balance-card">
    <div class="balance-header">
      <h3>Wallet Balance</h3>
      <button class="refresh-btn" @click="handleRefresh" :disabled="loading">
        ↻ Refresh
      </button>
    </div>

    <div class="balance-display">
      <div class="balance-amount">
        <span class="value">{{ balance.toFixed(2) }}</span>
        <span class="currency">{{ currency }}</span>
      </div>
      <p class="description">Simulated Currency</p>
    </div>

    <div class="balance-info">
      <p>
        <strong>Your SimCoin Balance:</strong> This is the virtual currency used to purchase insurance policies and cover claims.
      </p>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useWalletStore } from '@/stores/wallet'

const walletStore = useWalletStore()

const balance = computed(() => walletStore.balance)
const currency = computed(() => walletStore.currency)
const loading = computed(() => walletStore.loading)

const handleRefresh = async () => {
  await walletStore.fetchBalance()
}
</script>

<style scoped>
.balance-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
  margin-bottom: 20px;
}

.balance-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

h3 {
  margin: 0;
  font-size: 16px;
  opacity: 0.9;
}

.refresh-btn {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.3s ease;
}

.refresh-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.3);
}

.refresh-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.balance-display {
  text-align: center;
  margin-bottom: 20px;
}

.balance-amount {
  display: flex;
  align-items: baseline;
  justify-content: center;
  gap: 10px;
}

.value {
  font-size: 48px;
  font-weight: bold;
}

.currency {
  font-size: 24px;
  opacity: 0.9;
}

.description {
  margin: 10px 0 0 0;
  font-size: 14px;
  opacity: 0.8;
}

.balance-info {
  background: rgba(0, 0, 0, 0.1);
  padding: 15px;
  border-radius: 8px;
  font-size: 14px;
  line-height: 1.6;
}

.balance-info p {
  margin: 0;
}
</style>
