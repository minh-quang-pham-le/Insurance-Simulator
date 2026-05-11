<template>
  <div class="topup-form">
    <!-- KYC Status Check -->
    <div v-if="!kycVerified" class="kyc-warning">
      <p>⚠️ <strong>KYC Verification Required</strong></p>
      <p>You must complete KYC verification before you can top up your wallet.</p>
      <router-link to="/kyc" class="btn-link">Complete KYC Verification</router-link>
    </div>

    <!-- Top-up Form -->
    <div v-else class="form-group">
      <label for="amount">Amount (SimCoin)</label>
      <div class="input-row">
        <input
          id="amount"
          v-model.number="amount"
          type="number"
          placeholder="Enter amount"
          min="1"
          max="100000"
          :disabled="loading"
        />
        <button
          @click="handleTopUp"
          :disabled="!amount || amount <= 0 || loading"
          class="btn-topup"
        >
          {{ loading ? 'Processing...' : 'Top Up' }}
        </button>
      </div>

      <div v-if="error" class="error-message">
        {{ error }}
      </div>

      <div v-if="successMessage" class="success-message">
        {{ successMessage }}
      </div>

      <!-- Preset Amounts -->
      <div class="preset-amounts">
        <p>Quick amounts:</p>
        <button
          v-for="preset in presetAmounts"
          :key="preset"
          @click="setAmount(preset)"
          :disabled="loading"
          class="preset-btn"
        >
          +{{ preset }}
        </button>
      </div>

      <!-- Info -->
      <div class="info-box">
        <p>
          <strong>Available for top-up:</strong> Unlimited • <strong>Min amount:</strong> 1 SC •
          <strong>Max amount:</strong> 100,000 SC
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useWalletStore } from '@/stores/wallet'
import { useAuthStore } from '@/stores/auth'

const walletStore = useWalletStore()
const authStore = useAuthStore()

const emit = defineEmits(['topup-success'])

// Form state
const amount = ref('')
const loading = computed(() => walletStore.loading)
const error = computed(() => walletStore.error)
const successMessage = ref('')

const presetAmounts = [100, 500, 1000, 5000]

// KYC check
const kycVerified = computed(() => {
  return authStore.user?.kyc_status === 'VERIFIED'
})

const setAmount = (value) => {
  amount.value = amount.value ? amount.value + value : value
}

const handleTopUp = async () => {
  if (!amount.value || amount.value <= 0) {
    return
  }

  successMessage.value = ''

  try {
    await walletStore.topUp(amount.value)
    successMessage.value = `Successfully topped up ${amount.value} SC!`
    amount.value = ''
    emit('topup-success')

    // Clear success message after 3 seconds
    setTimeout(() => {
      successMessage.value = ''
    }, 3000)
  } catch (err) {
    // Error is handled by walletStore
  }
}

onMounted(async () => {
  // Ensure we have current user info for KYC check
  if (!authStore.user) {
    await authStore.fetchUser()
  }
})
</script>

<style scoped>
.topup-form {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.kyc-warning {
  background: #fef3cd;
  border: 1px solid #ffc107;
  border-radius: 8px;
  padding: 15px;
  color: #856404;
}

.kyc-warning p {
  margin: 8px 0;
}

.kyc-warning strong {
  color: #c33;
}

.btn-link {
  display: inline-block;
  margin-top: 10px;
  padding: 8px 16px;
  background: #ffc107;
  color: #333;
  text-decoration: none;
  border-radius: 4px;
  font-weight: 500;
  transition: background 0.3s;
}

.btn-link:hover {
  background: #ffb800;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

label {
  font-weight: 600;
  color: #333;
}

.input-row {
  display: flex;
  gap: 10px;
}

input {
  flex: 1;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
}

input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

input:disabled {
  background: #f5f5f5;
  cursor: not-allowed;
}

.btn-topup {
  padding: 10px 24px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.3s;
}

.btn-topup:hover:not(:disabled) {
  background: #5568d3;
}

.btn-topup:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.error-message {
  background: #fee;
  border: 1px solid #fcc;
  color: #c33;
  padding: 10px;
  border-radius: 4px;
  font-size: 14px;
}

.success-message {
  background: #efe;
  border: 1px solid #cfc;
  color: #3c3;
  padding: 10px;
  border-radius: 4px;
  font-size: 14px;
}

.preset-amounts {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.preset-amounts p {
  margin: 0;
  font-size: 14px;
  color: #666;
}

.preset-btn {
  padding: 6px 12px;
  background: #f0f0f0;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.3s;
}

.preset-btn:hover:not(:disabled) {
  background: #e0e0e0;
  border-color: #667eea;
}

.preset-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.info-box {
  background: #f9f9f9;
  border-left: 3px solid #667eea;
  padding: 10px;
  border-radius: 4px;
  font-size: 13px;
  color: #666;
}

.info-box p {
  margin: 0;
}
</style>
