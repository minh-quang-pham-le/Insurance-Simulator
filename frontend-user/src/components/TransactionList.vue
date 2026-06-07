<template>
  <div>
    <!-- Loading -->
    <div v-if="loading" class="py-8 text-center">
      <div
        class="animate-spin rounded-full h-8 w-8 border-4 border-blue-100 border-t-blue-600 mx-auto mb-2"
      ></div>
      <p class="text-slate-400 text-sm">Đang tải giao dịch...</p>
    </div>

    <!-- Empty -->
    <div v-else-if="transactions.length === 0" class="py-10 text-center">
      <div class="text-4xl mb-3">📋</div>
      <p class="text-slate-500 text-sm">Chưa có giao dịch nào. Hãy nạp tiền để bắt đầu!</p>
    </div>

    <!-- List -->
    <div v-else class="space-y-2">
      <div
        v-for="tx in transactions"
        :key="tx.id"
        class="flex items-center justify-between p-4 rounded-xl border border-slate-100 hover:border-slate-200 hover:bg-slate-50 transition-all"
      >
        <!-- Icon + info -->
        <div class="flex items-center gap-3">
          <div
            class="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0 text-base"
            :class="txIconBg(tx.type)"
          >
            {{ txIcon(tx.type) }}
          </div>
          <div>
            <p class="text-sm font-semibold text-slate-800">
              {{ formatTransactionType(tx.type) }}
            </p>
            <p class="text-xs text-slate-400 mt-0.5">{{ formatDate(tx.created_at) }}</p>
          </div>
        </div>

        <!-- Amount + balance -->
        <div class="text-right">
          <p
            class="text-sm font-bold tabular-nums"
            :class="isCredit(tx.type) ? 'text-emerald-600' : 'text-red-500'"
          >
            {{ isCredit(tx.type) ? '+' : '−' }}{{ tx.amount.toLocaleString('vi-VN') }} SC
          </p>
          <p class="text-xs text-slate-400 tabular-nums mt-0.5">
            Còn: {{ tx.balance_after.toLocaleString('vi-VN') }} SC
          </p>
        </div>
      </div>
    </div>

    <!-- Pagination -->
    <div
      v-if="pagination.total > pagination.limit"
      class="flex items-center justify-between pt-4 mt-2 border-t border-slate-100"
    >
      <button
        @click="goToPreviousPage"
        :disabled="pagination.skip === 0 || loading"
        class="text-sm text-slate-600 hover:text-blue-700 font-medium disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
      >
        ← Trước
      </button>
      <span class="text-xs text-slate-400">
        {{ pagination.skip + 1 }}–{{ Math.min(pagination.skip + pagination.limit, pagination.total) }}
        / {{ pagination.total }}
      </span>
      <button
        @click="goToNextPage"
        :disabled="pagination.skip + pagination.limit >= pagination.total || loading"
        class="text-sm text-slate-600 hover:text-blue-700 font-medium disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
      >
        Tiếp →
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useWalletStore } from '@/stores/wallet'

const walletStore = useWalletStore()

const transactions = computed(() => walletStore.transactions)
const loading      = computed(() => walletStore.loading)
const pagination   = computed(() => walletStore.pagination)

const CREDIT_TYPES = ['TOP_UP', 'CLAIM_PAYOUT', 'CREDIT', 'REFUND']

const isCredit = (type) => CREDIT_TYPES.includes(type)

const TX_CONFIG = {
  TOP_UP:       { icon: '💰', bg: 'bg-emerald-50' },
  PURCHASE:     { icon: '🛡️', bg: 'bg-blue-50'    },
  CLAIM_PAYOUT: { icon: '💵', bg: 'bg-emerald-50' },
  REFUND:       { icon: '↩️', bg: 'bg-amber-50'   },
  CREDIT:       { icon: '✨', bg: 'bg-emerald-50' },
  DEDUCT:       { icon: '➖', bg: 'bg-red-50'      },
}

const txIcon   = (type) => TX_CONFIG[type]?.icon ?? '💳'
const txIconBg = (type) => TX_CONFIG[type]?.bg   ?? 'bg-slate-50'

const formatDate = (dateString) =>
  new Date(dateString).toLocaleString('vi-VN', {
    day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  })

const formatTransactionType = (type) => {
  const map = {
    TOP_UP:       'Nạp tiền',
    PURCHASE:     'Mua bảo hiểm',
    CLAIM_PAYOUT: 'Bồi thường',
    REFUND:       'Hoàn tiền',
    CREDIT:       'Cộng tiền',
    DEDUCT:       'Trừ tiền',
  }
  return map[type] || type
}

const goToPreviousPage = async () => {
  const newSkip = Math.max(0, pagination.value.skip - pagination.value.limit)
  await walletStore.fetchTransactions(newSkip, pagination.value.limit)
}

const goToNextPage = async () => {
  const newSkip = pagination.value.skip + pagination.value.limit
  await walletStore.fetchTransactions(newSkip, pagination.value.limit)
}
</script>
