import api from './api'

export const walletService = {
  /**
   * Get current wallet balance
   */
  async getBalance() {
    const response = await api.get('/wallet/')
    return response.data
  },

  /**
   * Top up wallet
   * @param amount - Amount in SimCoin
   * @returns Updated balance info
   */
  async topUp(amount) {
    const response = await api.post('/wallet/topup', {
      amount: parseFloat(amount)
    })
    return response.data
  },

  /**
   * Get transaction history
   * @param skip - Number of transactions to skip (pagination)
   * @param limit - Number of transactions to return
   * @returns Transaction list with pagination info
   */
  async getTransactions(skip = 0, limit = 50) {
    const response = await api.get('/wallet/transactions', {
      params: { skip, limit }
    })
    return response.data
  }
}
