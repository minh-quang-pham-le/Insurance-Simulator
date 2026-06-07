import api from './api'

export const monitorService = {
  getHanoiWeather() {
    return api.get('/monitor/weather/hanoi')
  },
  getApiStatus() {
    return api.get('/monitor/status')
  },
  getLogs(params = {}) {
    return api.get('/monitor/logs', { params })
  },
  runCheck() {
    return api.post('/monitor/run-check')
  },
}
