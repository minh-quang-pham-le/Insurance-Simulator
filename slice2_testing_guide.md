# Slice 2: Authentication — Hướng dẫn kiểm thử

## Tổng quan

Theo `tasks/plan.md`, Slice 2 yêu cầu kiểm thử flow sau:

> **Verify:** Full register → login → access /me → refresh token → access admin-only endpoint (403 for USER) flow.
> **Additionally:** submit KYC → status = PENDING → admin approves → status = VERIFIED → wallet top-up now succeeds.

---

## Bước 0: Chuẩn bị môi trường

### 0.1 — Khởi động PostgreSQL (qua Docker)

```powershell
# Từ thư mục gốc project
cd d:\Thach\HUST\Software\project\Insurance-Simulator
docker-compose up -d db
```

> [!NOTE]
> Nếu bạn đã có PostgreSQL cài sẵn trên máy, có thể bỏ qua bước này.
> Database mặc định: `postgresql://postgres:postgres@localhost:5432/insurance_simulator_db`

### 0.2 — Tạo file `.env` cho backend (nếu chưa có)

```powershell
cd d:\Thach\HUST\Software\project\Insurance-Simulator\backend
copy .env.example .env
```

### 0.3 — Cài đặt dependencies backend

```powershell
cd d:\Thach\HUST\Software\project\Insurance-Simulator\backend
pip install -r requirements.txt
```

### 0.4 — Chạy migration + seed data

```powershell
cd d:\Thach\HUST\Software\project\Insurance-Simulator\backend
alembic upgrade head
python -m seed.seed_data
```

✅ **Acceptance:** Không có lỗi. DB có đầy đủ tables và seed data (admin user, test user, 5 products, 250+ risk records).

### 0.5 — Cài node_modules cho frontend (nếu chưa có)

```powershell
cd d:\Thach\HUST\Software\project\Insurance-Simulator\frontend-user
npm install

cd d:\Thach\HUST\Software\project\Insurance-Simulator\frontend-admin
npm install
```

---

## Bước 1: Khởi động 3 servers

Mở **3 terminal riêng biệt**:

### Terminal 1 — Backend (port 8000)

```powershell
cd d:\Thach\HUST\Software\project\Insurance-Simulator\backend
uvicorn app:app --port 8000 --reload
```

✅ **Acceptance:** Server chạy OK, không có import error.

### Terminal 2 — Frontend User (port 5173)

```powershell
cd d:\Thach\HUST\Software\project\Insurance-Simulator\frontend-user
npm run dev
```

✅ **Acceptance:** `npm run dev` khởi động trên port 5173 không lỗi.

### Terminal 3 — Frontend Admin (port 5174)

```powershell
cd d:\Thach\HUST\Software\project\Insurance-Simulator\frontend-admin
npm run dev
```

✅ **Acceptance:** `npm run dev` khởi động trên port 5174 không lỗi.

---

## Bước 2: Kiểm tra Swagger API docs

Mở trình duyệt: **http://localhost:8000/docs**

✅ **Acceptance:** Swagger hiển thị đúng **6 endpoints** của Auth:
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/auth/register` | Register |
| POST | `/api/v1/auth/login` | Login |
| POST | `/api/v1/auth/refresh` | Refresh token |
| GET | `/api/v1/auth/me` | Get current user |
| POST | `/api/v1/auth/kyc/submit` | Submit KYC |
| GET | `/api/v1/auth/kyc/status` | Get KYC status |

---

## Bước 3: Kiểm thử Backend API (dùng cURL/Swagger)

### Test 3.1 — Register

```powershell
curl -X POST http://localhost:8000/api/v1/auth/register `
  -H "Content-Type: application/json" `
  -d '{\"email\": \"test@example.com\", \"password\": \"Test@1234\", \"full_name\": \"Test User\"}'
```

✅ **Expected:** `201 Created` — Response chứa `kyc_status: "NOT_SUBMITTED"`, `id`, `email`, `role: "USER"`

### Test 3.2 — Register trùng email

```powershell
curl -X POST http://localhost:8000/api/v1/auth/register `
  -H "Content-Type: application/json" `
  -d '{\"email\": \"test@example.com\", \"password\": \"Test@1234\", \"full_name\": \"Test User\"}'
```

✅ **Expected:** `400 Bad Request` — `"Email already registered"`

### Test 3.3 — Register password yếu

```powershell
curl -X POST http://localhost:8000/api/v1/auth/register `
  -H "Content-Type: application/json" `
  -d '{\"email\": \"weak@example.com\", \"password\": \"12345678\", \"full_name\": \"Weak User\"}'
```

✅ **Expected:** `422 Unprocessable Entity` — Password validation error (thiếu uppercase + special char)

### Test 3.4 — Login

```powershell
curl -X POST http://localhost:8000/api/v1/auth/login `
  -H "Content-Type: application/json" `
  -d '{\"email\": \"test@example.com\", \"password\": \"Test@1234\"}'
```

✅ **Expected:** `200 OK` — Response chứa `access_token`, `refresh_token`, `token_type: "bearer"`

> [!IMPORTANT]
> Lưu lại `access_token` và `refresh_token` từ response này cho các test tiếp theo!

### Test 3.5 — Get /me (với JWT)

```powershell
curl -X GET http://localhost:8000/api/v1/auth/me `
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

✅ **Expected:** `200 OK` — UserResponse có `kyc_status`, `email`, `full_name`, `role`

### Test 3.6 — Get /me (không có JWT)

```powershell
curl -X GET http://localhost:8000/api/v1/auth/me
```

✅ **Expected:** `403 Forbidden` (HTTPBearer yêu cầu credentials)

### Test 3.7 — Get /me (JWT hết hạn/sai)

```powershell
curl -X GET http://localhost:8000/api/v1/auth/me `
  -H "Authorization: Bearer invalid-token-here"
```

✅ **Expected:** `401 Unauthorized`

### Test 3.8 — Refresh token

```powershell
curl -X POST http://localhost:8000/api/v1/auth/refresh `
  -H "Content-Type: application/json" `
  -d '{\"refresh_token\": \"<REFRESH_TOKEN>\"}'
```

✅ **Expected:** `200 OK` — Trả về access_token mới

### Test 3.9 — Admin-only endpoint (USER bị chặn 403)

Sử dụng token của user thường để gọi bất kỳ admin endpoint nào. Hiện tại chưa có admin router riêng (Slice 7), nhưng bạn có thể test `require_admin` dependency bằng cách:

> [!NOTE]
> Admin endpoint chưa được implement (Slice 7). Để kiểm tra `require_admin` hoạt động, bạn cần có endpoint sử dụng `require_admin` dependency. Hiện tại chỉ có thể test gián tiếp bằng cách login admin account từ seed data và xác nhận role.

**Login admin account (từ seed data):**
```powershell
curl -X POST http://localhost:8000/api/v1/auth/login `
  -H "Content-Type: application/json" `
  -d '{\"email\": \"admin@insurance.com\", \"password\": \"Admin@123\"}'
```

Kiểm tra `/me` với admin token → `role: "ADMIN"`.

---

## Bước 4: Kiểm thử KYC Flow

### Test 4.1 — Submit KYC (user thường)

```powershell
curl -X POST http://localhost:8000/api/v1/auth/kyc/submit `
  -H "Content-Type: application/json" `
  -H "Authorization: Bearer <USER_ACCESS_TOKEN>" `
  -d '{\"phone_number\": \"+84901234567\", \"identity_details\": \"CCCD: 001234567890\"}'
```

✅ **Expected:** `200 OK` — `kyc_status: "PENDING"`, `message: "KYC verification submitted for review"`

### Test 4.2 — Get KYC Status

```powershell
curl -X GET http://localhost:8000/api/v1/auth/kyc/status `
  -H "Authorization: Bearer <USER_ACCESS_TOKEN>"
```

✅ **Expected:** `200 OK` — `kyc_status: "PENDING"`

### Test 4.3 — Submit KYC lần 2 (đang PENDING → bị chặn)

```powershell
curl -X POST http://localhost:8000/api/v1/auth/kyc/submit `
  -H "Content-Type: application/json" `
  -H "Authorization: Bearer <USER_ACCESS_TOKEN>" `
  -d '{\"phone_number\": \"+84901234567\"}'
```

✅ **Expected:** `400 Bad Request` — `"KYC already submitted and pending review"`

### Test 4.4 — Phone number quá ngắn

```powershell
curl -X POST http://localhost:8000/api/v1/auth/kyc/submit `
  -H "Content-Type: application/json" `
  -H "Authorization: Bearer <USER_ACCESS_TOKEN>" `
  -d '{\"phone_number\": \"123\"}'
```

✅ **Expected:** `422 Unprocessable Entity` — Validation error (min_length=10)

---

## Bước 5: Kiểm thử Frontend User (http://localhost:5173)

| # | Thao tác | Expected |
|---|----------|----------|
| 5.1 | Mở http://localhost:5173 | Trang Home hiển thị, có nút "Get Started" và "Login" |
| 5.2 | Click "Get Started" | Chuyển sang trang Register (`/register`) |
| 5.3 | Đăng ký với email/password/name hợp lệ | Đăng ký thành công → redirect sang `/login` |
| 5.4 | Đăng nhập với account vừa tạo | Login thành công → redirect sang `/dashboard` |
| 5.5 | Xem Dashboard | Hiển thị Profile (name, email, KYC Status = NOT_SUBMITTED, Phone = Not provided) |
| 5.6 | Dashboard hiện banner KYC | Banner xanh "You must complete KYC verification..." với nút "Complete KYC Verification" |
| 5.7 | Click "Complete KYC Verification" hoặc vào `/kyc` | Trang KYC form hiển thị, status = "Not Submitted" |
| 5.8 | Nhập phone + identity → Submit | KYC thành công → status chuyển thành "Pending Review" |
| 5.9 | Header dropdown | Hiện user name, có link "KYC Verification" và "Logout" |
| 5.10 | Logout → redirect | Về `/login`, không truy cập được `/dashboard` |

---

## Bước 6: Kiểm thử Frontend Admin (http://localhost:5174)

| # | Thao tác | Expected |
|---|----------|----------|
| 6.1 | Mở http://localhost:5174 | Trang Admin Login |
| 6.2 | Login admin account (`admin@insurance.com` / `Admin@123`) | Login thành công → Dashboard |
| 6.3 | Login user thường | Error: "This account does not have admin access" |
| 6.4 | Dashboard hiển thị | Stats cards (placeholder), Sidebar menu, Header with "ADMIN" badge |
| 6.5 | Sidebar có các menu items | Dashboard, Products, Policies, Claims, Users, KYC Review, Risk Analytics, API Monitor |
| 6.6 | Logout | Redirect về `/login` |

> [!WARNING]
> Admin seed password cần phải khớp. Kiểm tra file `seed/seed_data.py` để xác nhận credentials admin. Nếu password trong seed_data.py khác với `Admin@123`, hãy dùng password đúng.

---

## Bước 7: Tóm tắt Acceptance Criteria cho Slice 2

| Task | Tiêu chí | Cách kiểm tra |
|------|----------|---------------|
| **2.1** JWT middleware | `get_current_user` extract user từ JWT; `require_admin` → 403 cho USER; expired → 401 | Tests 3.5, 3.6, 3.7, 3.9 |
| **2.2** Auth service | Register tạo User+Wallet; bcrypt password; authenticate validates; KYC submit + get_status | Tests 3.1, 3.4, 4.1, 4.2 |
| **2.3** Auth router | 6 endpoints: register, login, refresh, me, kyc/submit, kyc/status | Bước 2 (Swagger) |
| **2.4** Frontend scaffolding | npm run dev starts; Axios interceptor; router guards | Bước 1 (terminals), Tests 5.10 |
| **2.5** Auth pages | Register → Login → Dashboard → KYC flow; Admin Login + Sidebar | Bước 5 + 6 |

---

## Script kiểm thử tự động (PowerShell)

Nếu bạn muốn chạy kiểm thử API tự động bằng PowerShell (backend phải đang chạy):

```powershell
cd d:\Thach\HUST\Software\project\Insurance-Simulator

# === TEST 1: Register ===
Write-Host "`n=== TEST 1: Register ===" -ForegroundColor Cyan
$register = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/register" -Method POST `
  -ContentType "application/json" `
  -Body '{"email": "slice2test@example.com", "password": "Test@1234", "full_name": "Slice2 Tester"}'
Write-Host "Register OK: $($register.email), KYC: $($register.kyc_status)"

# === TEST 2: Login ===
Write-Host "`n=== TEST 2: Login ===" -ForegroundColor Cyan
$login = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" -Method POST `
  -ContentType "application/json" `
  -Body '{"email": "slice2test@example.com", "password": "Test@1234"}'
$token = $login.access_token
$refreshToken = $login.refresh_token
Write-Host "Login OK: token received"

# === TEST 3: Get /me ===
Write-Host "`n=== TEST 3: Get /me ===" -ForegroundColor Cyan
$me = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/me" -Method GET `
  -Headers @{ Authorization = "Bearer $token" }
Write-Host "Me OK: $($me.email), role=$($me.role), kyc=$($me.kyc_status)"

# === TEST 4: Refresh Token ===
Write-Host "`n=== TEST 4: Refresh Token ===" -ForegroundColor Cyan
$refresh = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/refresh" -Method POST `
  -ContentType "application/json" `
  -Body "{`"refresh_token`": `"$refreshToken`"}"
Write-Host "Refresh OK: new token received"

# === TEST 5: Get /me without token (expect error) ===
Write-Host "`n=== TEST 5: Get /me without token (expect 403) ===" -ForegroundColor Cyan
try {
  Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/me" -Method GET
  Write-Host "FAIL: Should have returned error" -ForegroundColor Red
} catch {
  $code = $_.Exception.Response.StatusCode.value__
  Write-Host "OK: Got HTTP $code (expected 403)" -ForegroundColor Green
}

# === TEST 6: Get /me with bad token (expect 401) ===
Write-Host "`n=== TEST 6: Get /me with bad token (expect 401) ===" -ForegroundColor Cyan
try {
  Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/me" -Method GET `
    -Headers @{ Authorization = "Bearer invalid-token" }
  Write-Host "FAIL: Should have returned 401" -ForegroundColor Red
} catch {
  $code = $_.Exception.Response.StatusCode.value__
  Write-Host "OK: Got HTTP $code (expected 401)" -ForegroundColor Green
}

# === TEST 7: Submit KYC ===
Write-Host "`n=== TEST 7: Submit KYC ===" -ForegroundColor Cyan
$kyc = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/kyc/submit" -Method POST `
  -ContentType "application/json" `
  -Headers @{ Authorization = "Bearer $token" } `
  -Body '{"phone_number": "+84901234567", "identity_details": "CCCD 001234567890"}'
Write-Host "KYC Submit OK: status=$($kyc.kyc_status), msg=$($kyc.message)"

# === TEST 8: Get KYC Status ===
Write-Host "`n=== TEST 8: Get KYC Status ===" -ForegroundColor Cyan
$kycStatus = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/kyc/status" -Method GET `
  -Headers @{ Authorization = "Bearer $token" }
Write-Host "KYC Status OK: $($kycStatus.kyc_status)"

# === TEST 9: Submit KYC again (expect 400) ===
Write-Host "`n=== TEST 9: Submit KYC again (expect 400) ===" -ForegroundColor Cyan
try {
  Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/kyc/submit" -Method POST `
    -ContentType "application/json" `
    -Headers @{ Authorization = "Bearer $token" } `
    -Body '{"phone_number": "+84901234567"}'
  Write-Host "FAIL: Should have returned 400" -ForegroundColor Red
} catch {
  $code = $_.Exception.Response.StatusCode.value__
  Write-Host "OK: Got HTTP $code (expected 400 - KYC already pending)" -ForegroundColor Green
}

# === TEST 10: Duplicate email registration (expect 400) ===
Write-Host "`n=== TEST 10: Duplicate email (expect 400) ===" -ForegroundColor Cyan
try {
  Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/register" -Method POST `
    -ContentType "application/json" `
    -Body '{"email": "slice2test@example.com", "password": "Test@1234", "full_name": "Dup"}'
  Write-Host "FAIL: Should have returned 400" -ForegroundColor Red
} catch {
  $code = $_.Exception.Response.StatusCode.value__
  Write-Host "OK: Got HTTP $code (expected 400 - duplicate email)" -ForegroundColor Green
}

# === TEST 11: Login admin (from seed) ===
Write-Host "`n=== TEST 11: Login admin ===" -ForegroundColor Cyan
try {
  $adminLogin = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" -Method POST `
    -ContentType "application/json" `
    -Body '{"email": "admin@insurance.com", "password": "Admin@123"}'
  $adminToken = $adminLogin.access_token
  
  $adminMe = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/me" -Method GET `
    -Headers @{ Authorization = "Bearer $adminToken" }
  Write-Host "Admin OK: $($adminMe.email), role=$($adminMe.role)"
} catch {
  Write-Host "Admin login failed - check seed data password" -ForegroundColor Yellow
}

Write-Host "`n=== ALL TESTS COMPLETED ===" -ForegroundColor Green
```

---

## Tóm tắt các lệnh chạy

```powershell
# 1. Chuẩn bị DB
docker-compose up -d db

# 2. Migration + Seed
cd backend
pip install -r requirements.txt
alembic upgrade head
python -m seed.seed_data

# 3. Chạy 3 servers (mỗi terminal riêng)
cd backend && uvicorn app:app --port 8000 --reload
cd frontend-user && npm install && npm run dev
cd frontend-admin && npm install && npm run dev

# 4. Kiểm tra Swagger
# Mở: http://localhost:8000/docs

# 5. Kiểm tra frontend
# User: http://localhost:5173
# Admin: http://localhost:5174
```
