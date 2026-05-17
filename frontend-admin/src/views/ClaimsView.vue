<template>
  <div class="p-6">
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-bold text-gray-900">Quản Lý Bồi Thường</h1>
      <select
        v-model="statusFilter"
        @change="handleFilter"
        class="border border-gray-300 rounded-lg px-3 py-2 text-sm bg-white"
      >
        <option value="">Tất cả</option>
        <option value="MANUAL_REVIEW">Chờ duyệt</option>
        <option value="PAID">Đã trả</option>
        <option value="REJECTED">Từ chối</option>
        <option value="AUTO_APPROVED">Tự động duyệt</option>
      </select>
    </div>

    <div v-if="adminStore.isLoadingClaims" class="flex justify-center py-20">
      <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-indigo-600"></div>
    </div>

    <div v-else-if="adminStore.claims.length === 0" class="text-center py-20 bg-white rounded-xl border border-gray-200">
      <span class="text-5xl mb-4 block">📋</span>
      <h3 class="text-lg font-medium text-gray-900">Chưa có yêu cầu bồi thường nào</h3>
    </div>

    <div v-else class="space-y-4">
      <div
        v-for="claim in adminStore.claims"
        :key="claim.id"
        class="bg-white rounded-xl border border-gray-200 shadow-sm p-5"
      >
        <div class="flex items-start justify-between">
          <div class="flex-1">
            <div class="flex items-center gap-3 mb-2">
              <span :class="getStatusClass(claim.status)" class="px-3 py-1 text-xs font-bold rounded-full uppercase">
                {{ formatStatus(claim.status) }}
              </span>
              <span class="text-xs text-gray-400">{{ claim.trigger_type }}</span>
            </div>

            <p class="text-gray-800 font-medium">{{ claim.trigger_event || 'Không có mô tả' }}</p>

            <div class="mt-3 grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div>
                <p class="text-gray-500">Mức bồi thường</p>
                <p class="font-bold text-green-600">{{ claim.payout_amount }} SC</p>
              </div>
              <div>
                <p class="text-gray-500">Ngày gửi</p>
                <p class="font-medium text-gray-900">{{ formatDate(claim.created_at) }}</p>
              </div>
              <div>
                <p class="text-gray-500">Ngày xử lý</p>
                <p class="font-medium text-gray-900">{{ claim.processed_at ? formatDate(claim.processed_at) : '—' }}</p>
              </div>
              <div>
                <p class="text-gray-500">Claim ID</p>
                <p class="font-mono text-xs text-gray-600">{{ claim.id?.substring(0, 8) }}...</p>
              </div>
            </div>

            <!-- Evidence URLs -->
            <div v-if="claim.evidence_urls && claim.evidence_urls.length" class="mt-3">
              <p class="text-xs text-gray-500 mb-1">Bằng chứng:</p>
              <div class="flex flex-wrap gap-2">
                <a
                  v-for="(url, i) in claim.evidence_urls"
                  :key="i"
                  :href="url"
                  target="_blank"
                  class="text-blue-600 text-xs underline hover:text-blue-800"
                >
                  Link {{ i + 1 }}
                </a>
              </div>
            </div>
          </div>

          <!-- Action buttons for MANUAL_REVIEW claims -->
          <div v-if="claim.status === 'MANUAL_REVIEW'" class="flex flex-col gap-2 ml-4">
            <button
              @click="handleApprove(claim.id)"
              :disabled="processingId === claim.id"
              class="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors disabled:opacity-50"
            >
              ✓ Duyệt
            </button>
            <button
              @click="handleReject(claim.id)"
              :disabled="processingId === claim.id"
              class="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors disabled:opacity-50"
            >
              ✗ Từ chối
            </button>
          </div>
        </div>
      </div>
    </div>

    <p class="text-sm text-gray-500 mt-4">Tổng: {{ adminStore.claimsTotal }} claims</p>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAdminStore } from '../stores/admin'

const adminStore = useAdminStore()
const statusFilter = ref('')
const processingId = ref(null)

onMounted(() => {
  adminStore.fetchClaims()
})

const handleFilter = () => {
  adminStore.fetchClaims(0, 50, statusFilter.value || null)
}

const handleApprove = async (claimId) => {
  if (!confirm('Bạn có chắc muốn duyệt claim này? Tiền sẽ được cộng vào ví user.')) return
  processingId.value = claimId
  try {
    await adminStore.reviewClaim(claimId, 'approve')
    alert('Đã duyệt thành công!')
  } catch (err) {
    alert(err.response?.data?.detail || 'Lỗi khi duyệt claim')
  } finally {
    processingId.value = null
  }
}

const handleReject = async (claimId) => {
  const reason = prompt('Nhập lý do từ chối:')
  if (reason === null) return
  processingId.value = claimId
  try {
    await adminStore.reviewClaim(claimId, 'reject', reason)
    alert('Đã từ chối claim.')
  } catch (err) {
    alert(err.response?.data?.detail || 'Lỗi khi từ chối claim')
  } finally {
    processingId.value = null
  }
}

const getStatusClass = (s) => {
  const c = {
    'MANUAL_REVIEW': 'bg-yellow-100 text-yellow-800',
    'PENDING': 'bg-yellow-100 text-yellow-800',
    'AUTO_APPROVED': 'bg-blue-100 text-blue-800',
    'APPROVED': 'bg-green-100 text-green-800',
    'PAID': 'bg-green-100 text-green-800',
    'REJECTED': 'bg-red-100 text-red-800',
  }
  return c[s] || 'bg-gray-100 text-gray-800'
}

const formatStatus = (s) => {
  const names = {
    'MANUAL_REVIEW': 'Chờ Duyệt',
    'PENDING': 'Đang Xử Lý',
    'AUTO_APPROVED': 'Tự Động Duyệt',
    'APPROVED': 'Đã Duyệt',
    'PAID': 'Đã Trả',
    'REJECTED': 'Từ Chối',
  }
  return names[s] || s
}

const formatDate = (d) => d ? new Date(d).toLocaleDateString('vi-VN') : ''
</script>
