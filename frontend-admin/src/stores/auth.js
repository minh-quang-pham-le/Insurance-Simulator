import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../services/api'

export const useAuthStore = defineStore('auth', () => {
  // State
  const accessToken = ref(localStorage.getItem('admin_accessToken'))
  const refreshToken = ref(localStorage.getItem('admin_refreshToken'))
  const user = ref(null)

  // Computed
  const isAuthenticated = computed(() => !!accessToken.value)

  // Methods
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
      logout()
      throw error
    }
  }

  function setTokens(access, refresh) {
    accessToken.value = access
    refreshToken.value = refresh
    localStorage.setItem('admin_accessToken', access)
    localStorage.setItem('admin_refreshToken', refresh)
  }

  function logout() {
    accessToken.value = null
    refreshToken.value = null
    user.value = null
    localStorage.removeItem('admin_accessToken')
    localStorage.removeItem('admin_refreshToken')
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
    login,
    logout,
    fetchMe,
    setTokens,
  }
})

