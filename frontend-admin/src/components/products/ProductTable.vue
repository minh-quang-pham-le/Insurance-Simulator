<template>
  <div class="overflow-x-auto bg-white rounded-lg shadow border border-gray-200">
    <table class="min-w-full divide-y divide-gray-200">
      <thead class="bg-gray-50">
        <tr>
          <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Tên Sản Phẩm</th>
          <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Danh Mục</th>
          <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Phí Cơ Bản</th>
          <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Trạng Thái</th>
          <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Hành Động</th>
        </tr>
      </thead>
      <tbody class="bg-white divide-y divide-gray-200">
        <tr v-for="product in products" :key="product.id" class="hover:bg-gray-50">
          <td class="px-6 py-4 whitespace-nowrap">
            <div class="text-sm font-medium text-gray-900">{{ product.name }}</div>
          </td>
          <td class="px-6 py-4 whitespace-nowrap">
            <span class="px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">
              {{ product.category }}
            </span>
          </td>
          <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
            {{ product.base_payout }} SC
          </td>
          <td class="px-6 py-4 whitespace-nowrap">
            <button 
              @click="$emit('toggle-status', product.id, product.is_active)"
              :class="product.is_active ? 'bg-green-100 text-green-800 hover:bg-green-200' : 'bg-red-100 text-red-800 hover:bg-red-200'"
              class="px-3 py-1 rounded-full text-xs font-semibold transition-colors"
            >
              {{ product.is_active ? 'Đang Bán' : 'Ngừng Bán' }}
            </button>
          </td>
          <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
            <router-link :to="`/products/edit/${product.id}`" class="text-indigo-600 hover:text-indigo-900">
              Chỉnh Sửa
            </router-link>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
defineProps({
  products: {
    type: Array,
    required: true
  }
})
defineEmits(['toggle-status'])
</script>