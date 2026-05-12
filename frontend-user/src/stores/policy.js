import { defineStore } from 'pinia'
import policyService from '../services/policyService'
import { useWalletStore } from './wallet' // Để cập nhật lại ví sau khi mua/hủy

export const usePolicyStore = defineStore('policy', {
  state: () => ({
    myPolicies: [],
    totalPolicies: 0,
    isLoading: false,
    error: null,
  }),

  actions: {
    async fetchMyPolicies(skip = 0) {
      this.isLoading = true
      this.error = null
      try {
        const data = await policyService.getMyPolicies(skip)
        this.myPolicies = data.policies
        this.totalPolicies = data.total
      } catch (err) {
        this.error = err.response?.data?.detail || 'Lỗi khi tải danh sách hợp đồng'
      } finally {
        this.isLoading = false
      }
    },

    async cancelPolicy(policyId) {
      this.isLoading = true
      try {
        await policyService.cancelPolicy(policyId)
        // Cập nhật lại danh sách local
        const index = this.myPolicies.findIndex(p => p.id === policyId)
        if (index !== -1) {
          this.myPolicies[index].status = 'CANCELLED'
        }
        // Gọi update ví
        const walletStore = useWalletStore()
        if (walletStore.fetchBalance) await walletStore.fetchBalance()
        
        return true
      } catch (err) {
        throw new Error(err.response?.data?.detail || 'Không thể hủy hợp đồng')
      } finally {
        this.isLoading = false
      }
    }
  }
})