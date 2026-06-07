<template>
  <div class="px-8 py-8">

    <!-- Page header -->
    <div class="flex items-center justify-between mb-8">
      <div>
        <h1 class="text-2xl font-extrabold text-slate-900 tracking-tight">Bồi thường</h1>
        <p class="text-slate-500 text-sm mt-0.5">Quản lý và xét duyệt yêu cầu bồi thường.</p>
      </div>
      <select
        v-model="statusFilter"
        @change="handleFilter"
        class="border border-slate-200 bg-white rounded-xl px-3 py-2.5 text-sm text-slate-700 font-medium outline-none focus:ring-2 focus:ring-indigo-500 transition-colors"
      >
        <option value="">Tất cả trạng thái</option>
        <option value="MANUAL_REVIEW">Chờ duyệt</option>
        <option value="PAID">Đã trả</option>
        <option value="REJECTED">Từ chối</option>
        <option value="AUTO_APPROVED">Tự động duyệt</option>
      </select>
    </div>

    <!-- Loading -->
    <div v-if="adminStore.isLoadingClaims" class="flex items-center justify-center py-24">
      <svg class="animate-spin w-8 h-8 text-indigo-600" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
        <path stroke-linecap="round" d="M12 3a9 9 0 1 0 9 9"/>
      </svg>
    </div>

    <!-- Empty -->
    <div v-else-if="adminStore.claims.length === 0" class="flex flex-col items-center justify-center py-24 bg-white rounded-2xl border border-slate-200">
      <div class="w-14 h-14 bg-slate-100 rounded-2xl flex items-center justify-center mb-4">
        <svg class="w-7 h-7 text-slate-400" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
        </svg>
      </div>
      <p class="text-slate-700 font-semibold">Chưa có yêu cầu bồi thường</p>
      <p class="text-slate-400 text-sm mt-1">Các claim sẽ xuất hiện ở đây khi được tạo.</p>
    </div>

    <!-- Claims list -->
    <div v-else class="space-y-3">
      <div
        v-for="claim in adminStore.claims"
        :key="claim.id"
        class="bg-white rounded-2xl border border-slate-200 shadow-sm p-5 hover:shadow-md transition-shadow"
      >
        <div class="flex items-start justify-between gap-4">
          <div class="flex-1 min-w-0">

            <!-- Status + trigger type -->
            <div class="flex items-center gap-2.5 mb-3">
              <span :class="getStatusClass(claim.status)" class="px-2.5 py-1 text-xs font-bold rounded-full uppercase tracking-wide">
                {{ formatStatus(claim.status) }}
              </span>
              <span class="text-xs text-slate-400 font-medium bg-slate-100 px-2 py-1 rounded-lg">{{ claim.trigger_type }}</span>
            </div>

            <p class="text-slate-800 font-semibold text-sm mb-3">{{ claim.trigger_event || 'Không có mô tả' }}</p>

            <!-- Meta grid -->
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <p class="text-[11px] text-slate-400 font-semibold uppercase tracking-wider mb-0.5">Bồi thường</p>
                <p class="font-bold text-emerald-600 text-sm">{{ claim.payout_amount }} SC</p>
              </div>
              <div>
                <p class="text-[11px] text-slate-400 font-semibold uppercase tracking-wider mb-0.5">Ngày gửi</p>
                <p class="font-semibold text-slate-800 text-sm">{{ formatDate(claim.created_at) }}</p>
              </div>
              <div>
                <p class="text-[11px] text-slate-400 font-semibold uppercase tracking-wider mb-0.5">Ngày xử lý</p>
                <p class="font-semibold text-slate-800 text-sm">{{ claim.processed_at ? formatDate(claim.processed_at) : '—' }}</p>
              </div>
              <div>
                <p class="text-[11px] text-slate-400 font-semibold uppercase tracking-wider mb-0.5">Claim ID</p>
                <p class="font-mono text-xs text-slate-500 bg-slate-50 border border-slate-100 px-2 py-1 rounded-lg inline-block">{{ claim.id?.substring(0, 8) }}…</p>
              </div>
            </div>

            <!-- Evidence -->
            <div v-if="claim.evidence_urls?.length" class="mt-3 flex flex-wrap gap-2">
              <a
                v-for="(url, i) in claim.evidence_urls"
                :key="i"
                :href="url"
                target="_blank"
                class="inline-flex items-center gap-1 text-indigo-600 hover:text-indigo-800 text-xs font-medium border border-indigo-100 bg-indigo-50 px-2.5 py-1 rounded-lg transition-colors"
              >
                <svg class="w-3 h-3" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/>
                </svg>
                Bằng chứng {{ i + 1 }}
              </a>
            </div>
          </div>

          <!-- Action buttons for MANUAL_REVIEW -->
          <div v-if="claim.status === 'MANUAL_REVIEW'" class="flex flex-col gap-2 flex-shrink-0">
            <button
              @click="handleApprove(claim.id)"
              :disabled="processingId === claim.id"
              class="inline-flex items-center gap-1.5 bg-emerald-600 hover:bg-emerald-700 active:scale-95 text-white px-4 py-2 rounded-xl text-sm font-semibold transition-all disabled:opacity-50"
            >
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/>
              </svg>
              Duyệt
            </button>
            <button
              @click="handleReject(claim.id)"
              :disabled="processingId === claim.id"
              class="inline-flex items-center gap-1.5 bg-red-500 hover:bg-red-600 active:scale-95 text-white px-4 py-2 rounded-xl text-sm font-semibold transition-all disabled:opacity-50"
            >
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
              </svg>
              Từ chối
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Total -->
    <p class="text-xs text-slate-400 mt-4 font-medium">Tổng: {{ adminStore.claimsTotal }} claims</p>

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

const getStatusClass = (s) => ({
  MANUAL_REVIEW: 'bg-amber-100 text-amber-800',
  PENDING:       'bg-amber-100 text-amber-800',
  AUTO_APPROVED: 'bg-blue-100 text-blue-700',
  APPROVED:      'bg-emerald-100 text-emerald-800',
  PAID:          'bg-emerald-100 text-emerald-800',
  REJECTED:      'bg-red-100 text-red-700',
})[s] || 'bg-slate-100 text-slate-600'

const formatStatus = (s) => ({
  MANUAL_REVIEW: 'Chờ Duyệt',
  PENDING:       'Đang Xử Lý',
  AUTO_APPROVED: 'Tự Động Duyệt',
  APPROVED:      'Đã Duyệt',
  PAID:          'Đã Trả',
  REJECTED:      'Từ Chối',
})[s] || s

const formatDate = (d) => d ? new Date(d).toLocaleDateString('vi-VN') : ''
</script>
