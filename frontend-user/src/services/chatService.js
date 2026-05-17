import api from './api'

export default {
  sendMessage(message, sessionId = null, contextProductId = null) {
    const payload = { message }
    if (sessionId) payload.session_id = sessionId
    if (contextProductId) payload.context_product_id = contextProductId
    return api.post('/chat/message', payload)
  },

  getSessions(skip = 0, limit = 20) {
    return api.get('/chat/sessions', { params: { skip, limit } })
  },

  getSession(sessionId) {
    return api.get(`/chat/sessions/${sessionId}`)
  },
}
