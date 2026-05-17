import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import notificationService from '@/services/notificationService'

export const useNotificationStore = defineStore('notification', () => {
  // State
  const notifications = ref([])
  const unreadCount = ref(0)
  const isLoading = ref(false)
  const error = ref(null)
  const pagination = ref({ total: 0, page: 1, page_size: 50 })

  // Computed
  const hasUnread = computed(() => unreadCount.value > 0)

  // Actions
  const fetchNotifications = async (skip = 0, limit = 50) => {
    isLoading.value = true
    error.value = null
    try {
      const data = await notificationService.getNotifications(skip, limit)
      notifications.value = data.notifications
      pagination.value = { total: data.total, page: data.page, page_size: data.page_size }
    } catch (err) {
      error.value = err.response?.data?.detail || 'Không thể tải thông báo'
    } finally {
      isLoading.value = false
    }
  }

  const fetchUnreadCount = async () => {
    try {
      const data = await notificationService.getUnreadCount()
      unreadCount.value = data.count
    } catch (err) {
      console.error('Failed to fetch unread count:', err)
    }
  }

  const markAsRead = async (notificationId) => {
    try {
      await notificationService.markAsRead(notificationId)
      // Update local state
      const notif = notifications.value.find(n => n.id === notificationId)
      if (notif && !notif.is_read) {
        notif.is_read = true
        unreadCount.value = Math.max(0, unreadCount.value - 1)
      }
    } catch (err) {
      console.error('Failed to mark notification as read:', err)
    }
  }

  const markAllAsRead = async () => {
    try {
      await notificationService.markAllAsRead()
      notifications.value.forEach(n => { n.is_read = true })
      unreadCount.value = 0
    } catch (err) {
      console.error('Failed to mark all notifications as read:', err)
    }
  }

  return {
    notifications,
    unreadCount,
    isLoading,
    error,
    pagination,
    hasUnread,
    fetchNotifications,
    fetchUnreadCount,
    markAsRead,
    markAllAsRead,
  }
})
