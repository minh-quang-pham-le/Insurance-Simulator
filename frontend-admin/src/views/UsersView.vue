<template>
  <div class="px-8 py-8">

    <!-- Page header -->
    <div class="mb-8">
      <h1 class="text-2xl font-extrabold text-slate-900 tracking-tight">Người dùng</h1>
      <p class="text-slate-500 text-sm mt-0.5">Danh sách tài khoản đã đăng ký trên hệ thống.</p>
    </div>

    <!-- Error banner -->
    <div v-if="actionError" class="mb-4 bg-red-50 border border-red-100 rounded-xl p-4 flex items-center justify-between">
      <div class="flex items-center gap-2 text-red-600 text-sm">
        <svg class="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v4m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/>
        </svg>
        {{ actionError }}
      </div>
      <button @click="actionError = null" class="text-red-400 hover:text-red-600 transition-colors">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
        </svg>
      </button>
    </div>

    <!-- Loading -->
    <div v-if="adminStore.isLoadingUsers" class="flex items-center justify-center py-24">
      <svg class="animate-spin w-8 h-8 text-indigo-600" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
        <path stroke-linecap="round" d="M12 3a9 9 0 1 0 9 9"/>
      </svg>
    </div>

    <div v-else>
      <div class="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        <table class="min-w-full">
          <thead>
            <tr class="border-b border-slate-100 bg-slate-50/60">
              <th class="px-5 py-4 text-left text-[11px] font-bold text-slate-400 uppercase tracking-wider">Người dùng</th>
              <th class="px-5 py-4 text-left text-[11px] font-bold text-slate-400 uppercase tracking-wider">Email</th>
              <th class="px-5 py-4 text-left text-[11px] font-bold text-slate-400 uppercase tracking-wider">Role</th>
              <th class="px-5 py-4 text-left text-[11px] font-bold text-slate-400 uppercase tracking-wider">KYC</th>
              <th class="px-5 py-4 text-left text-[11px] font-bold text-slate-400 uppercase tracking-wider">Trạng thái</th>
              <th class="px-5 py-4 text-left text-[11px] font-bold text-slate-400 uppercase tracking-wider">Đăng ký</th>
              <th class="px-5 py-4 text-right text-[11px] font-bold text-slate-400 uppercase tracking-wider">Hành động</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-50">
            <tr
              v-for="user in adminStore.users"
              :key="user.id"
              :class="['transition-colors', user.is_active ? 'hover:bg-slate-50/60' : 'bg-red-50/30 hover:bg-red-50/50']"
            >
              <!-- Name -->
              <td class="px-5 py-4">
                <div class="flex items-center gap-3">
                  <div :class="['w-8 h-8 rounded-xl flex items-center justify-center flex-shrink-0', user.is_active ? 'bg-indigo-100' : 'bg-slate-100']">
                    <span :class="['text-xs font-bold', user.is_active ? 'text-indigo-600' : 'text-slate-400']">
                      {{ (user.full_name || 'U')[0].toUpperCase() }}
                    </span>
                  </div>
                  <span :class="['font-semibold text-sm', user.is_active ? 'text-slate-800' : 'text-slate-400 line-through']">
                    {{ user.full_name }}
                  </span>
                </div>
              </td>

              <!-- Email -->
              <td class="px-5 py-4 text-sm text-slate-500">{{ user.email }}</td>

              <!-- Role -->
              <td class="px-5 py-4">
                <span :class="user.role === 'ADMIN' ? 'bg-violet-100 text-violet-700' : 'bg-slate-100 text-slate-600'"
                      class="px-2.5 py-1 text-xs font-bold rounded-full uppercase tracking-wide">
                  {{ user.role }}
                </span>
              </td>

              <!-- KYC -->
              <td class="px-5 py-4">
                <span :class="getKycClass(user.kyc_status)"
                      class="px-2.5 py-1 text-xs font-bold rounded-full uppercase tracking-wide">
                  {{ user.kyc_status }}
                </span>
              </td>

              <!-- Active status -->
              <td class="px-5 py-4">
                <span :class="user.is_active ? 'bg-emerald-100 text-emerald-700' : 'bg-red-100 text-red-600'"
                      class="inline-flex items-center gap-1.5 px-2.5 py-1 text-xs font-bold rounded-full">
                  <span :class="['w-1.5 h-1.5 rounded-full', user.is_active ? 'bg-emerald-500' : 'bg-red-400']"></span>
                  {{ user.is_active ? 'Hoạt động' : 'Đã khóa' }}
                </span>
              </td>

              <!-- Date -->
              <td class="px-5 py-4 text-sm text-slate-400 tabular-nums">{{ formatDate(user.created_at) }}</td>

              <!-- Actions -->
              <td class="px-5 py-4">
                <div class="flex items-center justify-end gap-2">
                  <!-- Disable / Enable -->
                  <button
                    v-if="user.role !== 'ADMIN'"
                    @click="handleToggleStatus(user)"
                    :disabled="processingId === user.id"
                    :title="user.is_active ? 'Khóa tài khoản' : 'Mở khóa tài khoản'"
                    :class="[
                      'inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all disabled:opacity-40',
                      user.is_active
                        ? 'bg-amber-50 text-amber-700 hover:bg-amber-100 border border-amber-200'
                        : 'bg-emerald-50 text-emerald-700 hover:bg-emerald-100 border border-emerald-200'
                    ]"
                  >
                    <svg v-if="processingId === user.id" class="animate-spin w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                      <path stroke-linecap="round" d="M12 3a9 9 0 1 0 9 9"/>
                    </svg>
                    <template v-else>
                      <!-- Lock icon -->
                      <svg v-if="user.is_active" class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                        <rect x="3" y="11" width="18" height="11" rx="2"/>
                        <path stroke-linecap="round" d="M7 11V7a5 5 0 0 1 10 0v4"/>
                      </svg>
                      <!-- Unlock icon -->
                      <svg v-else class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                        <rect x="3" y="11" width="18" height="11" rx="2"/>
                        <path stroke-linecap="round" d="M7 11V7a5 5 0 0 1 9.9-1"/>
                      </svg>
                    </template>
                    {{ user.is_active ? 'Khóa' : 'Mở khóa' }}
                  </button>

                  <!-- Delete -->
                  <button
                    v-if="user.role !== 'ADMIN'"
                    @click="handleDelete(user)"
                    :disabled="processingId === user.id"
                    title="Xóa tài khoản"
                    class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-red-50 text-red-600 hover:bg-red-100 border border-red-200 transition-all disabled:opacity-40"
                  >
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                    </svg>
                    Xóa
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <p class="text-xs text-slate-400 mt-3 font-medium">Tổng: {{ adminStore.usersTotal }} người dùng</p>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAdminStore } from '../stores/admin'

const adminStore = useAdminStore()
const processingId = ref(null)
const actionError = ref(null)

onMounted(() => {
  adminStore.fetchUsers()
})

const handleToggleStatus = async (user) => {
  const action = user.is_active ? 'khóa' : 'mở khóa'
  if (!confirm(`Bạn có chắc muốn ${action} tài khoản "${user.full_name}"?`)) return
  processingId.value = user.id
  actionError.value = null
  try {
    await adminStore.toggleUserStatus(user.id)
  } catch (err) {
    actionError.value = err.response?.data?.detail || `Không thể ${action} tài khoản`
  } finally {
    processingId.value = null
  }
}

const handleDelete = async (user) => {
  if (!confirm(`Xóa vĩnh viễn tài khoản "${user.full_name}" (${user.email})?\n\nHành động này không thể hoàn tác.`)) return
  processingId.value = user.id
  actionError.value = null
  try {
    await adminStore.deleteUser(user.id)
  } catch (err) {
    actionError.value = err.response?.data?.detail || 'Không thể xóa tài khoản'
  } finally {
    processingId.value = null
  }
}

const getKycClass = (status) => ({
  VERIFIED:      'bg-emerald-100 text-emerald-700',
  PENDING:       'bg-amber-100 text-amber-700',
  NOT_SUBMITTED: 'bg-slate-100 text-slate-500',
  REJECTED:      'bg-red-100 text-red-700',
})[status] || 'bg-slate-100 text-slate-600'

const formatDate = (d) => d ? new Date(d).toLocaleDateString('vi-VN') : ''
</script>
