import api from './api'

const adminService = {
  /**
   * Lấy dashboard metrics
   */
  async getDashboard() {
    const { data } = await api.get('/admin/dashboard')
    return data
  },

  /**
   * Lấy danh sách users
   */
  async getUsers(skip = 0, limit = 50, filters = {}) {
    const { data } = await api.get('/admin/users', {
      params: { skip, limit, ...filters },
    })
    return data
  },

  /**
   * Lấy danh sách policies
   */
  async getPolicies(skip = 0, limit = 50, status = null) {
    const params = { skip, limit }
    if (status) params.status = status
    const { data } = await api.get('/admin/policies', { params })
    return data
  },

  /**
   * Lấy danh sách claims
   */
  async getClaims(skip = 0, limit = 50, status = null) {
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

  /**
   * Lấy danh sách KYC pending
   */
  async getKycPending() {
    const { data } = await api.get('/admin/kyc/pending')
    return data
  },

  /**
   * Duyệt hoặc từ chối KYC
   */
  async reviewKyc(userId, action, rejectionReason = null) {
    const payload = { action }
    if (rejectionReason) payload.rejection_reason = rejectionReason
    const { data } = await api.patch(`/admin/kyc/${userId}`, payload)
    return data
  },

  /**
   * Lấy risk analytics data
   */
  async getRiskAnalytics() {
    const { data } = await api.get('/admin/risk-analytics')
    return data
  },

  /**
   * Lấy ML model stats
   */
  async getMlStats() {
    const { data } = await api.get('/admin/ml/model-stats')
    return data
  },

  /**
   * Retrain ML models
   */
  async retrainModels() {
    const { data } = await api.post('/admin/ml/retrain')
    return data
  },
}

export default adminService
