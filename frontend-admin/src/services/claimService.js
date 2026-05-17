import api from './api'

const claimService = {
  /**
   * Lấy danh sách tất cả claims (Admin)
   */
  async getAllClaims(skip = 0, limit = 50, status = null) {
    const params = { skip, limit }
    if (status) params.status = status
    const { data } = await api.get('/admin/claims', { params })
    return data
  },

  /**
   * Duyệt hoặc từ chối claim
   */
  async reviewClaim(claimId, action, rejectionReason = null) {
    const payload = { action }
    if (rejectionReason) payload.rejection_reason = rejectionReason
    const { data } = await api.put(`/admin/claims/${claimId}/review`, payload)
    return data
  },
}

export default claimService
