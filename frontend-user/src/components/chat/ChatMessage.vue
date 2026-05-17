<template>
  <div :class="['flex', msg.role === 'user' ? 'justify-end' : 'justify-start']">
    <div
      :class="[
        'max-w-[80%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed',
        msg.role === 'user'
          ? 'bg-blue-600 text-white rounded-br-md'
          : 'bg-gray-100 text-gray-800 rounded-bl-md'
      ]"
    >
      <p class="whitespace-pre-wrap">{{ msg.content }}</p>
      <span
        :class="[
          'block text-[10px] mt-1',
          msg.role === 'user' ? 'text-blue-200' : 'text-gray-400'
        ]"
      >
        {{ formatTime(msg.timestamp) }}
      </span>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  msg: { type: Object, required: true },
})

function formatTime(ts) {
  if (!ts) return ''
  const d = new Date(ts)
  return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}
</script>
