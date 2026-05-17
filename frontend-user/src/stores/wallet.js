import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { walletService } from '@/services/walletService'

export const useWalletStore = defineStore('wallet', () => {
  // State
  const balance = ref(0)
  const currency = ref('SC')
  const transactions = ref([])
  const loading = ref(false)
  const error = ref(null)
  const pagination = ref({
    skip: 0,
    limit: 50,
    total: 0
  })

  // Computed
  const formattedBalance = computed(() => {
    return `${balance.value.toFixed(2)} ${currency.value}`
  })

  // Actions
  const fetchBalance = async () => {
    loading.value = true
    error.value = null
    try {
      const data = await walletService.getBalance()
      balance.value = data.balance
      currency.value = data.currency
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to fetch balance'
      throw err
    } finally {
      loading.value = false
    }
  }

  const topUp = async (amount) => {
    loading.value = true
    error.value = null
    try {
      const data = await walletService.topUp(amount)
      balance.value = data.balance_after
      // Refresh transaction history
      await fetchTransactions()
      return data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Top-up failed'
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchTransactions = async (skip = 0, limit = 50) => {
    loading.value = true
    error.value = null
    try {
      const data = await walletService.getTransactions(skip, limit)
      transactions.value = data.transactions
      pagination.value = data.pagination
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to fetch transactions'
      throw err
    } finally {
      loading.value = false
    }
  }

  const clearError = () => {
    error.value = null
  }

  return {
    // State
    balance,
    currency,
    transactions,
    loading,
    error,
    pagination,

    // Computed
    formattedBalance,

    // Actions
    fetchBalance,
    topUp,
    fetchTransactions,
    clearError
  }
})
