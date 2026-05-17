<template>
  <div class="p-6 max-w-4xl mx-auto">
    <div class="flex items-center mb-6 gap-4">
      <router-link to="/products" class="text-gray-500 hover:text-gray-700">← Quay lại</router-link>
      <h1 class="text-2xl font-bold text-gray-900">{{ isEdit ? 'Chỉnh Sửa Sản Phẩm' : 'Thêm Sản Phẩm Mới' }}</h1>
    </div>

    <form @submit.prevent="submitForm" class="bg-white rounded-lg shadow p-6 space-y-6">
      
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Tên Sản Phẩm *</label>
          <input v-model="form.name" type="text" required class="w-full border border-gray-300 rounded-md px-3 py-2" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Danh Mục *</label>
          <select v-model="form.category" required class="w-full border border-gray-300 rounded-md px-3 py-2 bg-white">
            <option value="FLIGHT_DELAY">FLIGHT_DELAY</option>
            <option value="CROP_WEATHER">CROP_WEATHER</option>
            <option value="GADGET">GADGET</option>
            <option value="NATURAL_DISASTER">NATURAL_DISASTER</option>
            <option value="RAINFALL_EVENT">RAINFALL_EVENT</option>
          </select>
        </div>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Mô tả chi tiết *</label>
        <textarea v-model="form.description" required rows="3" class="w-full border border-gray-300 rounded-md px-3 py-2"></textarea>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Bồi thường (SC) *</label>
          <input v-model.number="form.base_payout" type="number" required min="1" class="w-full border border-gray-300 rounded-md px-3 py-2" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Biên lợi nhuận *</label>
          <input v-model.number="form.risk_margin" type="number" step="0.01" required min="0" max="1" class="w-full border border-gray-300 rounded-md px-3 py-2" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Thời hạn Min (Ngày)*</label>
          <input v-model.number="form.min_duration_days" type="number" required min="1" class="w-full border border-gray-300 rounded-md px-3 py-2" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Thời hạn Max (Ngày)*</label>
          <input v-model.number="form.max_duration_days" type="number" required min="1" class="w-full border border-gray-300 rounded-md px-3 py-2" />
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Parameters Schema (JSON) *</label>
          <textarea v-model="schemaString" required rows="8" class="w-full border border-gray-300 rounded-md px-3 py-2 font-mono text-sm" placeholder='{"fields": []}'></textarea>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Trigger Conditions (JSON) *</label>
          <textarea v-model="triggerString" required rows="8" class="w-full border border-gray-300 rounded-md px-3 py-2 font-mono text-sm" placeholder='{"type": "PARAMETRIC", "rules": []}'></textarea>
        </div>
      </div>

      <div class="flex justify-end pt-4 border-t">
        <button type="submit" :disabled="isSubmitting" class="bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-2 px-6 rounded-md transition-colors disabled:opacity-50">
          {{ isSubmitting ? 'Đang lưu...' : 'Lưu Sản Phẩm' }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import insuranceService from '../services/insuranceService'

const route = useRoute()
const router = useRouter()
const isEdit = computed(() => !!route.params.id)
const isSubmitting = ref(false)

// Các string để chứa JSON thô từ textarea
const schemaString = ref('')
const triggerString = ref('')

const form = ref({
  name: '',
  category: 'FLIGHT_DELAY',
  description: '',
  base_payout: 500,
  risk_margin: 0.25,
  min_duration_days: 1,
  max_duration_days: 7
})

onMounted(async () => {
  if (isEdit.value) {
    try {
      const data = await insuranceService.getProduct(route.params.id)
      form.value = { ...data }
      // Chuyển Object JSON thành chuỗi để hiển thị trên textarea
      schemaString.value = JSON.stringify(data.parameters_schema, null, 2)
      triggerString.value = JSON.stringify(data.trigger_conditions, null, 2)
    } catch (error) {
      alert('Không thể tải dữ liệu sản phẩm')
      router.push('/products')
    }
  }
})

const submitForm = async () => {
  isSubmitting.value = true
  try {
    // Parse JSON từ textarea thành Object trước khi gửi xuống Backend
    const payload = {
      ...form.value,
      parameters_schema: JSON.parse(schemaString.value),
      trigger_conditions: JSON.parse(triggerString.value)
    }

    if (isEdit.value) {
      await insuranceService.updateProduct(route.params.id, payload)
    } else {
      await insuranceService.createProduct(payload)
    }
    
    alert('Lưu thành công!')
    router.push('/products')
  } catch (error) {
    if (error instanceof SyntaxError) {
      alert('Lỗi: Cấu trúc JSON không hợp lệ. Vui lòng kiểm tra lại Parameters Schema hoặc Trigger Conditions.')
    } else {
      alert(error.response?.data?.detail || 'Có lỗi xảy ra khi lưu.')
    }
  } finally {
    isSubmitting.value = false
  }
}
</script>