# Slice 2: System Architecture Diagram

## Overall System Architecture

```
                                    INTERNET USER
                                          |
                    ┌─────────────────────┼─────────────────────┐
                    |                     |                     |
              localhost:5173          localhost:5174      localhost:8000
                    |                     |                     |
            ┌───────▼────────┐   ┌───────▼────────┐    ┌───────▼────────┐
            │  FRONTEND-USER │   │ FRONTEND-ADMIN │    │     BACKEND    │
            │    (Vue App)   │   │    (Vue App)   │    │   (FastAPI)    │
            └────────────────┘   └────────────────┘    └────────────────┘
                    │                     │                     │
                    └─────────────────────┼─────────────────────┘
                                          │
                           Axios with JWT Interceptor
                                          │
                    ┌─────────────────────▼─────────────────────┐
                    │         /api/v1 REST Endpoints           │
                    │  (register, login, refresh, me, kyc/*)   │
                    └────────────────────┬────────────────────┘
                                          │
                         FastAPI Dependency Injection
                                          │
                    ┌─────────────────────▼─────────────────────┐
                    │      Middleware & Dependencies            │
                    │  (get_current_user, require_admin)        │
                    └────────────────────┬────────────────────┘
                                          │
                    ┌─────────────────────▼─────────────────────┐
                    │      Auth Service Layer                   │
                    │  (Business Logic: register, login, etc)   │
                    └────────────────────┬────────────────────┘
                                          │
                         SQLAlchemy ORM
                                          │
                    ┌─────────────────────▼─────────────────────┐
                    │        PostgreSQL Database                │
                    │  (users, wallets, transactions, etc)      │
                    └────────────────────────────────────────────┘
```

---

## User Authentication Flow

```
╔═══════════════════════════════════════════════════════════════════════╗
║                        USER REGISTRATION FLOW                         ║
╚═══════════════════════════════════════════════════════════════════════╝

User visits http://localhost:5173
        │
        ▼
┌──────────────────────┐
│  HomeView           │
│  - "Get Started"    │
│  - "Login" buttons  │
└──────────┬───────────┘
           │ Click "Get Started"
           ▼
┌──────────────────────┐
│ RegisterView        │
│ - Full Name input   │
│ - Email input       │
│ - Password input    │
│ - Confirm Password  │
└──────────┬───────────┘
           │ Click Submit
           ▼
[Frontend Validation]
✓ Email format OK?
✓ Password strength OK?
✓ Passwords match?
           │
           ▼
POST /api/v1/auth/register
{ email, password, full_name }
           │
           ▼
┌──────────────────────────────┐
│ Backend: AuthService         │
│ - Hash password (bcrypt)     │
│ - Create User                │
│ - Create Wallet (balance=0)  │
│ - kyc_status = NOT_SUBMITTED │
└──────────┬───────────────────┘
           │
           ▼
Database: INSERT users, wallets
           │
           ▼
201 Created Response
{ UserResponse with all fields }
           │
           ▼
[Frontend: Store response]
authStore.user = response
           │
           ▼
Redirect to /login
           │
           ▼
┌──────────────────────┐
│  LoginView          │
│  - Email input      │
│  - Password input   │
│  (shown for user)   │
└─────────────────────┘


╔═══════════════════════════════════════════════════════════════════════╗
║                         USER LOGIN FLOW                              ║
╚═══════════════════════════════════════════════════════════════════════╝

User on LoginView
        │
        ▼ Enter credentials
┌──────────────────────┐
│ Email: user@ex.com  │
│ Pass: MyPass123!    │
└──────────┬───────────┘
           │ Click Submit
           ▼
POST /api/v1/auth/login
{ email, password }
           │
           ▼
┌────────────────────────────────┐
│ Backend: AuthService           │
│ 1. Query user by email         │
│ 2. Verify password (bcrypt)    │
│ 3. Create JWT tokens           │
│    - access_token (24h)        │
│    - refresh_token (7d)        │
└────────────┬───────────────────┘
             │
             ▼
200 OK Response
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
             │
             ▼
[Frontend: authStore.setTokens()]
- localStorage.setItem('accessToken', token)
- localStorage.setItem('refreshToken', token)
             │
             ▼
[Frontend: authStore.fetchMe()]
GET /api/v1/auth/me
Authorization: Bearer eyJ...
             │
             ▼
Backend returns UserResponse
             │
             ▼
[Frontend: Store in Pinia]
authStore.user = response
authStore.isAuthenticated = true
             │
             ▼
Router: redirect to /dashboard
             │
             ▼
┌────────────────────────────┐
│    DashboardView          │
│ - User profile card       │
│ - KYC status (color-code) │
│ - "Complete KYC" button   │
│   (if kyc_status ≠ VERIFIED)
└────────────────────────────┘


╔═══════════════════════════════════════════════════════════════════════╗
║                    TOKEN REFRESH FLOW (Auto)                         ║
╚═══════════════════════════════════════════════════════════════════════╝

User makes API request (e.g., GET /me)
        │
        ▼
[Axios Request Interceptor]
1. Check if accessToken exists
2. Add to Authorization header
Authorization: Bearer eyJ...
        │
        ▼
Backend receives request
        │
        ▼
[Middleware: get_current_user()]
1. Decode JWT with secret key
2. Extract 'sub' claim (user_id)
3. Query database for user
4. Return User object
        │
        ├─ JWT valid, not expired ──▶ Return 200 OK
        │
        └─ JWT expired ──────▶ Return 401 Unauthorized
                                    │
                                    ▼
                      [Axios Response Interceptor]
                      1. Detect 401 status
                      2. Get refreshToken from localStorage
                      3. POST /api/v1/auth/refresh
                         { refresh_token }
                                    │
                                    ▼
                      Backend validates refresh token
                                    │
                                    ▼
                      Return new { access_token, refresh_token }
                                    │
                                    ▼
                      [Frontend: Update tokens]
                      localStorage.setItem('accessToken', new_token)
                      localStorage.setItem('refreshToken', new_token)
                                    │
                                    ▼
                      [Retry original request]
                      GET /me with new Authorization header
                                    │
                                    ▼
                      Backend: get_current_user() succeeds
                                    │
                                    ▼
                      Return 200 OK with original response


╔═══════════════════════════════════════════════════════════════════════╗
║                     KYC SUBMISSION FLOW                              ║
╚═══════════════════════════════════════════════════════════════════════╝

User on DashboardView
        │ kyc_status = NOT_SUBMITTED
        │
        ▼ Click "Complete KYC"
┌────────────────────────┐
│    KycView            │
│ - Status display      │
│ - Phone input         │
│ - Identity textarea   │
│ - Submit button       │
└────────────┬───────────┘
             │ Click Submit
             ▼
[Frontend Validation]
✓ Phone format OK?
✓ Phone 10-20 chars?
             │
             ▼
POST /api/v1/auth/kyc/submit
Authorization: Bearer eyJ...
{
  "phone_number": "+84901234567",
  "identity_details": "ID: 123456789"
}
             │
             ▼
┌──────────────────────────────────┐
│ Backend: AuthService.submit_kyc()│
│ 1. Get current_user              │
│ 2. Update kyc_status = PENDING   │
│ 3. Set phone_number              │
│ 4. Set kyc_submitted_at = now()  │
└──────────┬───────────────────────┘
           │
           ▼
Database UPDATE users SET ...
           │
           ▼
200 OK Response
{
  "kyc_status": "PENDING",
  "message": "Submitted successfully"
}
           │
           ▼
[Frontend: Show success message]
           │
           ▼
[Frontend: authStore.fetchMe()]
GET /api/v1/auth/me
           │
           ▼
[Update display]
KycView shows:
✓ Status: PENDING (yellow)
✓ Message: "Under review..."
✓ Submit button disabled
           │
           ▼
[Admin reviews in Slice 7]
kyc_status → VERIFIED or REJECTED


╔═══════════════════════════════════════════════════════════════════════╗
║                     LOGOUT FLOW                                       ║
╚═══════════════════════════════════════════════════════════════════════╝

User clicks logout
        │
        ▼
[Frontend: authStore.logout()]
1. Clear localStorage
   - localStorage.removeItem('accessToken')
   - localStorage.removeItem('refreshToken')
2. Clear authStore state
   - authStore.user = null
   - authStore.accessToken = null
        │
        ▼
Router: redirect to /login
        │
        ▼
LoginView shown
(fresh state, no token)
```

---

## Database Schema

```
┌──────────────────────────────────────────────┐
│              users Table                     │
├──────────────────────────────────────────────┤
│ id (UUID) ................................ PK │
│ email (VARCHAR, UNIQUE) .................. UQ │
│ password_hash (VARCHAR)                      │
│ full_name (VARCHAR)                          │
│ role (ENUM: USER, ADMIN)                     │
│ phone_number (VARCHAR, NULLABLE)             │
│ kyc_status (ENUM: NOT_SUBMITTED, ...)        │
│ kyc_submitted_at (TIMESTAMP, NULLABLE)       │
│ kyc_rejection_reason (VARCHAR, NULLABLE)     │
│ is_active (BOOLEAN)                          │
│ created_at (TIMESTAMP)                       │
│ updated_at (TIMESTAMP)                       │
└──────────────────────────────────────────────┘
                   │ 1:1
                   │
┌──────────────────▼───────────────────────────┐
│             wallets Table                    │
├───────────────────────────────────────────────┤
│ id (UUID) ................................ PK │
│ user_id (UUID) ........................... FK │
│ balance (DECIMAL(15,2))                      │
│ currency (VARCHAR, default='SC')             │
│ created_at (TIMESTAMP)                       │
│ updated_at (TIMESTAMP)                       │
└──────────────────────────────────────────────┘
```

---

## Request/Response Cycle

### Register Request
```
HTTP REQUEST:
POST /api/v1/auth/register HTTP/1.1
Host: localhost:8000
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "MySecure123!",
  "full_name": "John Doe"
}


HTTP RESPONSE:
HTTP/1.1 201 Created
Content-Type: application/json

{
  "id": "550e8400-...",
  "email": "user@example.com",
  "full_name": "John Doe",
  "role": "USER",
  "phone_number": null,
  "kyc_status": "NOT_SUBMITTED",
  "kyc_submitted_at": null,
  "kyc_rejection_reason": null,
  "is_active": true,
  "created_at": "2024-04-28T10:00:00Z",
  "updated_at": "2024-04-28T10:00:00Z"
}
```

### Login Request
```
HTTP REQUEST:
POST /api/v1/auth/login HTTP/1.1
Host: localhost:8000
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "MySecure123!"
}


HTTP RESPONSE:
HTTP/1.1 200 OK
Content-Type: application/json

{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Protected Request
```
HTTP REQUEST:
GET /api/v1/auth/me HTTP/1.1
Host: localhost:8000
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...


HTTP RESPONSE:
HTTP/1.1 200 OK
Content-Type: application/json

{
  "id": "550e8400-...",
  "email": "user@example.com",
  ...
}

OR (on 401):

HTTP RESPONSE:
HTTP/1.1 401 Unauthorized
Content-Type: application/json

{
  "detail": "Not authenticated"
}
```

---

## Component Hierarchy

### Frontend-User

```
App.vue
├── AppHeader.vue
│   ├── Logo (link to /)
│   ├── Nav Links (Dashboard, Insurance, Wallet, Policies)
│   └── User Dropdown
│       ├── Profile
│       ├── KYC Verification
│       └── Logout
│
└── RouterView (based on route)
    ├── HomeView (/)
    ├── LoginView (/login)
    ├── RegisterView (/register)
    ├── DashboardView (/dashboard, protected)
    └── KycView (/kyc, protected)
```

### Frontend-Admin

```
App.vue
├── AdminHeader.vue
│   ├── Title "Admin Dashboard"
│   └── User Dropdown with ADMIN badge
│
├── AdminSidebar.vue
│   ├── Dashboard
│   ├── Products
│   ├── Policies
│   ├── Claims
│   ├── Users
│   ├── KYC Review
│   ├── Risk Analytics
│   └── API Monitor
│
└── RouterView (based on route)
    ├── LoginView (/login)
    └── DashboardView (/dashboard, protected)
```

---

## State Management (Pinia Store)

### authStore (User App)

```
STATE:
├── accessToken: string | null
├── refreshToken: string | null
└── user: UserResponse | null

GETTERS:
└── isAuthenticated: boolean

ACTIONS:
├── register(email, password, fullName)
├── login(email, password)
├── logout()
├── fetchMe()
├── submitKyc(phoneNumber, identityDetails)
├── getKycStatus()
└── setTokens(access, refresh)

LIFECYCLE:
└── On store init: if accessToken exists → fetchMe()
```

### authStore (Admin App)

```
STATE:
├── accessToken: string | null
├── refreshToken: string | null
└── user: UserResponse | null

GETTERS:
└── isAuthenticated: boolean

ACTIONS:
├── login(email, password) [checks role === ADMIN]
├── logout()
├── fetchMe()
└── setTokens(access, refresh)
```

---

## Middleware & Dependencies Chain

```
HTTP Request
    ↓
┌─────────────────────────────────┐
│ FastAPI Router                  │
│ POST /auth/login                │
│ GET  /auth/me (requires JWT)    │
└────────────────┬────────────────┘
                 ↓
┌─────────────────────────────────┐
│ Dependency: get_current_user()  │
│ - Extract Authorization header  │
│ - Decode JWT                    │
│ - Query User by ID              │
│ - Return User or 401            │
└────────────────┬────────────────┘
                 ↓
┌─────────────────────────────────┐
│ Dependency: require_admin()     │
│ - Check user.role === ADMIN     │
│ - Return user or 403            │
└────────────────┬────────────────┘
                 ↓
         Route Handler
                 ↓
         HTTP Response
```

---

## Error Handling Flow

```
User Makes Request
        │
        ▼
Validation Layer
├─ Pydantic validation
│  └─ 422 Unprocessable Entity
│
├─ Business logic validation
│  ├─ Email exists → 400
│  ├─ Weak password → 400
│  ├─ Invalid credentials → 401
│  └─ User not found → 404
│
└─ Authentication
   ├─ No JWT → 401
   ├─ Invalid JWT → 401
   ├─ Expired JWT → (Axios refresh + retry)
   └─ Insufficient role → 403

        ↓
Return Error Response
{
  "detail": "Error message"
}
```

---

**Last Updated:** April 28, 2024  
**For:** Slice 2 (Authentication System)
