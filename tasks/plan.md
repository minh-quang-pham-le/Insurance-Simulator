# Insurance Simulator — Implementation Plan

## Context

The project has a complete skeleton (configs, docker-compose, package.json, requirements.txt) but **zero implementation**. All 10 models, 9 routers, 10 schema files, 10 services, both frontend apps, and all tests need to be built from scratch. SPEC.md provides detailed definitions for every model, endpoint, and product.

The plan organizes ~90 files across 4 phases into 13 vertical slices. Each slice delivers a testable end-to-end path. The team has 5 members total — task assignments show how many members each slice needs, and the team decides internally who takes what.

---

## Dependency Graph

```
Layer 0 (EXISTS): config/settings.py, config/database.py, models/base.py, app.py skeleton
    |
Layer 1: models/enums.py  <--  all models depend on this
    |
Layer 2: 10 SQLAlchemy models (user, wallet, insurance_product, policy, claim, ...)
    |
Layer 3: Alembic migration + Pydantic schemas (10 files)
    |
Layer 4: middleware/auth.py (JWT) + seed data
    |
Layer 5: Services (auth, wallet, insurance, policy, claims, risk, simulation, chatbot, notifications, trigger_monitor)
    |
Layer 6: Routers (auth, wallet, insurance, policies, claims, simulation, chatbot, notifications, admin)
    |
Layer 7: Frontend scaffolding (main.js, App.vue, router, vite/tailwind config)
    |
Layer 8: Frontend services -> stores -> views -> components
```

**Cross-cutting:** Wallet <- Policy Purchase <- Claims <- Trigger Monitor (chain). Chatbot <- Products + RiskData. Simulation <- Products + trigger_conditions.

---

## PHASE 1 — Foundation

### Slice 1: Database Foundation [2 members] — BLOCKING

Everything else depends on this slice. Must be completed before other slices can start.

| Task | Files | Acceptance Criteria |
|------|-------|-------------------|
| **1.1** Create enums | `backend/models/enums.py` | 8 enums (UserRole, **KycStatus**, TransactionType, ProductCategory, PolicyStatus, TriggerType, ClaimStatus, NotificationType) all inherit `str, enum.Enum` |
| **1.2** Create 10 models | `backend/models/user.py`, `wallet.py`, `insurance_product.py`, `policy.py`, `claim.py`, `risk_data.py`, `notification.py`, `chat_session.py`, `simulation_session.py`, `api_monitor_log.py` | All columns, FKs, indexes, relationships match SPEC Section 6.2 exactly. Inherit `Base, UUIDPrimaryKeyMixin, TimestampMixin`. **User model** includes `phone_number`, `kyc_status`, `kyc_submitted_at`, `kyc_rejection_reason`. **WalletTransaction** uses `policy_id` (FK → Policy) and `claim_id` (FK → Claim) instead of polymorphic reference_id/reference_type |
| **1.3** Uncomment model imports | `backend/models/__init__.py` | All 10 imports active, `from models import *` works |
| **1.4** Generate migration | `backend/alembic/versions/*.py` | `alembic upgrade head` creates all 10 tables; `alembic downgrade base` drops cleanly |
| **1.5** Create Pydantic schemas | `backend/schemas/auth.py`, `user.py`, `wallet.py`, `insurance.py`, `policy.py`, `claim.py`, `simulation.py`, `chat.py`, `notification.py`, `admin.py` | All request/response schemas with `from_attributes=True`, proper validators. **auth.py** includes `KycSubmitRequest` (phone_number, identity details). **admin.py** includes `KycReviewRequest` (action: approve/reject, rejection_reason). **user.py** includes `kyc_status` in responses |
| **1.6** Create seed data | `backend/seed/products.json`, `seed/risk_data.json`, `seed/seed_data.py` | Idempotent script creates admin user, test user with 10000 SC wallet, 5 products, 250+ risk data records |

**Verify:** `alembic upgrade head && python -m seed.seed_data` runs cleanly on fresh DB. Query all tables to confirm data.

---

### Slice 2: Authentication [2 members]

| Task | Files | Acceptance Criteria |
|------|-------|-------------------|
| **2.1** JWT middleware | `backend/middleware/auth.py` | `get_current_user` dependency extracts user from JWT; `require_admin` raises 403 for USER role; expired tokens -> 401 |
| **2.2** Auth service | `backend/services/auth_service.py` | Register creates User+Wallet atomically (kyc_status = NOT_SUBMITTED); bcrypt password hashing; authenticate validates credentials; **KYC**: submit_kyc (validates phone + identity, sets PENDING), get_kyc_status |
| **2.3** Auth router | `backend/routers/auth.py` + uncomment in `app.py` | POST `/register`, `/login`, `/refresh`; GET `/me`; **POST `/kyc/submit`**, **GET `/kyc/status`**. Swagger docs show all 6 endpoints |
| **2.4** Frontend scaffolding | Both apps: `index.html`, `vite.config.js`, `tailwind.config.js`, `postcss.config.js`, `src/main.js`, `src/App.vue`, `src/assets/main.css`, `src/router/index.js`, `src/services/api.js`, `src/stores/auth.js` | `npm run dev` starts on 5173/5174; Axios interceptor attaches JWT; router guards protect routes |
| **2.5** Auth pages | User: `LoginView.vue`, `RegisterView.vue`, `HomeView.vue`, `AppHeader.vue`, `authService.js`, **`KycView.vue`** (KYC submission form). Admin: `LoginView.vue`, `AdminSidebar.vue`, `AdminHeader.vue` | Register -> login -> view profile -> logout flow works in browser. **KYC form accessible from profile/dashboard; shows current KYC status** |

**Verify:** Full register -> login -> access /me -> refresh token -> access admin-only endpoint (403 for USER) flow. **Additionally:** submit KYC -> status = PENDING -> admin approves -> status = VERIFIED -> wallet top-up now succeeds.

---

### Slice 3: Wallet System [2 members]

| Task | Files | Acceptance Criteria |
|------|-------|-------------------|
| **3.1** Wallet service | `backend/services/wallet_service.py` | `SELECT ... FOR UPDATE` locking; balance never negative; all ops create WalletTransaction with correct balance_after; **WalletTransaction links via `policy_id` or `claim_id` FKs** (not polymorphic reference) |
| **3.2** Wallet router | `backend/routers/wallet.py` + uncomment in `app.py` | GET `/`, POST `/topup`, GET `/transactions` with pagination. **Top-up requires `kyc_status = VERIFIED`; returns 403 with KYC message if not verified** |
| **3.3** Wallet frontend | `walletService.js`, `stores/wallet.js`, `WalletView.vue`, `BalanceCard.vue`, `TransactionList.vue` | Top up -> balance updates -> transaction history shows record; balance visible in header |

**Verify:** Register -> attempt top-up (blocked: KYC not verified) -> submit KYC -> admin approves -> top up 500 -> top up 300 -> balance shows 800 -> 2 transactions in history.

---

### Slice 4: Insurance Product Catalog [2-3 members]

| Task | Files | Acceptance Criteria |
|------|-------|-------------------|
| **4.1** Insurance service | `backend/services/insurance_service.py` | List/get products; CRUD for admins; basic risk score from RiskData |
| **4.2** Insurance router | `backend/routers/insurance.py` + uncomment in `app.py` | GET/POST/PUT/PATCH on `/products` per SPEC Section 7.3 |
| **4.3** User catalog UI | `insuranceService.js`, `stores/insurance.js`, `InsuranceListView.vue`, `InsuranceDetailView.vue`, `ProductCard.vue`, `RiskGauge.vue`, `DynamicForm.vue` | Grid of 5 products; detail page renders dynamic form from parameters_schema |
| **4.4** Admin product CRUD | Admin: `insuranceService.js`, `ProductsView.vue`, `ProductFormView.vue`, `ProductTable.vue` | Admin creates/edits/deactivates products; changes reflected in user catalog |

---

### Slice 5: Policy Purchase Flow [2 members]

| Task | Files | Acceptance Criteria |
|------|-------|-------------------|
| **5.1** Risk engine (basic) | `backend/services/risk_engine.py` | Premium formula from SPEC 4.4; season_factor, location_factor; risk_score 1-10 |
| **5.2** Policy service | `backend/services/policy_service.py` | **Verify `kyc_status = VERIFIED` before purchase (403 if not)**; atomic purchase (calc premium -> check wallet -> deduct -> create policy); cancel with refund; expire_policies background |
| **5.3** Policy router | `backend/routers/policies.py` + uncomment in `app.py` | POST `/calculate-premium`, `/purchase`; GET `/`, `/{id}`; POST `/{id}/cancel` |
| **5.4** Purchase UI | `PremiumCalculator.vue`, `MyPoliciesView.vue`, `DashboardView.vue` | Fill params -> calculate -> see breakdown -> purchase -> wallet deducted -> policy in My Policies |

**Verify:** Login (KYC verified user) -> top up 5000 -> calculate Flight Delay premium -> purchase -> wallet reduced -> My Policies shows ACTIVE -> cancel -> wallet refunded. **Also verify:** unverified user cannot purchase (403).

---

### Slice 6: Claims + Notifications [2 members]

| Task | Files | Acceptance Criteria |
|------|-------|-------------------|
| **6.1** Claims engine | `backend/services/claims_engine.py` | Manual claim -> MANUAL_REVIEW; auto claim -> AUTO_APPROVED + wallet credit; admin review -> approve/reject |
| **6.2** Claims router | `backend/routers/claims.py` + uncomment in `app.py` | POST `/`, GET `/`, GET `/{id}` |
| **6.3** Notification service + router | `backend/services/notification_service.py`, `backend/routers/notifications.py` + uncomment in `app.py` | Create/list/mark-read notifications; unread count endpoint |
| **6.4** Frontend | User: `claimService.js`, `notificationService.js`, `stores/notification.js`, `NotificationsView.vue`, `NotificationBell.vue`. Admin: `ClaimsView.vue`, `claimService.js` | Manual claim submission -> admin review -> approve -> wallet credited -> notification appears |

---

### Slice 7: Admin Dashboard [1-2 members]

| Task | Files | Acceptance Criteria |
|------|-------|-------------------|
| **7.1** Admin router | `backend/routers/admin.py` + uncomment in `app.py` | GET `/dashboard`, `/users`, `/policies`, `/claims`; PUT `/claims/{id}/review`; **GET `/kyc/pending`**, **PATCH `/kyc/{user_id}`** (approve/reject with reason) |
| **7.2** Admin dashboard UI | `adminService.js`, `DashboardView.vue`, `PoliciesView.vue`, `UsersView.vue`, `StatsCard.vue`, **`KycReviewView.vue`** | Metrics cards with real data; all admin tables paginated. **KYC review queue shows pending users; admin can approve or reject with reason** |

---

### CHECKPOINT 1 (Phase 1 Complete)
- [ ] Full auth on both apps
- [ ] **KYC flow: user submits → admin approves/rejects → status enforced on transactions**
- [ ] Wallet ops work **(top-up blocked without KYC)**
- [ ] 5 products in catalog with risk scores
- [ ] Policy purchase + cancel flow **(purchase blocked without KYC)**
- [ ] Manual claim -> admin review -> payout
- [ ] Notifications with unread count
- [ ] Admin dashboard with metrics **+ KYC review queue**
- [ ] Swagger docs complete at /docs

---

## PHASE 2 — Intelligence

### Slice 8: AI Chatbot [1-2 members]

| Task | Files | Acceptance Criteria |
|------|-------|-------------------|
| **8.1** Chatbot service | `backend/services/chatbot_service.py` | Gemini API call with context injection (product catalog, user policies, risk data); session persistence; graceful fallback |
| **8.2** Chatbot router | `backend/routers/chatbot.py` + uncomment in `app.py` | POST `/message`, GET `/sessions`, GET `/sessions/{id}` |
| **8.3** Chat widget | `chatService.js`, `ChatWidget.vue`, `ChatMessage.vue` | Floating widget on insurance pages; context-aware responses; typing indicator |

---

### Slice 9: Risk Engine + Simulation [2-3 members]

| Task | Files | Acceptance Criteria |
|------|-------|-------------------|
| **9.1** Enhanced risk engine | Modify `backend/services/risk_engine.py` | Admin analytics: probabilities by category/region/season; loss ratios; numpy stats |
| **9.2** Simulation engine | `backend/services/simulation_engine.py` | Extract slider configs from parameters_schema; evaluate trigger rules; payout multipliers |
| **9.3** Simulation router | `backend/routers/simulation.py` + uncomment in `app.py` | GET `/products/{id}/config`, POST `/products/{id}/check-trigger`, POST `/products/{id}/log` |
| **9.4** Simulation UI | `simulationService.js`, `SimulationModal.vue`, `TriggerSlider.vue`, `ThresholdBar.vue`, `TriggerResult.vue` | Sliders with green/yellow/red zones; threshold crossing shows "Activated!" with payout; all 5 products work |
| **9.5** Risk analytics admin | `RiskAnalyticsView.vue`, `RevenueChart.vue`, `ClaimsChart.vue`, `analyticsService.js` | ApexCharts: probability tables, loss ratio trends, revenue chart |

---

### CHECKPOINT 2 (Phase 2 Complete)
- [ ] Chatbot responds with product-aware advice
- [ ] Simulation sliders work for all 5 products
- [ ] Threshold crossing shows animated result
- [ ] Admin risk analytics with charts

---

## PHASE 3 — Real-World Integration

### Slice 10: External APIs + Trigger Monitor [1-2 members]

| Task | Files | Acceptance Criteria |
|------|-------|-------------------|
| **10.1** API clients | `backend/utils/external_apis.py` | WeatherClient + AviationClient using httpx; timeout handling; ApiMonitorLog on every call; returns None when keys missing |
| **10.2** Trigger monitor | `backend/services/trigger_monitor.py` + APScheduler in `app.py` | Background job checks ACTIVE parametric policies; auto-claim on trigger; mock mode when no API keys |
| **10.3** API monitor UI | Admin: `ApiMonitorView.vue`, `ApiStatusCard.vue`, `TriggerLogTable.vue`. Backend: GET `/admin/api-monitor`, POST `/admin/risk-data/import` | Per-API status cards (green/yellow/red); trigger event log; response time chart |

---

### CHECKPOINT 3 (Phase 3 Complete)
- [ ] External APIs called when keys configured; mock mode otherwise
- [ ] Auto-claims fire on trigger; wallet credited; notification sent
- [ ] API health dashboard shows status

---

## PHASE 4 — Polish

### Slice 11: UI/UX + Animations [1-2 members]

| Task | Files | Acceptance Criteria |
|------|-------|-------------------|
| **11.1** Visual polish | All frontend files | Responsive; loading spinners; empty states; error toasts; consistent design |
| **11.2** Simulation animations | `FlightAnimation.vue`, `WeatherAnimation.vue`, `TyphoonAnimation.vue`, `RainfallAnimation.vue`, `GadgetAnimation.vue` | CSS/SVG animations driven by slider values per SPEC 4.8.2 |

---

### Slice 12: Hardening [2 members]

| Task | Files | Acceptance Criteria |
|------|-------|-------------------|
| **12.1** Error handling | `backend/middleware/error_handler.py` | Global exception handler; structured JSON errors (`{"detail": "...", "error_code": "..."}`); 500s logged. Note: custom exceptions (`InsufficientBalanceError`, `KycNotVerifiedError`, etc.) and structured logging should be used from Phase 1 per SPEC Section 11 conventions; this slice adds the centralized handler and hardens edge cases |
| **12.2** Input validation | All schemas | Field validators; rate limiting on login/register |
| **12.3** Query optimization | All services | `joinedload` for N+1 prevention; pagination verified |
| **12.4** Security review | All routers/middleware | No SQL injection; no plaintext passwords; RBAC on all admin endpoints |

---

### Slice 13: Docker + Tests [2 members]

| Task | Files | Acceptance Criteria |
|------|-------|-------------------|
| **13.1** .env + Docker | `.env` files, `docker-compose.yml` | `docker-compose up` starts all 4 services; migrations run on startup |
| **13.2** Backend tests | `tests/conftest.py`, `test_auth.py`, `test_wallet.py`, `test_insurance.py`, `test_policies.py`, `test_claims.py` | `pytest` passes all tests |

---

### CHECKPOINT 4 (FINAL)
- [ ] All pages responsive
- [ ] Animations work for all products
- [ ] No security vulnerabilities
- [ ] Docker stack runs from scratch
- [ ] Tests pass
- [ ] README accurate

---

## Staffing Guide

| Slice | Members needed | Can parallelize with |
|-------|---------------|---------------------|
| 1 — Database Foundation | 2 | Nothing (BLOCKING) |
| 2 — Authentication | 2 | Slice 1 must finish first; then backend + frontend can split |
| 3 — Wallet | 2 | After Slice 2 (needs auth) |
| 4 — Insurance Catalog | 2-3 | After Slice 1 (backend) / After Slice 2 (frontend) |
| 5 — Policy Purchase | 2 | After Slices 3 + 4 |
| 6 — Claims + Notifications | 2 | After Slice 5 |
| 7 — Admin Dashboard | 1-2 | After Slice 2 (auth); independent of Slices 3-6 |
| 8 — AI Chatbot | 1-2 | After Slice 4 (needs products) |
| 9 — Risk + Simulation | 2-3 | After Slice 4 (needs products) |
| 10 — External APIs | 1-2 | After Slice 6 (needs claims engine) |
| 11 — UI Polish | 1-2 | After Phase 1 complete |
| 12 — Hardening | 2 | After Phase 2 complete |
| 13 — Docker + Tests | 2 | After Phase 2 complete |

### Parallel Streams After Slice 1

Once Slice 1 is done (models + migration), up to 4 parallel workstreams open:

- **Stream A:** Schemas (1.5) + seed data (1.6) — finishing database work
- **Stream B:** Auth backend (2.1-2.3) — needs User model only
- **Stream C:** Frontend-user scaffolding (2.4) — no backend dependency
- **Stream D:** Frontend-admin scaffolding (2.4) — no backend dependency

After auth is done, all streams advance independently on their respective slices.

---

## Verification Plan

After each checkpoint, run:
1. `cd backend && alembic upgrade head && python -m seed.seed_data` — DB is correct
2. `cd backend && uvicorn app:app --port 8000` — backend starts
3. Open `http://localhost:8000/docs` — Swagger shows all registered endpoints
4. `cd frontend-user && npm run dev` — user app starts on 5173
5. `cd frontend-admin && npm run dev` — admin app starts on 5174
6. Manual flow test: register -> top up -> browse -> purchase -> view policy -> (claim) -> notification
7. `cd backend && pytest` — all tests pass (Phase 4)
8. `docker-compose up -d` — full stack runs (Phase 4)

---

## Critical Path Files

These files have the highest dependency fan-out — errors here block everything:
- `backend/models/enums.py` — every model and schema imports from here (8 enums including KycStatus)
- `backend/middleware/auth.py` — every protected endpoint depends on this; KYC enforcement utility lives here
- `backend/services/auth_service.py` — registration + KYC flow; KYC status gates wallet and policy services
- `backend/services/wallet_service.py` — purchases, claims, and refunds all go through wallet; enforces KYC gate
- `backend/services/policy_service.py` — most complex transaction (KYC check + premium + wallet + policy + notification)
- `frontend-user/src/services/api.js` — every frontend API call uses this Axios instance

---

## File Manifest

### Backend (37+ files to create)

**Models (11):** `enums.py` (8 enums incl. KycStatus), `user.py` (+ KYC fields), `wallet.py` (WalletTransaction uses policy_id/claim_id FKs), `insurance_product.py`, `policy.py`, `claim.py`, `risk_data.py`, `notification.py`, `chat_session.py`, `simulation_session.py`, `api_monitor_log.py`

**Schemas (10):** `auth.py`, `user.py`, `wallet.py`, `insurance.py`, `policy.py`, `claim.py`, `simulation.py`, `chat.py`, `notification.py`, `admin.py`

**Services (10):** `auth_service.py`, `wallet_service.py`, `insurance_service.py`, `policy_service.py`, `claims_engine.py`, `risk_engine.py`, `simulation_engine.py`, `chatbot_service.py`, `trigger_monitor.py`, `notification_service.py`

**Routers (9):** `auth.py`, `wallet.py`, `insurance.py`, `policies.py`, `claims.py`, `simulation.py`, `chatbot.py`, `notifications.py`, `admin.py`

**Middleware (2):** `auth.py`, `error_handler.py`

**Utils (2):** `helpers.py`, `external_apis.py`

**Seed (3):** `seed_data.py`, `products.json`, `risk_data.json`

**Tests (6):** `conftest.py`, `test_auth.py`, `test_wallet.py`, `test_insurance.py`, `test_policies.py`, `test_claims.py`

**Modify (2):** `models/__init__.py`, `app.py`

### Frontend-User (~30 files)

**Scaffold (7):** `index.html`, `vite.config.js`, `tailwind.config.js`, `postcss.config.js`, `main.js`, `App.vue`, `main.css`

**Router (1):** `router/index.js`

**Stores (4):** `auth.js`, `wallet.js`, `insurance.js`, `notification.js`

**Services (8):** `api.js`, `authService.js`, `walletService.js`, `insuranceService.js`, `claimService.js`, `notificationService.js`, `chatService.js`, `simulationService.js`

**Views (10):** `HomeView.vue`, `LoginView.vue`, `RegisterView.vue`, `DashboardView.vue`, `InsuranceListView.vue`, `InsuranceDetailView.vue`, `WalletView.vue`, `MyPoliciesView.vue`, `NotificationsView.vue`, **`KycView.vue`**

**Components (~15+):** `AppHeader.vue`, `AppFooter.vue`, `NotificationBell.vue`, `ProductCard.vue`, `RiskGauge.vue`, `DynamicForm.vue`, `PremiumCalculator.vue`, `BalanceCard.vue`, `TransactionList.vue`, `ChatWidget.vue`, `ChatMessage.vue`, `SimulationModal.vue`, `TriggerSlider.vue`, `ThresholdBar.vue`, `TriggerResult.vue`, plus 5 animation components in Phase 4

### Frontend-Admin (~20 files)

**Scaffold (7):** Same structure as user app (port 5174)

**Router (1):** `router/index.js`

**Stores (2):** `auth.js`, `admin.js`

**Services (6):** `api.js`, `authService.js`, `adminService.js`, `insuranceService.js`, `claimService.js`, `analyticsService.js`

**Views (10):** `LoginView.vue`, `DashboardView.vue`, `ProductsView.vue`, `ProductFormView.vue`, `PoliciesView.vue`, `ClaimsView.vue`, `RiskAnalyticsView.vue`, `ApiMonitorView.vue`, `UsersView.vue`, **`KycReviewView.vue`**

**Components (~8):** `AdminSidebar.vue`, `AdminHeader.vue`, `StatsCard.vue`, `RevenueChart.vue`, `ClaimsChart.vue`, `ProductTable.vue`, `ApiStatusCard.vue`, `TriggerLogTable.vue`
