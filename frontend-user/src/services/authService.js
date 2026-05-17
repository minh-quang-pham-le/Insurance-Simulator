import api from './api'

export const authService = {
  register(email, password, fullName) {
    return api.post('/auth/register', {
      email,
      password,
      full_name: fullName
    })
  },

  login(email, password) {
    return api.post('/auth/login', {
      email,
      password
    })
  },

  refreshToken(refreshToken) {
    return api.post('/auth/refresh', {
      refresh_token: refreshToken
    })
  },

  getMe() {
    return api.get('/auth/me')
  },

  submitKyc(phoneNumber, identityDetails) {
    return api.post('/auth/kyc/submit', {
      phone_number: phoneNumber,
      identity_details: identityDetails
    })
  },

  getKycStatus() {
    return api.get('/auth/kyc/status')
  }
}

export default authService
