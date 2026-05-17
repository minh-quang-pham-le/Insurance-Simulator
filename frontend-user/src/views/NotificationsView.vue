<template>
  <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <div class="flex justify-between items-center mb-8">
      <div>
        <h1 class="text-3xl font-extrabold text-gray-900 tracking-tight">Thông Báo</h1>
        <p class="mt-2 text-sm text-gray-600">Theo dõi trạng thái yêu cầu bồi thường và cập nhật hệ thống.</p>
      </div>
      <button
        v-if="notificationStore.hasUnread"
        @click="notificationStore.markAllAsRead()"
        class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
      >
        Đánh dấu tất cả đã đọc
      </button>
    </div>

    <div v-if="notificationStore.isLoading" class="flex justify-center py-20">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
    </div>

    <div v-else-if="notificationStore.notifications.length === 0" class="text-center py-20 bg-white rounded-xl border border-gray-200">
      <span class="text-5xl mb-4 block">🔔</span>
      <h3 class="text-lg font-medium text-gray-900">Chưa có thông báo nào</h3>
      <p class="text-gray-500 mt-1">Thông báo về bồi thường và cập nhật sẽ hiển thị ở đây.</p>
    </div>

    <div v-else class="space-y-3">
      <div
        v-for="notif in notificationStore.notifications"
        :key="notif.id"
        @click="handleClick(notif)"
        :class="[
          'bg-white rounded-xl border p-5 cursor-pointer transition-all hover:shadow-md',
          notif.is_read ? 'border-gray-200 opacity-75' : 'border-blue-200 shadow-sm bg-blue-50/30'
        ]"
      >
        <div class="flex items-start gap-4">
          <div class="flex-shrink-0 mt-1">
            <span class="text-2xl">{{ getIcon(notif.type) }}</span>
          </div>
          <div class="flex-1 min-w-0">
            <div class="flex items-center justify-between gap-2">
              <h3 :class="['font-semibold', notif.is_read ? 'text-gray-700' : 'text-gray-900']">
                {{ notif.title }}
              </h3>
              <span v-if="!notif.is_read" class="flex-shrink-0 w-2.5 h-2.5 rounded-full bg-blue-500"></span>
            </div>
            <p class="text-sm text-gray-600 mt-1">{{ notif.message }}</p>
            <p class="text-xs text-gray-400 mt-2">{{ formatTime(notif.created_at) }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useNotificationStore } from '../stores/notification'

const notificationStore = useNotificationStore()

onMounted(() => {
  notificationStore.fetchNotifications()
})

const handleClick = (notif) => {
  if (!notif.is_read) {
    notificationStore.markAsRead(notif.id)
  }
}

const getIcon = (type) => {
  const icons = {
    'CLAIM_TRIGGERED': '📋',
    'PAYOUT_RECEIVED': '💰',
    'POLICY_EXPIRING': '⏳',
    'POLICY_EXPIRED': '📅',
    'SYSTEM': '🔔',
  }
  return icons[type] || '🔔'
}

const formatTime = (dateStr) => {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  const now = new Date()
  const diffMs = now - d
  const diffMin = Math.floor(diffMs / 60000)
  const diffHour = Math.floor(diffMs / 3600000)
  const diffDay = Math.floor(diffMs / 86400000)

  if (diffMin < 1) return 'Vừa xong'
  if (diffMin < 60) return `${diffMin} phút trước`
  if (diffHour < 24) return `${diffHour} giờ trước`
  if (diffDay < 7) return `${diffDay} ngày trước`
  return d.toLocaleDateString('vi-VN')
}
</script>
