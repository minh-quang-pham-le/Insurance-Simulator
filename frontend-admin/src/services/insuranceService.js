import api from './api'

const insuranceService = {
  // Lấy toàn bộ sản phẩm (kể cả inactive)
  async getProducts() {
    const response = await api.get('/insurance/products?include_inactive=true')
    return response.data
  },

  async getProduct(id) {
    const response = await api.get(`/insurance/products/${id}`)
    return response.data
  },

  async createProduct(productData) {
    const response = await api.post('/insurance/products', productData)
    return response.data
  },

  async updateProduct(id, productData) {
    const response = await api.put(`/insurance/products/${id}`, productData)
    return response.data
  },

  async updateProductStatus(id, isActive) {
    const response = await api.patch(`/insurance/products/${id}/status`, { is_active: isActive })
    return response.data
  }
}

export default insuranceService