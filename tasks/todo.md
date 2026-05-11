# Insurance Simulator — Task Checklist

> Track progress by checking off tasks as they're completed.
> Each task maps to the detailed plan in [plan.md](./plan.md).

---

## Phase 1 — Foundation

### Slice 1: Database Foundation [2 members, BLOCKING] -- DONE
- [x] **1.1** Create `backend/models/enums.py` — 8 enum classes matching SPEC Section 6.3 (added `KycStatus`)
- [x] **1.2** Create 10 SQLAlchemy models — all columns, FKs, indexes, relationships per SPEC Section 6.2. User model includes KYC fields (`phone_number`, `kyc_status`, `kyc_submitted_at`, `kyc_rejection_reason`). WalletTransaction uses `policy_id`/`claim_id` FKs (not polymorphic reference)
  - [x] `backend/models/user.py`
  - [x] `backend/models/wallet.py` (Wallet + WalletTransaction)
  - [x] `backend/models/insurance_product.py`
  - [x] `backend/models/policy.py`
  - [x] `backend/models/claim.py`
  - [x] `backend/models/risk_data.py`
  - [x] `backend/models/notification.py`
  - [x] `backend/models/chat_session.py`
  - [x] `backend/models/simulation_session.py`
  - [x] `backend/models/api_monitor_log.py`
- [x] **1.3** Uncomment all imports in `backend/models/__init__.py`
- [x] **1.4** Generate and verify Alembic migration (`alembic revision --autogenerate`)
- [x] **1.5** Create 10 Pydantic schema files in `backend/schemas/`
  - [x] `auth.py` (RegisterRequest, LoginRequest, TokenResponse, RefreshRequest, **KycSubmitRequest**)
  - [x] `user.py` (UserResponse incl. kyc_status, UserUpdate)
  - [x] `wallet.py` (TopUpRequest, WalletResponse, TransactionResponse, TransactionListResponse)
  - [x] `insurance.py` (ProductCreate, ProductUpdate, ProductResponse, ProductListResponse)
  - [x] `policy.py` (PremiumCalculateRequest/Response, PurchaseRequest, PolicyResponse, PolicyListResponse)
  - [x] `claim.py` (ManualClaimRequest, ClaimReviewRequest, ClaimResponse)
  - [x] `simulation.py` (SimulationConfigResponse, TriggerCheckRequest/Response, SimulationLogRequest)
  - [x] `chat.py` (ChatMessageRequest/Response, ChatSessionResponse)
  - [x] `notification.py` (NotificationResponse, UnreadCountResponse)
  - [x] `admin.py` (DashboardMetrics, RiskAnalyticsResponse, **KycReviewRequest**)
- [x] **1.6** Create seed data
  - [x] `backend/seed/products.json` — 5 product definitions from SPEC Section 5
  - [x] `backend/seed/risk_data.json` — 270 historical event records
  - [x] `backend/seed/seed_data.py` — idempotent script (admin user, test user, products, risk data)

**Checkpoint:** `alembic upgrade head && python -m seed.seed_data` — ready to run (requires PostgreSQL)

Vấn đề cần lưu ý: 
- Bcrypt và Passlib bị xung đột version, đã fix. 
- Không cần cài PostgreSQL local, tránh bị xung đột port 5432
- Đã xong, người hoàn thành: Quang + Vinh, người check: Thái
---

### Slice 2: Authentication [2 members] -- DONE
- [x] **2.1** Create `backend/middleware/auth.py` — JWT verify, get_current_user, require_admin
- [x] **2.2** Create `backend/services/auth_service.py` — register (kyc_status=NOT_SUBMITTED), login, refresh, bcrypt, **submit_kyc**, **get_kyc_status**, **review_kyc**
- [x] **2.3** Create `backend/routers/auth.py` — POST register/login/refresh, GET me, **POST kyc/submit, GET kyc/status**
- [x] **2.4** Frontend scaffolding (both apps)
  - [x] User app: index.html, vite.config.js, tailwind.config.js, postcss.config.js, main.js, App.vue, main.css, router/index.js, services/api.js, services/authService.js, stores/auth.js
  - [x] Admin app: same scaffold files (port 5174, sidebar layout)
- [x] **2.5** Auth pages
  - [x] User: LoginView.vue, RegisterView.vue, HomeView.vue, AppHeader.vue, authService.js, **KycView.vue**
  - [x] Admin: LoginView.vue, AdminSidebar.vue, AdminHeader.vue

Người hoàn thành: (team member names), người check: (reviewer)

---

### Slice 3: Wallet System [2 members]
- [x] **3.1** Create `backend/services/wallet_service.py` — top_up, deduct, credit, with FOR UPDATE locking. WalletTransaction links via `policy_id`/`claim_id` FKs
- [x] **3.2** Create `backend/routers/wallet.py` — GET balance, POST topup (**KYC VERIFIED required**), GET transactions
- [x] **3.3** Wallet frontend — walletService.js, stores/wallet.js, WalletView.vue, BalanceCard.vue, TransactionList.vue  

---

### Data Preparation: External Training Data [1 member]
- [ ] **Data.1** Create `backend/utils/crawl_data.py` — utility for fetching and preparing external ML training data
  - [ ] `DataCrawler` class with methods: `create_training_data_dir()`, `save_json_data()`, `save_csv_data()`, `load_json_data()`, `load_csv_data()`
  - [ ] `fetch_flight_delay_data()` — fetch/generate flight delay training records with format `{flight_id, distance, delay_occurred}`
  - [ ] `fetch_weather_data()` — fetch/generate weather event training records with format `{date, region, temperature, humidity, wind_speed, event_occurred}`
  - [ ] Can run standalone: `python -m utils.crawl_data`
  - [ ] Creates `backend/ml_data/` directory and saves training files (JSON/CSV formats)

---

### Slice ML: Risk ML Models [1-2 members]
- [ ] **ML.1** Create `backend/services/ml_models.py` — Base class + 2 classification models
  - [ ] `BaseRiskModel` abstract class with fit(), predict_proba(), save(), load() methods
  - [ ] `FlightDelayModel` — binary classification model (LogisticRegression/RandomForest) → P(flight_delay) ∈ [0.0, 1.0]
  - [ ] `WeatherModel` — binary classification model (LogisticRegression/RandomForest) → P(weather_event) ∈ [0.0, 1.0]
- [ ] **ML.2** Create `backend/seed/train_models.py` — standalone training script
  - [ ] Load training data from **external sources** (CSV/JSON files in `backend/ml_data/`)
  - [ ] Train 2 binary classification models (simple train/test, no optimization needed)
  - [ ] Models output probability via `predict_proba()`: returns P(event=1) as value 0.0-1.0
  - [ ] Save models to `backend/ml_models/{product}.joblib` (joblib format)
  - [ ] Can run standalone: `python -m seed.train_models`
  - [ ] Add scikit-learn, pandas, numpy, joblib to `backend/requirements.txt`
- [ ] **ML.3** Refactor `backend/services/risk_engine.py`
  - [ ] Load models at startup
  - [ ] `calculate_premium(product_id, params)` calls `model.predict_proba(params)` → returns probability (0.0-1.0)
  - [ ] Convert probability to risk multiplier: `risk_multiplier = 0.5 + (probability × 1.5)` (range: 0.5-2.0)
  - [ ] Premium = base_price × risk_multiplier
  - [ ] Return in response: event_probability (%), risk_multiplier, final_premium for user display
  - [ ] Fallback to simple formula if model unavailable
- [ ] **ML.4** Add ML endpoints to `backend/routers/admin.py`
  - [ ] `GET /admin/ml/model-stats` — model last_updated, model file exists
  - [ ] `POST /admin/ml/retrain` — trigger retraining from external data files

**Acceptance Criteria:**
- `python -m seed.train_models` trains 2 binary classification models from external data files
- Models save to `backend/ml_models/flight_delay.joblib` & `backend/ml_models/weather.joblib`
- `risk_engine.calculate_premium()` loads models → calls `predict_proba()` → returns probability
- Premium breakdown shows: event_probability (%), risk_multiplier (0.5-2.0), final_premium
- Fallback formula works if model load fails
- Admin can check model status & trigger retrain via API

---

### Slice 4: Insurance Catalog [2-3 members]
- [ ] **4.1** Create `backend/services/insurance_service.py` — list, get, CRUD, basic risk score
- [ ] **4.2** Create `backend/routers/insurance.py` — GET/POST/PUT/PATCH products
- [ ] **4.3** User catalog UI — InsuranceListView.vue, InsuranceDetailView.vue, ProductCard.vue, RiskGauge.vue, DynamicForm.vue
- [ ] **4.4** Admin product CRUD — ProductsView.vue, ProductFormView.vue, ProductTable.vue

---

### Slice 5: Policy Purchase [2 members]
- [ ] **5.1** ~~Create risk_engine.py~~ (moved to Slice ML — now uses classification models)
- [ ] **5.2** Create `backend/services/policy_service.py` — **KYC VERIFIED check before purchase**; atomic purchase (calc ML premium → check wallet → deduct → create policy); cancel with refund; expire
  - Uses `risk_engine.calculate_premium()` which now calls ML classification models
- [ ] **5.3** Create `backend/routers/policies.py` — calculate-premium, purchase, list, cancel
  - Response includes: event_probability (%), risk_multiplier, final_premium in breakdown
- [ ] **5.4** Purchase UI — PremiumCalculator.vue, MyPoliciesView.vue, DashboardView.vue
  - Display ML probability (%) + risk multiplier + final premium in calculator

**Verify:** Login (KYC verified user) → top up 5000 → calculate Flight Delay premium (shows "X% chance of delay" + multiplier) → purchase → wallet reduced → My Policies shows ACTIVE with ML-calculated premium

---

### Slice 6: Claims + Notifications [2 members]
- [ ] **6.1** Create `backend/services/claims_engine.py` — manual claim, auto claim, admin review
- [ ] **6.2** Create `backend/routers/claims.py` — POST submit, GET list, GET detail
- [ ] **6.3** Create notification service + router — create, list, mark-read, unread-count
- [ ] **6.4** Frontend — NotificationsView.vue, NotificationBell.vue, admin ClaimsView.vue

---

### Slice 7: Admin Dashboard [1-2 members]
- [ ] **7.1** Create `backend/routers/admin.py` — dashboard metrics, user/policy/claim lists, claim review, **GET kyc/pending, PATCH kyc/{user_id}** (approve/reject)
- [ ] **7.2** Admin dashboard UI — DashboardView.vue, PoliciesView.vue, UsersView.vue, StatsCard.vue, **KycReviewView.vue**

---

### Phase 1 Checkpoint
- [ ] Full auth flow works on both apps
- [ ] **KYC flow: user submits → admin approves/rejects → status enforced on transactions**
- [ ] Wallet top-up, balance, transactions work **(top-up blocked without KYC)**
- [ ] 5 products visible in catalog with risk scores
- [ ] **ML binary classification models trained** from external data; displays event probability %
- [ ] Policy purchase and cancel flow complete **(purchase blocked without KYC)**; shows ML probability + multiplier + premium
- [ ] Manual claim -> admin review -> payout works
- [ ] Notifications with unread count
- [ ] Admin dashboard shows real metrics **+ KYC review queue**
- [ ] Swagger docs at /docs are complete

---

## Phase 2 — Intelligence

### Slice 8: AI Chatbot [1-2 members]
- [ ] **8.1** Create `backend/services/chatbot_service.py` — Gemini integration, context injection, fallback
- [ ] **8.2** Create `backend/routers/chatbot.py` — POST message, GET sessions
- [ ] **8.3** Chat widget frontend — ChatWidget.vue, ChatMessage.vue

---

### Slice 9: Risk Engine + Simulation [2-3 members]
- [ ] **9.1** Enhance `backend/services/risk_engine.py` — admin analytics, probability distributions
- [ ] **9.2** Create `backend/services/simulation_engine.py` — slider config, trigger evaluation
- [ ] **9.3** Create `backend/routers/simulation.py` — config, check-trigger, log endpoints
- [ ] **9.4** Simulation UI — SimulationModal.vue, TriggerSlider.vue, ThresholdBar.vue, TriggerResult.vue
- [ ] **9.5** Risk analytics admin — RiskAnalyticsView.vue, RevenueChart.vue, ClaimsChart.vue

---

### Phase 2 Checkpoint
- [ ] Chatbot responds with product-aware advice
- [ ] Simulation sliders work for all 5 products
- [ ] Threshold crossing shows animated "Activated!" with payout
- [ ] Admin risk analytics with interactive charts

---

## Phase 3 — Real-World Integration

### Slice 10: External APIs + Trigger Monitor [1-2 members]
- [ ] **10.1** Create `backend/utils/external_apis.py` — WeatherClient, AviationClient, with logging
- [ ] **10.2** Create `backend/services/trigger_monitor.py` — background job, mock mode, auto-claims
- [ ] **10.3** API monitor UI — ApiMonitorView.vue, ApiStatusCard.vue, TriggerLogTable.vue

---

### Phase 3 Checkpoint
- [ ] External APIs work when keys configured; mock mode otherwise
- [ ] Auto-claims fire on trigger conditions
- [ ] API health dashboard shows status per API

---

## Phase 4 — Polish

### Slice 11: UI/UX + Animations [1-2 members]
- [ ] **11.1** Visual polish — responsive, loading states, empty states, error toasts
- [ ] **11.2** Simulation animations — 5 product-specific CSS/SVG animations

### Slice 12: Hardening [2 members]
- [ ] **12.1** Global error handler middleware (custom exceptions + structured logging used from Phase 1; this slice adds centralized handler + edge case hardening)
- [ ] **12.2** Input validation + rate limiting
- [ ] **12.3** Query optimization (joinedload, pagination)
- [ ] **12.4** Security review (auth, RBAC, CORS, SQL injection)

### Slice 13: Docker + Tests [2 members]
- [ ] **13.1** .env files + Docker compose verification
- [ ] **13.2** Backend test suite (auth, wallet, insurance, policies, claims)

---

### Final Checkpoint
- [ ] All pages responsive on mobile + desktop
- [ ] Simulation animations for all 5 products
- [ ] No security vulnerabilities
- [ ] `docker-compose up` starts full stack from scratch
- [ ] `pytest` all tests pass
- [ ] README.md is accurate and up to date
