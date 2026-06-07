<template>
  <div>
    <!-- KYC warning -->
    <div
      v-if="!kycVerified"
      class="bg-amber-50 border border-amber-200 rounded-xl p-4 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3"
    >
      <div>
        <p class="font-bold text-amber-800 text-sm mb-0.5">⚠️ Cần xác minh KYC</p>
        <p class="text-amber-700 text-sm">Hoàn thành xác minh danh tính để nạp tiền vào ví.</p>
      </div>
      <router-link
        to="/kyc"
        class="whitespace-nowrap bg-amber-500 hover:bg-amber-600 text-white font-bold px-4 py-2 rounded-xl text-sm transition-colors"
      >
        Xác minh ngay →
      </router-link>
    </div>

    <!-- Top-up form -->
    <div v-else class="space-y-4">
      <div>
        <label class="block text-sm font-semibold text-slate-700 mb-1.5">Số lượng SimCoin</label>
        <div class="flex gap-2">
          <input
            v-model.number="amount"
            type="number"
            placeholder="Nhập số lượng..."
            min="1"
            max="100000"
            :disabled="loading"
            class="flex-1 border border-slate-200 rounded-xl px-4 py-2.5 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none disabled:bg-slate-50"
          />
          <button
            @click="handleTopUp"
            :disabled="!amount || amount <= 0 || loading"
            class="bg-blue-600 hover:bg-blue-700 active:scale-95 text-white font-bold px-5 py-2.5 rounded-xl text-sm transition-all disabled:bg-slate-300 disabled:cursor-not-allowed"
          >
            {{ loading ? '···' : 'Nạp tiền' }}
          </button>
        </div>
      </div>

      <!-- Preset amounts -->
      <div>
        <p class="text-xs text-slate-400 mb-2">Nạp nhanh:</p>
        <div class="flex flex-wrap gap-2">
          <button
            v-for="preset in presetAmounts"
            :key="preset"
            @click="setAmount(preset)"
            :disabled="loading"
            class="bg-slate-100 hover:bg-blue-50 hover:text-blue-700 hover:border-blue-200 border border-slate-200 text-slate-600 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all disabled:opacity-50"
          >
            +{{ preset.toLocaleString() }} SC
          </button>
        </div>
      </div>

      <!-- Feedback -->
      <div
        v-if="error"
        class="bg-red-50 border border-red-100 text-red-600 text-sm p-3 rounded-xl"
      >
        {{ error }}
      </div>
      <div
        v-if="successMessage"
        class="bg-emerald-50 border border-emerald-100 text-emerald-700 text-sm p-3 rounded-xl font-medium"
      >
        ✓ {{ successMessage }}
      </div>

      <p class="text-xs text-slate-400 border-t border-slate-100 pt-3">
        Giới hạn: 1 SC tối thiểu · 100,000 SC tối đa mỗi lần nạp
      </p>
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

const amount = ref('')
const loading = computed(() => walletStore.loading)
const error = computed(() => walletStore.error)
const successMessage = ref('')

const presetAmounts = [100, 500, 1000, 5000]

const kycVerified = computed(() => authStore.user?.kyc_status === 'VERIFIED')

const setAmount = (value) => {
  amount.value = amount.value ? amount.value + value : value
}

const handleTopUp = async () => {
  if (!amount.value || amount.value <= 0) return
  successMessage.value = ''
  try {
    await walletStore.topUp(amount.value)
    successMessage.value = `Nạp thành công ${amount.value.toLocaleString()} SC!`
    amount.value = ''
    emit('topup-success')
    setTimeout(() => { successMessage.value = '' }, 3000)
  } catch (err) {
    // Error handled by walletStore
  }
}

onMounted(async () => {
  if (!authStore.user) await authStore.fetchUser()
})
</script>
