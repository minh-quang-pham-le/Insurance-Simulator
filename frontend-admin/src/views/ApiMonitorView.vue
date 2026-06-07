<template>
  <div class="p-6 space-y-6">
    <!-- Header -->
    <div class="flex justify-between items-center">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">API Monitor</h1>
        <p class="text-sm text-gray-500 mt-1">Theo dõi external APIs và trigger tự động</p>
      </div>
      <button
        @click="runManualCheck"
        :disabled="checking"
        class="px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700 disabled:opacity-50 transition flex items-center gap-2"
      >
        <span v-if="checking" class="animate-spin inline-block">⏳</span>
        {{ checking ? 'Đang kiểm tra...' : 'Chạy Trigger Check' }}
      </button>
    </div>

    <!-- Last check result banner -->
    <div v-if="lastCheckResult" class="bg-green-50 border border-green-200 rounded-xl p-4 text-sm text-green-800">
      Kết quả lần cuối: kiểm tra <strong>{{ lastCheckResult.checked }}</strong> policy,
      triggered <strong>{{ lastCheckResult.triggered }}</strong>,
      lỗi <strong>{{ lastCheckResult.errors }}</strong>
    </div>

    <!-- Hanoi Weather Card -->
    <div class="bg-white rounded-xl border border-gray-200 p-5">
      <div class="flex justify-between items-center mb-4">
        <h2 class="text-lg font-semibold text-gray-800">Thời tiết Hà Nội (OpenWeatherMap)</h2>
        <button @click="loadWeather" class="text-indigo-600 text-sm hover:underline">Làm mới</button>
      </div>
      <div v-if="weatherLoading" class="flex justify-center py-8">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
      </div>
      <div v-else-if="weather" class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div class="text-center p-3 bg-orange-50 rounded-lg">
          <p class="text-2xl font-bold text-orange-600">{{ weather.temp_celsius?.toFixed(1) }}°C</p>
          <p class="text-xs text-gray-500 mt-1">Nhiệt độ</p>
        </div>
        <div class="text-center p-3 bg-blue-50 rounded-lg">
          <p class="text-2xl font-bold text-blue-600">{{ weather.rainfall_mm?.toFixed(1) }} mm</p>
          <p class="text-xs text-gray-500 mt-1">Lượng mưa (1h)</p>
        </div>
        <div class="text-center p-3 bg-teal-50 rounded-lg">
          <p class="text-2xl font-bold text-teal-600">{{ weather.humidity }}%</p>
          <p class="text-xs text-gray-500 mt-1">Độ ẩm</p>
        </div>
        <div class="text-center p-3 rounded-lg" :class="severityBg(weather.alert_severity)">
          <p class="text-2xl font-bold" :class="severityColor(weather.alert_severity)">
            {{ weather.alert_severity }}/5
          </p>
          <p class="text-xs text-gray-500 mt-1">Mức cảnh báo</p>
        </div>
        <div class="col-span-2 md:col-span-4 flex items-center gap-2 mt-1 flex-wrap">
          <span class="text-gray-500 text-sm capitalize">{{ weather.description }}</span>
          <span v-if="weather.is_mock" class="text-xs bg-yellow-100 text-yellow-700 px-2 py-0.5 rounded-full">mock</span>
          <span class="text-xs text-gray-400 ml-auto">
            {{ weather.location_name }} · {{ formatTime(weather.fetched_at) }}
          </span>
        </div>
      </div>
    </div>

    <!-- API Status Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div class="bg-white rounded-xl border border-gray-200 p-5">
        <div class="flex items-center justify-between mb-3">
          <h3 class="font-semibold text-gray-800">OpenWeatherMap</h3>
          <span :class="statusBadge(apiStatus.openweathermap?.status)">
            {{ apiStatus.openweathermap?.status ?? 'unknown' }}
          </span>
        </div>
        <div class="text-sm text-gray-600 space-y-1">
          <p>Khoá API:
            <span :class="apiStatus.config?.openweathermap_configured ? 'text-green-600 font-medium' : 'text-red-500'">
              {{ apiStatus.config?.openweathermap_configured ? 'Đã cấu hình' : 'Chưa cấu hình' }}
            </span>
          </p>
          <p v-if="apiStatus.openweathermap?.last_checked">
            Lần cuối: {{ formatTime(apiStatus.openweathermap.last_checked) }}
          </p>
          <p v-if="apiStatus.openweathermap?.response_time_ms">
            Phản hồi: {{ apiStatus.openweathermap.response_time_ms }}ms
          </p>
          <p v-if="apiStatus.openweathermap?.error" class="text-red-500 text-xs">
            {{ apiStatus.openweathermap.error }}
          </p>
        </div>
      </div>

      <div class="bg-white rounded-xl border border-gray-200 p-5">
        <div class="flex items-center justify-between mb-3">
          <h3 class="font-semibold text-gray-800">AviationStack</h3>
          <span :class="statusBadge(apiStatus.aviationstack?.status)">
            {{ apiStatus.aviationstack?.status ?? 'unknown' }}
          </span>
        </div>
        <div class="text-sm text-gray-600 space-y-1">
          <p>Khoá API:
            <span :class="apiStatus.config?.aviationstack_configured ? 'text-green-600 font-medium' : 'text-yellow-600'">
              {{ apiStatus.config?.aviationstack_configured ? 'Đã cấu hình' : 'Chưa cấu hình (mock mode)' }}
            </span>
          </p>
          <p v-if="apiStatus.aviationstack?.last_checked">
            Lần cuối: {{ formatTime(apiStatus.aviationstack.last_checked) }}
          </p>
          <p v-if="apiStatus.aviationstack?.response_time_ms">
            Phản hồi: {{ apiStatus.aviationstack.response_time_ms }}ms
          </p>
        </div>
      </div>
    </div>

    <!-- Config info banner -->
    <div v-if="apiStatus.config" class="bg-indigo-50 border border-indigo-100 rounded-xl p-4 text-sm text-indigo-800">
      Trigger monitor chạy tự động mỗi
      <strong>{{ apiStatus.config.trigger_interval_minutes }} phút</strong>
      — kiểm tra tất cả policy ACTIVE và tự động chi trả khi điều kiện thỏa mãn.
    </div>

    <!-- Logs Table -->
    <div class="bg-white rounded-xl border border-gray-200">
      <div class="flex items-center justify-between p-5 border-b border-gray-100">
        <h2 class="text-lg font-semibold text-gray-800">Lịch sử API calls</h2>
        <select
          v-model="logFilter"
          @change="loadLogs"
          class="text-sm border border-gray-200 rounded-lg px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-indigo-300"
        >
          <option value="">Tất cả</option>
          <option value="openweathermap">OpenWeatherMap</option>
          <option value="aviationstack">AviationStack</option>
        </select>
      </div>

      <div v-if="logsLoading" class="flex justify-center py-10">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
      </div>
      <div v-else-if="logs.length === 0" class="text-center py-10 text-gray-400 text-sm">
        Chưa có log nào. Nhấn "Chạy Trigger Check" để bắt đầu.
      </div>
      <div v-else class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="bg-gray-50 text-gray-500 text-xs uppercase">
            <tr>
              <th class="px-4 py-3 text-left">API</th>
              <th class="px-4 py-3 text-left">HTTP</th>
              <th class="px-4 py-3 text-left">Thời gian</th>
              <th class="px-4 py-3 text-left">Kết quả</th>
              <th class="px-4 py-3 text-left">Thời điểm</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <tr v-for="log in logs" :key="log.id" class="hover:bg-gray-50">
              <td class="px-4 py-3 font-medium text-gray-800">{{ log.api_name }}</td>
              <td class="px-4 py-3">
                <span :class="log.error_message ? 'text-red-600 font-semibold' : 'text-green-600 font-semibold'">
                  {{ log.status_code ?? '—' }}
                </span>
              </td>
              <td class="px-4 py-3 text-gray-600">{{ log.response_time_ms }}ms</td>
              <td class="px-4 py-3 text-gray-600 max-w-xs">
                <span v-if="log.error_message" class="text-red-500 text-xs line-clamp-1">{{ log.error_message }}</span>
                <span v-else-if="log.response_summary" class="text-xs">{{ formatSummary(log.response_summary) }}</span>
              </td>
              <td class="px-4 py-3 text-gray-400 text-xs whitespace-nowrap">{{ formatTime(log.checked_at) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { monitorService } from '../services/monitorService'

const weather = ref(null)
const weatherLoading = ref(false)
const apiStatus = ref({})
const logs = ref([])
const logsLoading = ref(false)
const logFilter = ref('')
const checking = ref(false)
const lastCheckResult = ref(null)

async function loadWeather() {
  weatherLoading.value = true
  try {
    const res = await monitorService.getHanoiWeather()
    weather.value = res.data
  } catch {
    weather.value = null
  } finally {
    weatherLoading.value = false
  }
}

async function loadStatus() {
  try {
    const res = await monitorService.getApiStatus()
    apiStatus.value = res.data
  } catch {
    apiStatus.value = {}
  }
}

async function loadLogs() {
  logsLoading.value = true
  try {
    const params = logFilter.value ? { api_name: logFilter.value } : {}
    const res = await monitorService.getLogs(params)
    logs.value = res.data
  } catch {
    logs.value = []
  } finally {
    logsLoading.value = false
  }
}

async function runManualCheck() {
  checking.value = true
  lastCheckResult.value = null
  try {
    const res = await monitorService.runCheck()
    lastCheckResult.value = res.data.summary
    await Promise.all([loadStatus(), loadLogs()])
  } catch {
    // ignore
  } finally {
    checking.value = false
  }
}

function statusBadge(status) {
  const base = 'text-xs font-medium px-2 py-0.5 rounded-full'
  if (status === 'ok') return `${base} bg-green-100 text-green-700`
  if (status === 'error') return `${base} bg-red-100 text-red-700`
  return `${base} bg-gray-100 text-gray-500`
}

function severityBg(level) {
  if (level >= 4) return 'bg-red-50'
  if (level >= 2) return 'bg-yellow-50'
  return 'bg-green-50'
}

function severityColor(level) {
  if (level >= 4) return 'text-red-600'
  if (level >= 2) return 'text-yellow-600'
  return 'text-green-600'
}

function formatTime(iso) {
  if (!iso) return '—'
  return new Date(iso).toLocaleString('vi-VN', { hour12: false })
}

function formatSummary(summary) {
  if (!summary) return ''
  if (summary.location) return `${summary.location} · ${summary.temp_celsius}°C · ${summary.rainfall_mm}mm`
  if (summary.flight) return `${summary.flight} → ${summary.status}`
  return JSON.stringify(summary).slice(0, 80)
}

onMounted(() => {
  loadWeather()
  loadStatus()
  loadLogs()
})
</script>
