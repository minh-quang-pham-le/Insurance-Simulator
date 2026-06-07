<template>
  <div class="p-6 space-y-6">
    <div class="flex justify-between items-center">
      <h1 class="text-2xl font-bold text-gray-900">Risk Analytics</h1>
      <button
        @click="loadData"
        :disabled="loading"
        class="px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700 disabled:opacity-50 transition"
      >
        {{ loading ? 'Loading...' : 'Refresh' }}
      </button>
    </div>

    <div v-if="loading" class="flex justify-center py-20">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
    </div>

    <template v-else-if="data">
      <!-- Overview Cards -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div class="bg-white rounded-xl border border-gray-200 p-5">
          <p class="text-sm text-gray-500">Total Policies</p>
          <p class="text-2xl font-bold text-gray-900">{{ data.total_policies }}</p>
        </div>
        <div class="bg-white rounded-xl border border-gray-200 p-5">
          <p class="text-sm text-gray-500">Premiums Collected</p>
          <p class="text-2xl font-bold text-green-600">{{ formatCurrency(data.total_premiums) }}</p>
        </div>
        <div class="bg-white rounded-xl border border-gray-200 p-5">
          <p class="text-sm text-gray-500">Claims Paid</p>
          <p class="text-2xl font-bold text-red-600">{{ formatCurrency(data.total_payouts) }}</p>
        </div>
        <div class="bg-white rounded-xl border border-gray-200 p-5">
          <p class="text-sm text-gray-500">Loss Ratio</p>
          <p class="text-2xl font-bold" :class="data.overall_loss_ratio > 1 ? 'text-red-600' : 'text-blue-600'">
            {{ (data.overall_loss_ratio * 100).toFixed(1) }}%
          </p>
        </div>
      </div>

      <!-- Charts Row -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Revenue vs Payouts Chart -->
        <div class="bg-white rounded-xl border border-gray-200 p-5">
          <h3 class="font-semibold text-gray-800 mb-4">Revenue vs Payouts (Monthly)</h3>
          <apexchart
            type="area"
            height="280"
            :options="revenueChartOptions"
            :series="revenueChartSeries"
          />
        </div>

        <!-- Category Distribution -->
        <div class="bg-white rounded-xl border border-gray-200 p-5">
          <h3 class="font-semibold text-gray-800 mb-4">Policy Distribution by Category</h3>
          <apexchart
            type="donut"
            height="280"
            :options="categoryDonutOptions"
            :series="categoryDonutSeries"
          />
        </div>
      </div>

      <!-- Category Risk Table -->
      <div class="bg-white rounded-xl border border-gray-200 p-5">
        <h3 class="font-semibold text-gray-800 mb-4">Risk Statistics by Category</h3>
        <div class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-4 py-3 text-left font-medium text-gray-500">Category</th>
                <th class="px-4 py-3 text-right font-medium text-gray-500">Events</th>
                <th class="px-4 py-3 text-right font-medium text-gray-500">Avg Severity</th>
                <th class="px-4 py-3 text-right font-medium text-gray-500">Probability</th>
                <th class="px-4 py-3 text-right font-medium text-gray-500">Policies</th>
                <th class="px-4 py-3 text-right font-medium text-gray-500">Premiums</th>
                <th class="px-4 py-3 text-right font-medium text-gray-500">Payouts</th>
                <th class="px-4 py-3 text-right font-medium text-gray-500">Loss Ratio</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100">
              <tr v-for="cat in data.category_stats" :key="cat.category" class="hover:bg-gray-50">
                <td class="px-4 py-3 font-medium text-gray-800">{{ formatCategory(cat.category) }}</td>
                <td class="px-4 py-3 text-right text-gray-600">{{ cat.total_events }}</td>
                <td class="px-4 py-3 text-right text-gray-600">{{ cat.avg_severity?.toFixed(1) ?? '-' }}</td>
                <td class="px-4 py-3 text-right">
                  <span :class="probabilityColor(cat.event_probability)">
                    {{ (cat.event_probability * 100).toFixed(1) }}%
                  </span>
                </td>
                <td class="px-4 py-3 text-right text-gray-600">{{ cat.total_policies }}</td>
                <td class="px-4 py-3 text-right text-green-600">{{ formatCurrency(cat.total_premiums) }}</td>
                <td class="px-4 py-3 text-right text-red-600">{{ formatCurrency(cat.total_payouts) }}</td>
                <td class="px-4 py-3 text-right">
                  <span :class="cat.loss_ratio > 1 ? 'text-red-600 font-bold' : 'text-gray-600'">
                    {{ (cat.loss_ratio * 100).toFixed(1) }}%
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Claims & Policies Monthly Chart -->
      <div class="bg-white rounded-xl border border-gray-200 p-5">
        <h3 class="font-semibold text-gray-800 mb-4">Policies Sold & Claims (Monthly)</h3>
        <apexchart
          type="bar"
          height="280"
          :options="claimsChartOptions"
          :series="claimsChartSeries"
        />
      </div>

      <!-- Regional Risk Data -->
      <div v-if="data.region_stats.length > 0" class="bg-white rounded-xl border border-gray-200 p-5">
        <h3 class="font-semibold text-gray-800 mb-4">Risk Events by Region</h3>
        <apexchart
          type="bar"
          height="280"
          :options="regionChartOptions"
          :series="regionChartSeries"
        />
      </div>

    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import adminService from '../services/adminService'

const loading = ref(true)
const data = ref(null)

onMounted(() => loadData())

async function loadData() {
  loading.value = true
  try {
    data.value = await adminService.getRiskAnalytics()
  } catch (err) {
    console.error('Failed to load risk analytics:', err)
  } finally {
    loading.value = false
  }
}

function formatCurrency(val) {
  return (val || 0).toLocaleString('en-US', { maximumFractionDigits: 0 }) + ' SC'
}

function formatCategory(cat) {
  return cat.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}

function probabilityColor(prob) {
  if (prob < 0.15) return 'text-green-600'
  if (prob < 0.40) return 'text-yellow-600'
  return 'text-red-600 font-bold'
}

// Revenue chart
const revenueChartOptions = computed(() => ({
  chart: { toolbar: { show: false }, fontFamily: 'inherit' },
  colors: ['#10b981', '#ef4444'],
  stroke: { curve: 'smooth', width: 2 },
  fill: { type: 'gradient', gradient: { opacityFrom: 0.4, opacityTo: 0.05 } },
  xaxis: {
    categories: (data.value?.monthly_trends || []).map(t => t.month),
    labels: { style: { fontSize: '11px' } },
  },
  yaxis: { labels: { formatter: v => v.toLocaleString() + ' SC' } },
  tooltip: { y: { formatter: v => v.toLocaleString() + ' SC' } },
  legend: { position: 'top' },
}))

const revenueChartSeries = computed(() => [
  { name: 'Premiums', data: (data.value?.monthly_trends || []).map(t => t.premiums) },
  { name: 'Payouts', data: (data.value?.monthly_trends || []).map(t => t.payouts) },
])

// Category donut
const categoryDonutOptions = computed(() => ({
  chart: { fontFamily: 'inherit' },
  labels: (data.value?.category_stats || []).map(c => formatCategory(c.category)),
  colors: ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'],
  legend: { position: 'bottom', fontSize: '12px' },
  dataLabels: { enabled: true, formatter: (v) => v.toFixed(0) + '%' },
}))

const categoryDonutSeries = computed(() =>
  (data.value?.category_stats || []).map(c => c.total_policies)
)

// Claims/Policies bar chart
const claimsChartOptions = computed(() => ({
  chart: { toolbar: { show: false }, fontFamily: 'inherit' },
  colors: ['#6366f1', '#f97316'],
  plotOptions: { bar: { borderRadius: 4, columnWidth: '60%' } },
  xaxis: {
    categories: (data.value?.monthly_trends || []).map(t => t.month),
    labels: { style: { fontSize: '11px' } },
  },
  legend: { position: 'top' },
}))

const claimsChartSeries = computed(() => [
  { name: 'Policies Sold', data: (data.value?.monthly_trends || []).map(t => t.policies_sold) },
  { name: 'Claims', data: (data.value?.monthly_trends || []).map(t => t.claims_count) },
])

// Regional bar chart
const regionChartOptions = computed(() => ({
  chart: { toolbar: { show: false }, fontFamily: 'inherit' },
  colors: ['#3b82f6'],
  plotOptions: { bar: { horizontal: true, borderRadius: 4 } },
  xaxis: { title: { text: 'Event Count' } },
  yaxis: { labels: { style: { fontSize: '11px' } } },
}))

const regionChartSeries = computed(() => [{
  name: 'Events',
  data: (data.value?.region_stats || []).map(r => ({
    x: r.region,
    y: r.event_count,
  })),
}])
</script>
