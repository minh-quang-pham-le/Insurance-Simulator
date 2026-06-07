<template>
  <div class="min-h-screen flex overflow-hidden">

    <!-- ─── Left: Brand panel ─── -->
    <div class="hidden lg:flex lg:w-[55%] relative overflow-hidden bg-gradient-to-br from-indigo-700 via-blue-600 to-violet-700">

      <!-- Abstract blob shapes -->
      <div class="absolute -top-40 -left-40 w-[520px] h-[520px] bg-white/10 rounded-full"></div>
      <div class="absolute -bottom-28 -right-28 w-[420px] h-[420px] bg-teal-400/25 rounded-[60%_40%_30%_70%/60%_30%_70%_40%]"></div>
      <div class="absolute top-1/2 -left-20 w-56 h-56 bg-indigo-900/30 rounded-full blur-2xl"></div>
      <div class="absolute top-20 right-1/4 w-40 h-40 bg-blue-300/15 rounded-full blur-xl"></div>

      <!-- Floating icon cards -->
      <div class="absolute top-12 right-16 w-14 h-14 bg-white/15 backdrop-blur-sm border border-white/25 rounded-2xl flex items-center justify-center shadow-xl" style="animation: float 3s ease-in-out infinite;">
        <!-- Bar chart -->
        <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" stroke-width="1.75" viewBox="0 0 24 24">
          <rect x="3" y="12" width="4" height="9" rx="1"/><rect x="10" y="7" width="4" height="14" rx="1"/><rect x="17" y="3" width="4" height="18" rx="1"/>
        </svg>
      </div>
      <div class="absolute top-28 left-16 w-14 h-14 bg-white/15 backdrop-blur-sm border border-white/25 rounded-2xl flex items-center justify-center shadow-xl" style="animation: float 4s ease-in-out infinite; animation-delay: 0.6s;">
        <!-- Shield check -->
        <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" stroke-width="1.75" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 3l8 3v6c0 4.418-3.582 8-8 9-4.418-1-8-4.582-8-9V6l8-3z"/>
          <path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4"/>
        </svg>
      </div>
      <div class="absolute bottom-36 right-12 w-14 h-14 bg-white/15 backdrop-blur-sm border border-white/25 rounded-2xl flex items-center justify-center shadow-xl" style="animation: float 3.5s ease-in-out infinite; animation-delay: 1s;">
        <!-- Airplane -->
        <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" stroke-width="1.75" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z"/>
        </svg>
      </div>
      <div class="absolute bottom-20 left-20 w-14 h-14 bg-white/15 backdrop-blur-sm border border-white/25 rounded-2xl flex items-center justify-center shadow-xl" style="animation: float 4.5s ease-in-out infinite; animation-delay: 1.5s;">
        <!-- Sun / weather -->
        <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" stroke-width="1.75" viewBox="0 0 24 24">
          <circle cx="12" cy="12" r="4"/><path stroke-linecap="round" d="M12 2v2m0 16v2M4.22 4.22l1.42 1.42m12.72 12.72 1.42 1.42M2 12h2m16 0h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/>
        </svg>
      </div>

      <!-- Central content -->
      <div class="relative z-10 flex flex-col items-center justify-center w-full px-12 text-white">

        <!-- Logo -->
        <div class="flex items-center gap-3 mb-10">
          <div class="w-12 h-12 bg-white/20 border border-white/30 rounded-2xl flex items-center justify-center shadow-lg">
            <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" stroke-width="1.75" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 3l8 3v6c0 4.418-3.582 8-8 9-4.418-1-8-4.582-8-9V6l8-3z"/>
              <path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4"/>
            </svg>
          </div>
          <div>
            <p class="text-xl font-extrabold tracking-tight leading-tight">Insurance Simulator</p>
            <p class="text-blue-200 text-xs font-medium">Nền tảng bảo hiểm tham số hóa</p>
          </div>
        </div>

        <!-- Mock SimCoin card -->
        <div class="relative w-full max-w-sm">
          <!-- Shadow layer -->
          <div class="absolute inset-0 translate-y-5 translate-x-4 bg-black/20 rounded-3xl blur-md"></div>

          <!-- Main card -->
          <div class="relative bg-white/15 backdrop-blur-xl border border-white/25 rounded-3xl p-6 shadow-2xl">
            <!-- Balance row -->
            <div class="flex items-center justify-between mb-5">
              <div>
                <p class="text-[11px] text-blue-200 font-semibold uppercase tracking-wider mb-0.5">Ví SimCoin</p>
                <p class="text-4xl font-black tabular-nums leading-none">
                  2,500 <span class="text-xl font-bold text-blue-300">SC</span>
                </p>
              </div>
              <!-- Wallet icon -->
              <div class="w-12 h-12 bg-blue-400/30 border border-blue-300/20 rounded-2xl flex items-center justify-center">
                <svg class="w-6 h-6 text-blue-200" fill="none" stroke="currentColor" stroke-width="1.75" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M21 12V7a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v10a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-3"/>
                  <path stroke-linecap="round" stroke-linejoin="round" d="M16 12h5v4h-5a2 2 0 0 1 0-4z"/>
                </svg>
              </div>
            </div>

            <!-- Active policies -->
            <div class="grid grid-cols-2 gap-2.5 mb-4">
              <div class="bg-white/10 border border-white/15 rounded-2xl p-3">
                <p class="text-[10px] text-blue-200 mb-1.5 font-medium">Chuyến bay</p>
                <div class="flex items-center gap-1.5">
                  <svg class="w-3.5 h-3.5 text-white flex-shrink-0" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z"/>
                  </svg>
                  <span class="text-xs font-bold">VN123</span>
                  <span class="ml-auto text-[9px] bg-emerald-400/25 text-emerald-300 border border-emerald-400/20 px-1.5 py-0.5 rounded-full font-bold">ON</span>
                </div>
              </div>
              <div class="bg-white/10 border border-white/15 rounded-2xl p-3">
                <p class="text-[10px] text-blue-200 mb-1.5 font-medium">Thời tiết</p>
                <div class="flex items-center gap-1.5">
                  <svg class="w-3.5 h-3.5 text-white flex-shrink-0" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                    <circle cx="12" cy="12" r="4"/><path stroke-linecap="round" d="M12 2v2m0 16v2M4.22 4.22l1.42 1.42m12.72 12.72 1.42 1.42M2 12h2m16 0h2"/>
                  </svg>
                  <span class="text-xs font-bold">Hà Nội</span>
                  <span class="ml-auto text-[9px] bg-emerald-400/25 text-emerald-300 border border-emerald-400/20 px-1.5 py-0.5 rounded-full font-bold">ON</span>
                </div>
              </div>
            </div>

            <!-- Auto payout -->
            <div class="bg-emerald-400/15 border border-emerald-400/20 rounded-2xl p-3 flex items-center gap-2.5">
              <div class="w-8 h-8 bg-emerald-400/25 rounded-xl flex items-center justify-center flex-shrink-0">
                <svg class="w-4 h-4 text-emerald-300" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M12 6v12m-4-4l4 4 4-4"/>
                  <circle cx="12" cy="12" r="9"/>
                </svg>
              </div>
              <div>
                <p class="text-[11px] font-bold text-emerald-300">Bồi thường tự động</p>
                <p class="text-[10px] text-white/60">VN123 trễ 2h30 → <span class="text-emerald-300 font-bold">+500 SC</span></p>
              </div>
            </div>
          </div>
        </div>

        <!-- Tagline -->
        <p class="mt-8 text-center text-blue-200 text-sm leading-relaxed max-w-xs">
          Chi trả <strong class="text-white">tự động</strong> khi điều kiện kích hoạt —<br/>
          không paperwork, không chờ duyệt.
        </p>
      </div>
    </div>

    <!-- ─── Right: Login form ─── -->
    <div class="w-full lg:w-[45%] flex items-center justify-center bg-white px-6 py-12">
      <div class="w-full max-w-xs">

        <!-- Mobile logo -->
        <div class="flex items-center justify-center gap-2 mb-8 lg:hidden">
          <svg class="w-8 h-8 text-indigo-600" fill="none" stroke="currentColor" stroke-width="1.75" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 3l8 3v6c0 4.418-3.582 8-8 9-4.418-1-8-4.582-8-9V6l8-3z"/>
          </svg>
          <span class="text-xl font-extrabold text-slate-900">Insurance Simulator</span>
        </div>

        <!-- Heading -->
        <div class="mb-8">
          <h1 class="text-3xl font-extrabold text-slate-900 mb-2">Chào mừng!</h1>
          <p class="text-slate-500 text-sm leading-relaxed">
            Đăng nhập để quản lý hợp đồng bảo hiểm của bạn.
          </p>
        </div>

        <!-- Form -->
        <form @submit.prevent="handleLogin" class="space-y-4">
          <!-- Email -->
          <div>
            <label class="block text-[11px] font-bold text-slate-500 mb-1.5 uppercase tracking-wider">Email</label>
            <div class="relative">
              <span class="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="1.75" viewBox="0 0 24 24">
                  <rect x="2" y="4" width="20" height="16" rx="2"/><path stroke-linecap="round" stroke-linejoin="round" d="m2 7 10 7 10-7"/>
                </svg>
              </span>
              <input
                v-model="email"
                type="email"
                required
                placeholder="you@example.com"
                class="w-full border-2 border-slate-100 bg-slate-50 rounded-2xl pl-10 pr-4 py-3 text-sm focus:border-indigo-400 focus:bg-white outline-none transition-colors"
              />
            </div>
          </div>

          <!-- Password -->
          <div>
            <label class="block text-[11px] font-bold text-slate-500 mb-1.5 uppercase tracking-wider">Mật khẩu</label>
            <div class="relative">
              <span class="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="1.75" viewBox="0 0 24 24">
                  <rect x="3" y="11" width="18" height="11" rx="2"/><path stroke-linecap="round" stroke-linejoin="round" d="M7 11V7a5 5 0 0 1 10 0v4"/>
                </svg>
              </span>
              <input
                v-model="password"
                type="password"
                required
                placeholder="••••••••"
                class="w-full border-2 border-slate-100 bg-slate-50 rounded-2xl pl-10 pr-4 py-3 text-sm focus:border-indigo-400 focus:bg-white outline-none transition-colors"
              />
            </div>
          </div>

          <!-- Error -->
          <div
            v-if="error"
            class="bg-red-50 border border-red-100 text-red-600 text-xs p-3 rounded-2xl flex items-start gap-2"
          >
            <svg class="w-4 h-4 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v4m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/>
            </svg>
            <span>{{ error }}</span>
          </div>

          <!-- Submit -->
          <button
            type="submit"
            :disabled="loading"
            class="w-full bg-gradient-to-r from-indigo-600 to-blue-600 hover:from-indigo-700 hover:to-blue-700 active:scale-[0.98] text-white font-bold py-3.5 rounded-2xl transition-all disabled:opacity-50 disabled:cursor-not-allowed text-sm shadow-lg shadow-indigo-100 mt-1"
          >
            <span v-if="!loading" class="flex items-center justify-center gap-2">
              Đăng nhập
              <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M13.5 4.5 21 12m0 0-7.5 7.5M21 12H3"/>
              </svg>
            </span>
            <span v-else class="flex items-center justify-center gap-2">
              <svg class="animate-spin w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path stroke-linecap="round" d="M12 3a9 9 0 1 0 9 9"/>
              </svg>
              Đang xử lý...
            </span>
          </button>
        </form>

        <!-- Divider -->
        <div class="flex items-center gap-3 my-6">
          <div class="flex-1 h-px bg-slate-100"></div>
          <span class="text-xs text-slate-400 font-medium">hoặc</span>
          <div class="flex-1 h-px bg-slate-100"></div>
        </div>

        <!-- Register -->
        <p class="text-center text-slate-500 text-sm">
          Chưa có tài khoản?
          <router-link to="/register" class="text-indigo-600 hover:text-indigo-700 font-bold ml-1">
            Đăng ký miễn phí →
          </router-link>
        </p>

        <!-- Security note -->
        <p class="text-center text-[11px] text-slate-400 mt-6 flex items-center justify-center gap-1.5">
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <rect x="3" y="11" width="18" height="11" rx="2"/><path stroke-linecap="round" d="M7 11V7a5 5 0 0 1 10 0v4"/>
          </svg>
          Kết nối an toàn · Dữ liệu được mã hóa
        </p>

      </div>
    </div>

  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const email    = ref('')
const password = ref('')
const loading  = ref(false)
const error    = ref('')
const router    = useRouter()
const authStore = useAuthStore()

async function handleLogin() {
  error.value   = ''
  loading.value = true
  try {
    await authStore.login(email.value, password.value)
    router.push('/dashboard')
  } catch (err) {
    error.value = err.response?.data?.detail || 'Đăng nhập thất bại. Vui lòng thử lại.'
  } finally {
    loading.value = false
  }
}
</script>

<style>
@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50%       { transform: translateY(-10px); }
}
</style>
