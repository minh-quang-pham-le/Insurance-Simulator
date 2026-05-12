import { defineStore } from 'pinia'
import insuranceService from '../services/insuranceService'

export const useInsuranceStore = defineStore('insurance', {
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
        this.error = err.response?.data?.detail || 'Failed to load products'
        console.error('Error fetching products:', err)
      } finally {
        this.isLoading = false
      }
    },

    async fetchProductById(id) {
      this.isLoading = true
      this.error = null
      try {
        const data = await insuranceService.getProduct(id)
        this.currentProduct = data
        return data
      } catch (err) {
        this.error = err.response?.data?.detail || 'Failed to load product details'
        console.error(`Error fetching product ${id}:`, err)
        throw err
      } finally {
        this.isLoading = false
      }
    },
    
    clearCurrentProduct() {
      this.currentProduct = null
    }
  }
})