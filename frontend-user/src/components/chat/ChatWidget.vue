<template>
  <!-- Floating toggle button -->
  <button
    v-if="!isOpen"
    @click="isOpen = true"
    class="fixed bottom-6 right-6 z-50 w-14 h-14 bg-blue-600 hover:bg-blue-700 text-white rounded-full shadow-lg flex items-center justify-center transition-transform hover:scale-105"
    title="Chat with AI Advisor"
  >
    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
        d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
    </svg>
  </button>

  <!-- Chat panel -->
  <Transition name="chat-slide">
    <div
      v-if="isOpen"
      class="fixed bottom-6 right-6 z-50 w-96 h-[520px] bg-white rounded-2xl shadow-2xl border border-gray-200 flex flex-col overflow-hidden"
    >
      <!-- Header -->
      <div class="bg-blue-600 text-white px-4 py-3 flex items-center justify-between shrink-0">
        <div class="flex items-center gap-2">
          <div class="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center text-sm">AI</div>
          <div>
            <p class="font-semibold text-sm">Insurance Advisor</p>
            <p class="text-[10px] text-blue-200">Powered by Gemini</p>
          </div>
        </div>
        <button @click="isOpen = false" class="hover:bg-blue-500 rounded-lg p-1 transition">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Messages area -->
      <div ref="messagesContainer" class="flex-1 overflow-y-auto px-4 py-3 space-y-3">
        <!-- Welcome message if empty -->
        <div v-if="messages.length === 0" class="text-center py-8 text-gray-400">
          <div class="text-3xl mb-2">💬</div>
          <p class="text-sm">Ask me anything about insurance products, risk levels, or how to choose the right coverage.</p>
        </div>

        <ChatMessage v-for="(msg, i) in messages" :key="i" :msg="msg" />

        <!-- Typing indicator -->
        <div v-if="isLoading" class="flex justify-start">
          <div class="bg-gray-100 rounded-2xl rounded-bl-md px-4 py-3">
            <div class="flex gap-1">
              <span class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0ms"></span>
              <span class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 150ms"></span>
              <span class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 300ms"></span>
            </div>
          </div>
        </div>
      </div>

      <!-- Input area -->
      <div class="border-t border-gray-100 px-3 py-2 shrink-0">
        <form @submit.prevent="sendMessage" class="flex gap-2">
          <input
            ref="inputRef"
            v-model="inputText"
            type="text"
            placeholder="Type your question..."
            class="flex-1 px-3 py-2 text-sm border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            :disabled="isLoading"
          />
          <button
            type="submit"
            :disabled="!inputText.trim() || isLoading"
            class="px-3 py-2 bg-blue-600 text-white rounded-xl hover:bg-blue-700 disabled:opacity-40 disabled:cursor-not-allowed transition"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
          </button>
        </form>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { ref, nextTick, watch } from 'vue'
import chatService from '../../services/chatService'
import ChatMessage from './ChatMessage.vue'

const props = defineProps({
  productId: { type: String, default: null },
})

const isOpen = ref(false)
const inputText = ref('')
const messages = ref([])
const sessionId = ref(null)
const isLoading = ref(false)
const messagesContainer = ref(null)
const inputRef = ref(null)

// Auto-focus input when opened
watch(isOpen, async (open) => {
  if (open) {
    await nextTick()
    inputRef.value?.focus()
  }
})

async function scrollToBottom() {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

async function sendMessage() {
  const text = inputText.value.trim()
  if (!text || isLoading.value) return

  // Add user message to UI immediately
  messages.value.push({
    role: 'user',
    content: text,
    timestamp: new Date().toISOString(),
  })
  inputText.value = ''
  isLoading.value = true
  await scrollToBottom()

  try {
    const { data } = await chatService.sendMessage(
      text,
      sessionId.value,
      props.productId,
    )
    sessionId.value = data.session_id
    messages.value.push({
      role: 'assistant',
      content: data.content,
      timestamp: data.timestamp,
    })
  } catch (err) {
    messages.value.push({
      role: 'assistant',
      content: 'Sorry, I encountered an error. Please try again.',
      timestamp: new Date().toISOString(),
    })
  } finally {
    isLoading.value = false
    await scrollToBottom()
  }
}
</script>

<style scoped>
.chat-slide-enter-active,
.chat-slide-leave-active {
  transition: all 0.25s ease;
}
.chat-slide-enter-from,
.chat-slide-leave-to {
  opacity: 0;
  transform: translateY(20px) scale(0.95);
}
</style>
