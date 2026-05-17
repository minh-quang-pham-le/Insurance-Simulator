import { defineStore } from 'pinia'
import insuranceService from '../services/insuranceService'

export const useAdminInsuranceStore = defineStore('admin-insurance', {
  state: () => ({
    products: [],
    currentProduct: null,
    isLoading: false,
    error: null,
  }),

  actions: {
    async fetchProducts() {
      this.isLoading = true
      this.error = null
      try {
        const data = await insuranceService.getProducts()
        this.products = data.products
      } catch (err) {
        this.error = err.response?.data?.detail || 'Lỗi khi tải danh sách sản phẩm'
      } finally {
        this.isLoading = false
      }
    },

    async toggleProductStatus(id, currentStatus) {
      try {
        const updated = await insuranceService.updateProductStatus(id, !currentStatus)
        const index = this.products.findIndex(p => p.id === id)
        if (index !== -1) {
          this.products[index].is_active = updated.is_active
        }
      } catch (err) {
        alert(err.response?.data?.detail || 'Lỗi khi cập nhật trạng thái')
      }
    }
  }
})