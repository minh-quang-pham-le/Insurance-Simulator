import { defineStore } from 'pinia'
import { ref } from 'vue'
import adminService from '@/services/adminService'

export const useAdminStore = defineStore('admin', () => {
  // Dashboard
  const dashboardMetrics = ref(null)
  const isLoadingDashboard = ref(false)

  // Users
  const users = ref([])
  const usersTotal = ref(0)
  const isLoadingUsers = ref(false)

  // Policies
  const policies = ref([])
  const policiesTotal = ref(0)
  const isLoadingPolicies = ref(false)

  // Claims
  const claims = ref([])
  const claimsTotal = ref(0)
  const isLoadingClaims = ref(false)

  // KYC
  const kycPending = ref([])
  const isLoadingKyc = ref(false)

  // Error
  const error = ref(null)

  // Actions
  const fetchDashboard = async () => {
    isLoadingDashboard.value = true
    error.value = null
    try {
      dashboardMetrics.value = await adminService.getDashboard()
    } catch (err) {
      error.value = err.response?.data?.detail || 'Không thể tải dashboard'
    } finally {
      isLoadingDashboard.value = false
    }
  }

  const fetchUsers = async (skip = 0, limit = 50, filters = {}) => {
    isLoadingUsers.value = true
    try {
      const data = await adminService.getUsers(skip, limit, filters)
      users.value = data.users
      usersTotal.value = data.total
    } catch (err) {
      error.value = err.response?.data?.detail || 'Không thể tải danh sách users'
    } finally {
      isLoadingUsers.value = false
    }
  }

  const fetchPolicies = async (skip = 0, limit = 50, status = null) => {
    isLoadingPolicies.value = true
    try {
      const data = await adminService.getPolicies(skip, limit, status)
      policies.value = data.policies
      policiesTotal.value = data.total
    } catch (err) {
      error.value = err.response?.data?.detail || 'Không thể tải danh sách policies'
    } finally {
      isLoadingPolicies.value = false
    }
  }

  const fetchClaims = async (skip = 0, limit = 50, status = null) => {
    isLoadingClaims.value = true
    try {
      const data = await adminService.getClaims(skip, limit, status)
      claims.value = data.claims
      claimsTotal.value = data.total
    } catch (err) {
      error.value = err.response?.data?.detail || 'Không thể tải danh sách claims'
    } finally {
      isLoadingClaims.value = false
    }
  }

  const reviewClaim = async (claimId, action, reason = null) => {
    try {
      await adminService.reviewClaim(claimId, action, reason)
      await fetchClaims()
    } catch (err) {
      throw err
    }
  }

  const fetchKycPending = async () => {
    isLoadingKyc.value = true
    try {
      const data = await adminService.getKycPending()
      kycPending.value = data.users
    } catch (err) {
      error.value = err.response?.data?.detail || 'Không thể tải KYC queue'
    } finally {
      isLoadingKyc.value = false
    }
  }

  const reviewKyc = async (userId, action, reason = null) => {
    try {
      await adminService.reviewKyc(userId, action, reason)
      await fetchKycPending()
    } catch (err) {
      throw err
    }
  }

  const toggleUserStatus = async (userId) => {
    const updated = await adminService.toggleUserStatus(userId)
    const idx = users.value.findIndex(u => u.id === userId)
    if (idx !== -1) users.value[idx] = updated
  }

  const deleteUser = async (userId) => {
    await adminService.deleteUser(userId)
    users.value = users.value.filter(u => u.id !== userId)
    usersTotal.value = Math.max(0, usersTotal.value - 1)
  }

  return {
    dashboardMetrics,
    isLoadingDashboard,
    users,
    usersTotal,
    isLoadingUsers,
    policies,
    policiesTotal,
    isLoadingPolicies,
    claims,
    claimsTotal,
    isLoadingClaims,
    kycPending,
    isLoadingKyc,
    error,
    fetchDashboard,
    fetchUsers,
    fetchPolicies,
    fetchClaims,
    reviewClaim,
    fetchKycPending,
    reviewKyc,
    toggleUserStatus,
    deleteUser,
  }
})
