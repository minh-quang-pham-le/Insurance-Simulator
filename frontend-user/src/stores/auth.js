import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../services/api'

export const useAuthStore = defineStore('auth', () => {
  // State
  const accessToken = ref(localStorage.getItem('accessToken'))
  const refreshToken = ref(localStorage.getItem('refreshToken'))
  const user = ref(null)

  // Computed
  const isAuthenticated = computed(() => !!accessToken.value)

  // Methods
  async function register(email, password, fullName) {
    const { data } = await api.post('/auth/register', {
      email,
      password,
      full_name: fullName
    })
    user.value = data
    return data
  }

  async function login(email, password) {
    const { data } = await api.post('/auth/login', {
      email,
      password
    })
    setTokens(data.access_token, data.refresh_token)
    await fetchMe()
  }

  async function fetchMe() {
    try {
      const { data } = await api.get('/auth/me')
      user.value = data
      return data
    } catch (error) {
      // If fetch fails, clear tokens
      logout()
      throw error
    }
  }

  async function submitKyc(phoneNumber, identityDetails = '') {
    const { data } = await api.post('/auth/kyc/submit', {
      phone_number: phoneNumber,
      identity_details: identityDetails
    })
    await fetchMe()
    return data
  }

  async function getKycStatus() {
    const { data } = await api.get('/auth/kyc/status')
    return data.kyc_status
  }

  function setTokens(access, refresh) {
    accessToken.value = access
    refreshToken.value = refresh
    localStorage.setItem('accessToken', access)
    localStorage.setItem('refreshToken', refresh)
  }

  function logout() {
    accessToken.value = null
    refreshToken.value = null
    user.value = null
    localStorage.removeItem('accessToken')
    localStorage.removeItem('refreshToken')
  }

  // Load user from token on init if exists
  if (accessToken.value && !user.value) {
    fetchMe().catch(() => {
      logout()
    })
  }

  return {
    // State
    accessToken,
    refreshToken,
    user,
    
    // Computed
    isAuthenticated,
    
    // Methods
    register,
    login,
    logout,
    fetchMe,
    setTokens,
    submitKyc,
    getKycStatus,
  }
})
