<template>
  <!-- Gradient variant -->
  <div
    v-if="variant === 'gradient'"
    :class="['rounded-2xl p-5 text-white relative overflow-hidden shadow-lg', GRADIENT_MAP[color] || GRADIENT_MAP.indigo]"
  >
    <!-- Decorative blobs -->
    <div class="absolute -right-5 -top-5 w-28 h-28 bg-white/10 rounded-full pointer-events-none"></div>
    <div class="absolute right-8 bottom-3 w-14 h-14 bg-white/8 rounded-full pointer-events-none"></div>

    <div class="relative z-10 flex flex-col h-full">
      <div class="flex items-start justify-between mb-4">
        <p class="text-white/70 text-[11px] font-bold uppercase tracking-wider leading-tight">{{ label }}</p>
        <div class="w-9 h-9 bg-white/20 rounded-xl flex items-center justify-center flex-shrink-0">
          <svg class="w-4.5 h-4.5 text-white" fill="none" stroke="currentColor" stroke-width="1.75"
               stroke-linecap="round" stroke-linejoin="round" viewBox="0 0 24 24">
            <path :d="iconPath" />
          </svg>
        </div>
      </div>
      <p class="text-3xl font-black tabular-nums leading-none">{{ formattedValue }}</p>
      <p v-if="subtext" class="text-white/60 text-[11px] mt-2 font-medium">{{ subtext }}</p>
    </div>
  </div>

  <!-- Default variant (white card) -->
  <div
    v-else
    :class="['bg-white rounded-2xl border-l-4 border border-slate-100 shadow-sm p-5 hover:shadow-md transition-shadow', LEFT_BORDER_MAP[color] || LEFT_BORDER_MAP.slate]"
  >
    <div class="flex items-start justify-between gap-3">
      <div class="flex-1 min-w-0">
        <p class="text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-2">{{ label }}</p>
        <p class="text-2xl font-black tabular-nums leading-none" :class="valueClass || colorTextMap[color] || 'text-slate-900'">
          {{ formattedValue }}
        </p>
        <p v-if="subtext" class="text-[11px] text-slate-400 mt-2 font-medium">{{ subtext }}</p>
      </div>
      <div :class="['w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0', COLOR_MAP[color]?.bg || 'bg-slate-100']">
        <svg class="w-5 h-5" :class="COLOR_MAP[color]?.text || 'text-slate-500'"
             fill="none" stroke="currentColor" stroke-width="1.75"
             stroke-linecap="round" stroke-linejoin="round" viewBox="0 0 24 24">
          <path :d="iconPath" />
        </svg>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  label:     String,
  value:     [Number, String],
  icon:      { type: String, default: 'chart' },
  format:    { type: String, default: 'number' },
  color:     { type: String, default: 'slate' },
  variant:   { type: String, default: 'default' }, // 'default' | 'gradient'
  valueClass:{ type: String, default: null },
  iconBg:    { type: String, default: null },
  subtext:   { type: String, default: null },
})

const formattedValue = computed(() => {
  if (props.value === null || props.value === undefined) return '—'
  if (props.format === 'currency') return `${Number(props.value).toLocaleString('vi-VN')} SC`
  if (props.format === 'percent')  return `${(Number(props.value) * 100).toFixed(1)}%`
  return Number(props.value).toLocaleString('vi-VN')
})

const GRADIENT_MAP = {
  blue:    'bg-gradient-to-br from-blue-500 to-blue-700',
  indigo:  'bg-gradient-to-br from-indigo-500 to-violet-600',
  emerald: 'bg-gradient-to-br from-emerald-500 to-teal-600',
  green:   'bg-gradient-to-br from-emerald-500 to-teal-600',
  amber:   'bg-gradient-to-br from-amber-400 to-orange-500',
  red:     'bg-gradient-to-br from-red-500 to-rose-600',
  violet:  'bg-gradient-to-br from-violet-500 to-purple-700',
  teal:    'bg-gradient-to-br from-teal-500 to-cyan-600',
  slate:   'bg-gradient-to-br from-slate-600 to-slate-800',
}

const LEFT_BORDER_MAP = {
  blue:    'border-l-blue-500',
  indigo:  'border-l-indigo-500',
  emerald: 'border-l-emerald-500',
  green:   'border-l-emerald-500',
  amber:   'border-l-amber-500',
  red:     'border-l-red-500',
  violet:  'border-l-violet-500',
  teal:    'border-l-teal-500',
  slate:   'border-l-slate-400',
}

const COLOR_MAP = {
  blue:    { bg: 'bg-blue-50',    text: 'text-blue-600' },
  indigo:  { bg: 'bg-indigo-50',  text: 'text-indigo-600' },
  emerald: { bg: 'bg-emerald-50', text: 'text-emerald-600' },
  green:   { bg: 'bg-emerald-50', text: 'text-emerald-600' },
  amber:   { bg: 'bg-amber-50',   text: 'text-amber-600' },
  red:     { bg: 'bg-red-50',     text: 'text-red-500' },
  violet:  { bg: 'bg-violet-50',  text: 'text-violet-600' },
  teal:    { bg: 'bg-teal-50',    text: 'text-teal-600' },
  slate:   { bg: 'bg-slate-100',  text: 'text-slate-500' },
}

const colorTextMap = {
  blue:    'text-blue-700',
  indigo:  'text-indigo-700',
  emerald: 'text-emerald-700',
  green:   'text-emerald-700',
  amber:   'text-amber-700',
  red:     'text-red-600',
  violet:  'text-violet-700',
  teal:    'text-teal-700',
}

const ICON_PATHS = {
  users:          'M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z',
  shield:         'M12 3l8 3v6c0 4.418-3.582 8-8 9-4.418-1-8-4.582-8-9V6l8-3z',
  currency:       'M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z',
  clipboard:      'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4',
  'trending-up':  'M13 7h8m0 0v8m0-8l-8 8-4-4-6 6',
  payout:         'M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z',
  chart:          'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z',
  'user-plus':    'M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z',
  'check-circle': 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z',
  activity:       'M22 12h-4l-3 9L9 3l-3 9H2',
}

const iconPath = computed(() => ICON_PATHS[props.icon] || ICON_PATHS.chart)
</script>
