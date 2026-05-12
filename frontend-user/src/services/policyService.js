import api from './api'

const policyService = {
  async calculatePremium(payload) {
    const response = await api.post('/policies/calculate-premium', payload)
    return response.data
  },

  async purchasePolicy(payload) {
    const response = await api.post('/policies/purchase', payload)
    return response.data
  },

  async getMyPolicies(skip = 0, limit = 50) {
    const response = await api.get(`/policies?skip=${skip}&limit=${limit}`)
    return response.data
  },

  async cancelPolicy(policyId) {
    const response = await api.post(`/policies/${policyId}/cancel`)
    return response.data
  }
}

export default policyService