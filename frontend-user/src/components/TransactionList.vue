<template>
  <div class="transaction-list">
    <div v-if="loading" class="loading">
      Loading transactions...
    </div>

    <div v-else-if="transactions.length === 0" class="empty-state">
      <p>No transactions yet. Top up your wallet to get started!</p>
    </div>

    <div v-else>
      <!-- Transactions Table -->
      <div class="table-wrapper">
        <table class="transactions-table">
          <thead>
            <tr>
              <th>Date & Time</th>
              <th>Type</th>
              <th>Amount</th>
              <th>Balance After</th>
              <th>Description</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="transaction in transactions" :key="transaction.id" class="transaction-row">
              <td class="date">
                {{ formatDate(transaction.created_at) }}
              </td>
              <td class="type">
                <span :class="`badge badge-${transaction.type.toLowerCase()}`">
                  {{ formatTransactionType(transaction.type) }}
                </span>
              </td>
              <td class="amount" :class="getAmountClass(transaction.type)">
                {{ getAmountSign(transaction.type) }}{{ transaction.amount.toFixed(2) }}
              </td>
              <td class="balance">
                {{ transaction.balance_after.toFixed(2) }} SC
              </td>
              <td class="description">
                {{ transaction.description }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div v-if="pagination.total > 0" class="pagination">
        <button
          @click="goToPreviousPage"
          :disabled="pagination.skip === 0 || loading"
          class="btn-pag"
        >
          ← Previous
        </button>
        <span class="page-info">
          {{ pagination.skip + 1 }}-{{ Math.min(pagination.skip + pagination.limit, pagination.total) }}
          of {{ pagination.total }}
        </span>
        <button
          @click="goToNextPage"
          :disabled="pagination.skip + pagination.limit >= pagination.total || loading"
          class="btn-pag"
        >
          Next →
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useWalletStore } from '@/stores/wallet'

const walletStore = useWalletStore()

const transactions = computed(() => walletStore.transactions)
const loading = computed(() => walletStore.loading)
const pagination = computed(() => walletStore.pagination)

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

const formatTransactionType = (type) => {
  const typeMap = {
    TOP_UP: 'Top-Up',
    PURCHASE: 'Purchase',
    CLAIM_PAYOUT: 'Claim Payout',
    REFUND: 'Refund',
    CREDIT: 'Credit',
    DEDUCT: 'Deduction'
  }
  return typeMap[type] || type
}

const getAmountSign = (type) => {
  const creditTypes = ['TOP_UP', 'CLAIM_PAYOUT', 'CREDIT', 'REFUND']
  return creditTypes.includes(type) ? '+' : '-'
}

const getAmountClass = (type) => {
  const creditTypes = ['TOP_UP', 'CLAIM_PAYOUT', 'CREDIT', 'REFUND']
  return creditTypes.includes(type) ? 'credit' : 'debit'
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

<style scoped>
.transaction-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.loading,
.empty-state {
  text-align: center;
  padding: 30px;
  color: #999;
  background: #f9f9f9;
  border-radius: 8px;
}

.table-wrapper {
  overflow-x: auto;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
}

.transactions-table {
  width: 100%;
  border-collapse: collapse;
  background: white;
}

thead {
  background: #f5f5f5;
  font-weight: 600;
}

th {
  padding: 12px;
  text-align: left;
  font-size: 13px;
  color: #666;
  border-bottom: 2px solid #e0e0e0;
}

.transaction-row {
  border-bottom: 1px solid #e0e0e0;
  transition: background 0.2s;
}

.transaction-row:hover {
  background: #fafafa;
}

td {
  padding: 12px;
  font-size: 14px;
}

.date {
  color: #666;
  font-size: 13px;
  white-space: nowrap;
}

.type {
  min-width: 100px;
}

.badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.badge-top_up {
  background: #d4edda;
  color: #155724;
}

.badge-purchase {
  background: #cce5ff;
  color: #004085;
}

.badge-claim_payout {
  background: #d4edda;
  color: #155724;
}

.badge-refund {
  background: #d4edda;
  color: #155724;
}

.badge-credit {
  background: #d4edda;
  color: #155724;
}

.badge-deduct {
  background: #f8d7da;
  color: #721c24;
}

.amount {
  font-weight: 600;
  min-width: 80px;
}

.amount.credit {
  color: #28a745;
}

.amount.debit {
  color: #dc3545;
}

.balance {
  font-weight: 500;
  color: #667eea;
  min-width: 100px;
}

.description {
  color: #999;
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 15px;
  padding: 15px;
}

.btn-pag {
  padding: 8px 16px;
  background: #f0f0f0;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
}

.btn-pag:hover:not(:disabled) {
  background: #667eea;
  color: white;
  border-color: #667eea;
}

.btn-pag:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

@media (max-width: 768px) {
  .table-wrapper {
    font-size: 12px;
  }

  th,
  td {
    padding: 8px;
  }

  .description {
    display: none;
  }

  .pagination {
    flex-wrap: wrap;
    gap: 8px;
  }
}
</style>
