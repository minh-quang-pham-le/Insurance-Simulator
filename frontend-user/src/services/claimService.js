import api from './api'

const claimService = {
  /**
   * Gửi yêu cầu bồi thường thủ công
   */
  async submitClaim(policyId, description, evidenceUrls = null) {
    const payload = {
      policy_id: policyId,
      description,
    }
    if (evidenceUrls && evidenceUrls.length > 0) {
      payload.evidence_urls = evidenceUrls
    }
    const { data } = await api.post('/claims', payload)
    return data
  },

  /**
   * Lấy danh sách claims của user
   */
  async getMyClaims(skip = 0, limit = 50) {
    const { data } = await api.get('/claims', { params: { skip, limit } })
    return data
  },

  /**
   * Lấy chi tiết một claim
   */
  async getClaimById(claimId) {
    const { data } = await api.get(`/claims/${claimId}`)
    return data
  },
}

export default claimService
