import api from './api'

const notificationService = {
  /**
   * Lấy danh sách thông báo
   */
  async getNotifications(skip = 0, limit = 50, unreadOnly = false) {
    const { data } = await api.get('/notifications', {
      params: { skip, limit, unread_only: unreadOnly },
    })
    return data
  },

  /**
   * Lấy số lượng thông báo chưa đọc
   */
  async getUnreadCount() {
    const { data } = await api.get('/notifications/unread-count')
    return data
  },

  /**
   * Đánh dấu 1 thông báo là đã đọc
   */
  async markAsRead(notificationId) {
    const { data } = await api.post(`/notifications/${notificationId}/read`)
    return data
  },

  /**
   * Đánh dấu tất cả thông báo là đã đọc
   */
  async markAllAsRead() {
    const { data } = await api.post('/notifications/read-all')
    return data
  },
}

export default notificationService
