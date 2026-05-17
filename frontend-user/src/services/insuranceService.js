import api from './api'

const insuranceService = {
  /**
   * Lấy danh sách sản phẩm bảo hiểm
   * @returns {Promise<Object>} Data chứa mảng products
   */
  async getProducts() {
    // User mặc định chỉ lấy product active, không cần truyền include_inactive
    const response = await api.get('/insurance/products')
    return response.data
  },

  /**
   * Lấy chi tiết một sản phẩm theo ID
   * @param {String} id - UUID của sản phẩm
   * @returns {Promise<Object>} Chi tiết sản phẩm
   */
  async getProduct(id) {
    const response = await api.get(`/insurance/products/${id}`)
    return response.data
  }
}

export default insuranceService