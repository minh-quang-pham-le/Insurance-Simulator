import api from './api'

export default {
  getConfig(productId) {
    return api.get(`/simulation/products/${productId}/config`)
  },

  checkTrigger(productId, parameters) {
    return api.post(`/simulation/products/${productId}/check-trigger`, { parameters })
  },

  logSession(productId, inputParameters, triggersActivated) {
    return api.post(`/simulation/products/${productId}/log`, {
      input_parameters: inputParameters,
      triggers_activated: triggersActivated,
    })
  },
}
