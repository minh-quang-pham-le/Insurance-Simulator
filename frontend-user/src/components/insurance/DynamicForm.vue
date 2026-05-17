<template>
  <form @submit.prevent="handleSubmit" class="space-y-4">
    <div v-for="field in schema.fields" :key="field.name" class="flex flex-col gap-1">
      <label :for="field.name" class="text-sm font-medium text-gray-700">
        {{ field.label }} <span v-if="field.required" class="text-red-500">*</span>
      </label>

      <input 
        v-if="field.type === 'string'"
        type="text"
        :id="field.name"
        v-model="formData[field.name]"
        :placeholder="field.placeholder"
        :required="field.required"
        class="border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
      />

      <input 
        v-else-if="field.type === 'number'"
        type="number"
        :id="field.name"
        v-model.number="formData[field.name]"
        :min="field.min"
        :max="field.max"
        :step="field.step"
        :required="field.required"
        class="border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
      />

      <input 
        v-else-if="field.type === 'date'"
        type="date"
        :id="field.name"
        v-model="formData[field.name]"
        :required="field.required"
        class="border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
      />

      <select 
        v-else-if="field.type === 'select'"
        :id="field.name"
        v-model="formData[field.name]"
        :required="field.required"
        class="border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none bg-white"
      >
        <option value="" disabled selected>Chọn {{ field.label.toLowerCase() }}</option>
        <option v-for="opt in field.options" :key="opt.value" :value="opt.value">
          {{ opt.label }}
        </option>
      </select>
    </div>

    <button 
      type="submit"
      class="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-4 rounded-lg transition-colors mt-6"
    >
      Tính Toán Phí Bảo Hiểm
    </button>
  </form>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  schema: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['submit'])

const formData = ref({})

// Khởi tạo giá trị mặc định từ schema
const initFormData = () => {
  const initialData = {}
  if (props.schema && props.schema.fields) {
    props.schema.fields.forEach(field => {
      initialData[field.name] = field.default !== undefined ? field.default : ''
    })
  }
  formData.value = initialData
}

watch(() => props.schema, initFormData, { immediate: true })

const handleSubmit = () => {
  emit('submit', formData.value)
}
</script>