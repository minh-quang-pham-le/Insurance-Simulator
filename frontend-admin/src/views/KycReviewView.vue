<template>
  <div class="p-6">
    <h1 class="text-2xl font-bold text-gray-900 mb-6">Duyệt KYC</h1>

    <div v-if="adminStore.isLoadingKyc" class="flex justify-center py-20">
      <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-indigo-600"></div>
    </div>

    <div v-else-if="adminStore.kycPending.length === 0" class="text-center py-20 bg-white rounded-xl border border-gray-200">
      <span class="text-5xl mb-4 block">✅</span>
      <h3 class="text-lg font-medium text-gray-900">Không có yêu cầu KYC nào chờ duyệt</h3>
      <p class="text-gray-500 mt-1">Tất cả đã được xử lý.</p>
    </div>

    <div v-else class="space-y-4">
      <div
        v-for="user in adminStore.kycPending"
        :key="user.id"
        class="bg-white rounded-xl border border-yellow-200 shadow-sm p-6"
      >
        <div class="flex items-center justify-between">
          <div class="flex-1">
            <h3 class="text-lg font-bold text-gray-900">{{ user.full_name }}</h3>
            <p class="text-sm text-gray-500 mt-1">{{ user.email }}</p>

            <div class="mt-3 grid grid-cols-2 gap-4 text-sm">
              <div>
                <p class="text-gray-500">Số điện thoại</p>
                <p class="font-medium text-gray-900">{{ user.phone_number || 'Chưa cung cấp' }}</p>
              </div>
              <div>
                <p class="text-gray-500">Ngày gửi KYC</p>
                <p class="font-medium text-gray-900">{{ formatDate(user.kyc_submitted_at) }}</p>
              </div>
            </div>
          </div>

          <div class="flex gap-3 ml-4">
            <button
              @click="handleApprove(user.id)"
              :disabled="processingId === user.id"
              class="bg-green-600 hover:bg-green-700 text-white px-5 py-2.5 rounded-lg font-medium transition-colors disabled:opacity-50"
            >
              ✓ Phê duyệt
            </button>
            <button
              @click="handleReject(user.id)"
              :disabled="processingId === user.id"
              class="bg-red-500 hover:bg-red-600 text-white px-5 py-2.5 rounded-lg font-medium transition-colors disabled:opacity-50"
            >
              ✗ Từ chối
            </button>
          </div>
        </div>
      </div>
    </div>

    <p v-if="adminStore.kycPending.length > 0" class="text-sm text-gray-500 mt-4">
      Tổng: {{ adminStore.kycPending.length }} người đang chờ
    </p>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAdminStore } from '../stores/admin'

const adminStore = useAdminStore()
const processingId = ref(null)

onMounted(() => {
  adminStore.fetchKycPending()
})

const handleApprove = async (userId) => {
  if (!confirm('Phê duyệt KYC cho user này?')) return
  processingId.value = userId
  try {
    await adminStore.reviewKyc(userId, 'approve')
    alert('Đã phê duyệt KYC!')
  } catch (err) {
    alert(err.response?.data?.detail || 'Lỗi khi phê duyệt')
  } finally {
    processingId.value = null
  }
}

const handleReject = async (userId) => {
  const reason = prompt('Nhập lý do từ chối KYC:')
  if (reason === null) return
  processingId.value = userId
  try {
    await adminStore.reviewKyc(userId, 'reject', reason)
    alert('Đã từ chối KYC.')
  } catch (err) {
    alert(err.response?.data?.detail || 'Lỗi khi từ chối')
  } finally {
    processingId.value = null
  }
}

const formatDate = (d) => d ? new Date(d).toLocaleDateString('vi-VN') : '—'
</script>
