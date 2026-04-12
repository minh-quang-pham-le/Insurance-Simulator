# AI-Powered Insurance Simulator — Specification

> **Course**: Introduction to Software Engineering
> **Team size**: 5 members
> **Status**: Draft v2
> **Last updated**: 2026-04-13

---

## 1. Objective

Build a simplified fintech platform that introduces users to **risk management and micro-insurance** through a digital interface. The system serves two audiences through separate frontends backed by a single API and database:

| Audience | Interface | Purpose |
|----------|-----------|---------|
| **End users** | User Web App | Browse, simulate, purchase micro-insurance; manage virtual wallet; receive automated claim payouts |
| **Insurance company (admin)** | Admin Dashboard | Create insurance products, set risk parameters, monitor APIs, view analytics |

The platform is positioned as a **third-party software product** delivered to an insurance company (professor's role). It demonstrates:
- How insurance premiums are calculated from risk data
- How risk pooling works in micro-insurance
- How parametric insurance uses real-world data triggers to auto-settle claims
- How AI assists both buyers and sellers in making informed decisions

### What "AI-Powered" Means

1. **AI Chatbot** — An LLM-powered advisor that helps users understand products and make purchase decisions, using product catalog data and risk statistics as context.
2. **AI Risk Probability Engine** — A statistical engine that calculates event probabilities from historical data, displayed to both users (as a simple risk score) and admins (as detailed actuarial analytics).

---

## 2. System Architecture

```
┌─────────────────┐     ┌─────────────────┐
│  User Web App   │     │ Admin Dashboard  │
│  (Vue 3 + Vite) │     │ (Vue 3 + Vite)  │
│  Port 5173      │     │  Port 5174       │
└────────┬────────┘     └────────┬─────────┘
         │          HTTPS        │
         └──────────┬────────────┘
                    ▼
          ┌─────────────────┐
          │  FastAPI Backend │──────► External APIs
          │   Port 8000     │       (Weather, Aviation)
          └────────┬────────┘
                   │              ┌──────────────┐
                   │              │  Gemini API   │
                   │              │  (AI Chatbot) │
                   │              └──────────────┘
                   ▼
          ┌─────────────────┐
          │  PostgreSQL 15  │
          │   Port 5432     │
          └─────────────────┘
```

**Key architectural decisions:**
- **Single backend** serves both frontends. Role-based access control (RBAC) in middleware determines what each JWT token can access.
- **Two separate frontend apps** for security isolation and UX optimization. They share no runtime state.
- **Parametric triggers** run as a background task (or cron) in the backend, polling external APIs and auto-settling claims when thresholds are crossed.

---

## 3. User Roles & Flows

### 3.1 End User (role: `USER`)

```
Register → Login → Top up wallet → Browse insurance catalog
                                         │
                                         ▼
                                  Click on a product
                                         │
                                         ▼
                          ┌── Insurance Detail Page ──┐
                          │                           │
                          │  Product info + premium   │
                          │  Risk probability section │
                          │  AI chatbot widget        │
                          │  [Try Simulation] button  │
                          │                           │
                          └───────────┬───────────────┘
                                      │
                         ┌────────────┼────────────┐
                         ▼            ▼            ▼
                    Try simulation  Chat with    Fill params
                    (explore        AI advisor   & purchase
                     triggers)          │            │
                         │              │            ▼
                         └──────────────┴──► Purchase policy
                                                   │
                                                   ▼
                                          Policy is ACTIVE
                                                   │
                                     ┌─────────────┼─────────────┐
                                     ▼                           ▼
                               Trigger event              Policy expires
                               detected (auto)            (no claim)
                                     │
                                     ▼
                              Claim auto-approved
                              Payout → Wallet
                              Notification sent
```

### 3.2 Admin (role: `ADMIN`)

```
Login → Dashboard (overview metrics)
              │
    ┌─────────┼──────────┬──────────────┬───────────────┐
    ▼         ▼          ▼              ▼               ▼
 Manage    View all    Monitor      Risk analytics   System
 products  policies    API status   & loss ratios    settings
 (CRUD)    & claims    & triggers
```

---

## 4. Core Features

### 4.1 Authentication & User Management

| Requirement | Detail |
|-------------|--------|
| Registration | Email + password + full name. Default role: `USER`. |
| Login | Returns JWT access token (expires 24h) + refresh token (expires 7d). |
| Password | Hashed with bcrypt. Minimum 8 characters. |
| Admin creation | First admin seeded. Subsequent admins created by existing admins. |
| Protected routes | All endpoints except `/auth/register` and `/auth/login` require valid JWT. |
| KYC verification | Users must complete KYC before any financial transaction (wallet top-up, policy purchase). |

**KYC verification flow:**
```
User registers → kyc_status = NOT_SUBMITTED
       │
       ▼
User fills KYC form (phone number + identity confirmation)
       │
       ▼
kyc_status = PENDING  →  Appears in Admin dashboard queue
       │
       ├── Admin approves → kyc_status = VERIFIED ✓
       │
       └── Admin rejects (with reason) → kyc_status = REJECTED
                │
                └── User can resubmit → back to PENDING
```

| Action | Requires KYC VERIFIED? |
|--------|------------------------|
| Browse products, view catalog | No |
| Use AI chatbot | No |
| Run simulations | No |
| Wallet top-up | **Yes** |
| Purchase policy | **Yes** |

**Acceptance criteria:**
- [ ] User can register, login, and receive a JWT
- [ ] Invalid credentials return 401
- [ ] Expired tokens are rejected; refresh token can issue a new access token
- [ ] Admin-only endpoints return 403 for USER role
- [ ] User can submit KYC (phone number + identity details); status moves to PENDING
- [ ] Admin can approve or reject KYC with reason
- [ ] Rejected users can resubmit; status cycles back to PENDING
- [ ] Wallet top-up and policy purchase are blocked until kyc_status = VERIFIED

### 4.2 Virtual Wallet System

Users start with a balance of **0 SimCoin (SC)**. They must top up before purchasing insurance.

| Operation | Description |
|-----------|-------------|
| Top up | Add SC to wallet (simulated — no real payment gateway) |
| Premium payment | Deducted when purchasing a policy |
| Claim payout | Credited when a claim is auto-approved |
| Refund | Credited if a policy is cancelled before activation |

All wallet operations create a `WalletTransaction` record for audit trail. Balance can never go negative — purchases are rejected if insufficient funds.

> **KYC gate:** Wallet top-up requires `kyc_status = VERIFIED`. Users with NOT_SUBMITTED, PENDING, or REJECTED status receive a 403 with a message directing them to complete KYC first.

**Acceptance criteria:**
- [ ] Wallet top-up is blocked if user's KYC is not VERIFIED
- [ ] User can top up any positive amount
- [ ] Policy purchase deducts exact premium from wallet
- [ ] Claim payout credits wallet and creates transaction record
- [ ] Concurrent transactions maintain balance consistency (DB-level locking)

### 4.3 Insurance Product Catalog

Products are **micro-insurance**: short-term, small-premium, specific-trigger. Each product is defined by a **JSON parameter schema** (what inputs the user must provide) and **trigger conditions** (when the auto-claim fires).

**Five initial product types:**

| # | Product | Trigger Type | External API |
|---|---------|-------------|--------------|
| 1 | Flight Delay Protection | Flight delayed ≥ threshold or cancelled | AviationStack |
| 2 | Crop Weather Insurance | Weather metric exceeds threshold | OpenWeatherMap |
| 3 | Gadget Repair Coverage | Manual claim with evidence (non-parametric) | None |
| 4 | Typhoon / Natural Disaster Insurance | Severe weather alert ≥ threshold | OpenWeatherMap |
| 5 | Rainfall Event Insurance | Rainfall on specific date > threshold | OpenWeatherMap |

Admins create new products by uploading a JSON configuration file that defines the parameter schema and trigger conditions. The system renders forms dynamically from the schema. See [Section 5](#5-insurance-products) for detailed product definitions.

**Acceptance criteria:**
- [ ] Users can browse all active products with descriptions, premiums, and risk scores
- [ ] Admin can create/update/deactivate products via the dashboard
- [ ] Product forms are dynamically rendered from `parameters_schema` JSON

### 4.4 Policy Purchase Flow

1. System verifies user's `kyc_status = VERIFIED` (rejects with 403 if not)
2. User selects a product and fills in parameters (flight number, location, etc.)
3. System calculates personalized premium using the risk engine
4. User reviews premium, payout amount, and risk score
5. User confirms purchase → premium deducted from wallet → policy created as `ACTIVE`
6. System begins monitoring trigger conditions for this policy

**Premium calculation formula:**
```
event_probability = historical_events / total_observations
adjusted_probability = event_probability × season_factor × location_factor
base_premium = adjusted_probability × payout_amount × (1 + risk_margin)
daily_rate = base_premium / base_observation_period_days
policy_premium = daily_rate × policy_duration_days
```

Where:
- `risk_margin`: Company profit margin (default 25%, configurable per product)
- `season_factor`: 0.5–3.0 based on time of year (e.g., typhoon season = higher)
- `location_factor`: 0.5–2.0 based on geographic risk

**Acceptance criteria:**
- [ ] Purchase is blocked if user's KYC is not VERIFIED
- [ ] Premium is calculated dynamically and shown before purchase
- [ ] Wallet balance is validated before purchase
- [ ] Policy status transitions: PENDING → ACTIVE → EXPIRED | CLAIMED | CANCELLED

### 4.5 Automated Claims Processing (Parametric Engine)

The core differentiator. A background service periodically checks external APIs against active policies' trigger conditions.

**Flow:**
```
Background job (every 5–15 min)
  → Fetch active policies with parametric triggers
  → For each policy, check external API
  → If trigger_condition met:
      → Create Claim (status: AUTO_APPROVED)
      → Credit user wallet with payout_amount
      → Send notification
      → Update policy status to CLAIMED
```

**For demo/simulation mode:** When real APIs are unavailable, the system uses a mock trigger service that generates realistic events based on historical probability distributions.

**Acceptance criteria:**
- [ ] Active parametric policies are checked automatically on schedule
- [ ] When trigger fires, claim is created and wallet is credited within one check cycle
- [ ] User receives notification of claim payout
- [ ] Non-parametric products (gadget) require manual claim submission

### 4.6 AI Chatbot (Insurance Advisor)

A floating chat widget on the user app that provides context-aware insurance advice.

**Implementation:**
- **LLM**: Google Gemini 2.0 Flash (free tier: 15 RPM, 1M tokens/day)
- **Fallback**: Groq API with Llama 3.1 (free tier, fast inference)
- **Context injection**: System prompt includes product catalog, user's current page, existing policies, and relevant risk data
- **Scope**: Advisory only — the chatbot cannot execute purchases or wallet operations

**System prompt template:**
```
You are an insurance advisor for the Insurance Simulator platform.
Help users understand micro-insurance products and make informed decisions.

Available products: {product_catalog_summary}
User is currently viewing: {current_product_or_page}
User's existing policies: {user_active_policies}
Relevant risk data: {risk_statistics}

Rules:
- Be educational — explain insurance concepts simply
- Be honest about risks vs. benefits
- Reference actual risk scores and probabilities
- Never guarantee outcomes
- Keep responses concise (under 150 words)
```

**Acceptance criteria:**
- [ ] Chat widget appears on insurance browsing/detail pages
- [ ] Chatbot responds with product-specific advice using real risk data
- [ ] Chat history persists within a session
- [ ] Graceful fallback if LLM API is unavailable

### 4.7 AI Risk Probability Engine

Calculates and displays event probabilities based on historical data.

**Data flow:**
```
Historical event data (seeded + API-collected)
  → Statistical calculation per product/region/season
  → Risk score (1–10 for users, detailed % for admins)
  → Feeds into: premium calculation, chatbot context, simulation engine
```

**Risk score display:**
| Score | Label | Color | Probability Range |
|-------|-------|-------|-------------------|
| 1–3 | Low Risk | Green | 0–15% |
| 4–6 | Moderate Risk | Yellow | 15–40% |
| 7–10 | High Risk | Red | 40–100% |

**For admins**, the dashboard shows:
- Probability tables per product/region/season
- Historical event frequency charts
- Loss ratio (total payouts / total premiums collected)
- Trend analysis over time

**Acceptance criteria:**
- [ ] Every product displays a risk score to users
- [ ] Risk scores update when new historical data is added
- [ ] Admin dashboard shows detailed probability analytics
- [ ] Risk data feeds into premium calculation formula

### 4.8 Simulation Mode

An interactive **trigger demonstration** accessed from the Insurance Detail page via a "Try Simulation" button. It shows users exactly **when and how** their insurance would activate — making the parametric model tangible. Simulation is always tied to a specific product.

#### 4.8.1 Trigger Explorer (Core — build first)

Opens as a modal or expandable panel within the Insurance Detail page.

- **Sliders** for each trigger parameter, generated from the product's `parameters_schema`
  - Flight Delay: delay minutes slider (0–360 min), with threshold line at user-chosen threshold
  - Crop Weather: rainfall mm slider (0–200 mm), temperature slider, etc.
  - Typhoon: severity level slider (1–5)
  - Rainfall Event: rainfall mm slider for event day
- **Threshold visualization**: slider track has colored zones — green (safe) → yellow (approaching, 80% of threshold) → red (triggered)
- **When parameter crosses threshold**: animated popup notification — *"Insurance Activated! Your policy pays out 500 SC"*
- **All trigger scenarios listed**: for products with multiple triggers (e.g., Flight Delay has "delay ≥ 120min" AND "cancelled"), each scenario is shown as a separate threshold on the slider or as tabs
- **Payout multiplier display**: if the product has tiered payouts (e.g., cancellation = 150%), show the payout amount changing as the user explores different scenarios

#### 4.8.2 Animated Scenario (Enhancement — build after core works)

A mini visual story for each product category, driven by the slider values:

| Product | Animation |
|---------|-----------|
| Flight Delay | Airplane icon at gate, clock ticking up. As delay slider increases: clock turns yellow, then red. At threshold: "DELAYED" stamp, payout animation. At cancellation: "CANCELLED" stamp with higher payout. |
| Crop Weather | Farm/field scene with weather indicators. Slider controls rain intensity or temperature. Clouds darken, rain increases. At threshold: flood/drought visual, farmer receives payout. |
| Typhoon | Map of Vietnam with storm icon. Severity slider controls storm size/color. At threshold: alert banner, payout credited. At max severity: double payout animation. |
| Rainfall Event | Outdoor event scene (wedding/festival). Rain slider controls clouds and rainfall. At threshold: event disrupted visual, payout notification. |
| Gadget | Device with damage indicator. Shows claim submission flow instead (since non-parametric): take photo → submit → admin reviews → payout. |

These animations are CSS/SVG-based, lightweight, and educational. They make the abstract concept of "parametric trigger" concrete and visually engaging.

**Acceptance criteria:**
- [ ] Simulation opens from the Insurance Detail page for the specific product
- [ ] Sliders reflect the product's actual trigger parameters and thresholds
- [ ] Crossing a threshold shows a clear "Activated!" notification with payout amount
- [ ] Multiple trigger scenarios per product are all explorable
- [ ] User must be logged in to access simulation

### 4.9 Notification System

| Event | Notification |
|-------|-------------|
| Claim auto-triggered | "Your Flight Delay policy was triggered! **500 SC** has been credited to your wallet." |
| Policy expiring (24h before) | "Your Crop Weather policy expires tomorrow." |
| Policy expired (no claim) | "Your policy has expired with no claim triggered." |
| Payout received | "You received a payout of **X SC**." |
| System announcement | Admin broadcasts (maintenance, new products, etc.) |

Notifications are stored in DB and displayed as a bell icon with unread count in the user app header.

**Acceptance criteria:**
- [ ] Notifications are created for all listed events
- [ ] Unread count badge updates in real-time (polling or WebSocket)
- [ ] User can mark notifications as read

### 4.10 Admin Dashboard

**Dashboard home** shows key metrics:
- Total active users / new registrations
- Total active policies / total premiums collected
- Total claims paid / loss ratio
- Revenue (premiums − payouts)
- API health status

**Product Management:**
- Create product: upload JSON parameter schema + trigger conditions, set base premium, payout, duration range
- Edit/deactivate existing products
- View purchase statistics per product

**Claims Monitor:**
- List of all claims (filterable by status, product, date)
- Manual approval/rejection for non-parametric claims (gadget)

**Risk Analytics:**
- Probability tables and charts per product
- Loss ratio trends
- Regional risk heatmap (if location data available)

**API Monitor:**
- Status of each external API (last check, response time, error rate)
- Trigger event log

---

## 5. Insurance Products — Detailed Definitions

### 5.1 Flight Delay Protection

```json
{
  "name": "Flight Delay Protection",
  "category": "FLIGHT_DELAY",
  "description": "Get automatic payout when your flight is delayed beyond your chosen threshold or cancelled.",
  "parameters_schema": {
    "fields": [
      {"name": "airline_code", "type": "select", "label": "Airline", "required": true,
       "options": [
         {"value": "VN", "label": "Vietnam Airlines"},
         {"value": "VJ", "label": "VietJet Air"},
         {"value": "QH", "label": "Bamboo Airways"}
       ]},
      {"name": "flight_number", "type": "string", "label": "Flight Number", "required": true, "placeholder": "e.g., VN123"},
      {"name": "departure_date", "type": "date", "label": "Departure Date", "required": true},
      {"name": "delay_threshold_minutes", "type": "number", "label": "Delay Threshold (minutes)", "required": true,
       "default": 120, "min": 60, "max": 360, "step": 30}
    ]
  },
  "trigger_conditions": {
    "type": "PARAMETRIC",
    "api_source": "aviation",
    "rules": [
      {"field": "delay_minutes", "operator": ">=", "threshold_param": "delay_threshold_minutes", "payout_multiplier": 1.0},
      {"field": "status", "operator": "==", "value": "CANCELLED", "payout_multiplier": 1.5}
    ]
  },
  "base_payout": 500,
  "duration_range_days": [1, 7],
  "risk_margin": 0.25
}
```

### 5.2 Crop Weather Insurance

```json
{
  "name": "Crop Weather Insurance",
  "category": "CROP_WEATHER",
  "description": "Protect your harvest against extreme weather conditions. Automatic payout when weather thresholds are breached.",
  "parameters_schema": {
    "fields": [
      {"name": "location_name", "type": "string", "label": "Farm Location", "required": true, "placeholder": "e.g., Can Tho, Mekong Delta"},
      {"name": "location_lat", "type": "number", "label": "Latitude", "required": true},
      {"name": "location_lon", "type": "number", "label": "Longitude", "required": true},
      {"name": "crop_type", "type": "select", "label": "Crop Type", "required": true,
       "options": [
         {"value": "rice", "label": "Rice"},
         {"value": "coffee", "label": "Coffee"},
         {"value": "pepper", "label": "Pepper"},
         {"value": "cashew", "label": "Cashew"}
       ]},
      {"name": "weather_metric", "type": "select", "label": "Weather Risk", "required": true,
       "options": [
         {"value": "rainfall_mm", "label": "Excessive Rainfall (flood)"},
         {"value": "temp_celsius", "label": "Extreme Temperature"},
         {"value": "drought_days", "label": "Drought (no rain for X days)"}
       ]},
      {"name": "threshold", "type": "number", "label": "Trigger Threshold", "required": true},
      {"name": "comparison", "type": "select", "label": "Trigger When", "required": true,
       "options": [
         {"value": "ABOVE", "label": "Above threshold"},
         {"value": "BELOW", "label": "Below threshold"}
       ]}
    ]
  },
  "trigger_conditions": {
    "type": "PARAMETRIC",
    "api_source": "openweathermap",
    "check_interval_hours": 6,
    "rules": [
      {"field": "{weather_metric}", "operator": "{comparison}", "threshold_param": "threshold", "payout_multiplier": 1.0}
    ]
  },
  "base_payout": 1000,
  "duration_range_days": [30, 180],
  "risk_margin": 0.30
}
```

### 5.3 Gadget Repair Coverage (Non-Parametric)

```json
{
  "name": "Gadget Repair Coverage",
  "category": "GADGET",
  "description": "Coverage for accidental damage to your personal devices. Submit a claim with evidence for manual review.",
  "parameters_schema": {
    "fields": [
      {"name": "device_type", "type": "select", "label": "Device Type", "required": true,
       "options": [
         {"value": "smartphone", "label": "Smartphone"},
         {"value": "laptop", "label": "Laptop"},
         {"value": "tablet", "label": "Tablet"},
         {"value": "smartwatch", "label": "Smartwatch"}
       ]},
      {"name": "brand", "type": "string", "label": "Brand", "required": true},
      {"name": "model", "type": "string", "label": "Model", "required": true},
      {"name": "purchase_date", "type": "date", "label": "Device Purchase Date", "required": true},
      {"name": "coverage_type", "type": "select", "label": "Coverage Type", "required": true,
       "options": [
         {"value": "SCREEN_DAMAGE", "label": "Screen Damage"},
         {"value": "WATER_DAMAGE", "label": "Water Damage"},
         {"value": "MALFUNCTION", "label": "Hardware Malfunction"},
         {"value": "ALL_RISK", "label": "All Risks (higher premium)"}
       ]}
    ]
  },
  "trigger_conditions": {
    "type": "MANUAL",
    "requires": ["description", "photo_evidence"],
    "review": "ADMIN"
  },
  "base_payout": 300,
  "duration_range_days": [30, 365],
  "risk_margin": 0.35
}
```

### 5.4 Typhoon / Natural Disaster Insurance

```json
{
  "name": "Typhoon Insurance",
  "category": "NATURAL_DISASTER",
  "description": "Automatic payout when a typhoon or severe weather event meets the alert threshold in your area.",
  "parameters_schema": {
    "fields": [
      {"name": "location_name", "type": "string", "label": "Location", "required": true, "placeholder": "e.g., Da Nang"},
      {"name": "location_lat", "type": "number", "label": "Latitude", "required": true},
      {"name": "location_lon", "type": "number", "label": "Longitude", "required": true},
      {"name": "disaster_type", "type": "select", "label": "Disaster Type", "required": true,
       "options": [
         {"value": "TYPHOON", "label": "Typhoon"},
         {"value": "FLOOD", "label": "Flood"},
         {"value": "EARTHQUAKE", "label": "Earthquake"}
       ]},
      {"name": "severity_threshold", "type": "number", "label": "Minimum Severity Level (1-5)", "required": true, "min": 1, "max": 5, "default": 3}
    ]
  },
  "trigger_conditions": {
    "type": "PARAMETRIC",
    "api_source": "openweathermap_alerts",
    "rules": [
      {"field": "alert_severity", "operator": ">=", "threshold_param": "severity_threshold", "payout_multiplier": 1.0},
      {"field": "alert_severity", "operator": ">=", "value": 5, "payout_multiplier": 2.0}
    ]
  },
  "base_payout": 2000,
  "duration_range_days": [30, 180],
  "risk_margin": 0.20
}
```

### 5.5 Rainfall Event Insurance

```json
{
  "name": "Rainfall Event Insurance",
  "category": "RAINFALL_EVENT",
  "description": "Protection against rain ruining your outdoor event. Automatic payout if rainfall exceeds threshold on your event date.",
  "parameters_schema": {
    "fields": [
      {"name": "event_name", "type": "string", "label": "Event Name", "required": true, "placeholder": "e.g., Wedding, Festival"},
      {"name": "location_name", "type": "string", "label": "Location", "required": true},
      {"name": "location_lat", "type": "number", "label": "Latitude", "required": true},
      {"name": "location_lon", "type": "number", "label": "Longitude", "required": true},
      {"name": "event_date", "type": "date", "label": "Event Date", "required": true},
      {"name": "rainfall_threshold_mm", "type": "number", "label": "Rainfall Threshold (mm)", "required": true, "default": 10, "min": 5, "max": 100}
    ]
  },
  "trigger_conditions": {
    "type": "PARAMETRIC",
    "api_source": "openweathermap",
    "check_on": "event_date",
    "rules": [
      {"field": "rainfall_mm", "operator": ">=", "threshold_param": "rainfall_threshold_mm", "payout_multiplier": 1.0},
      {"field": "rainfall_mm", "operator": ">=", "value": 50, "payout_multiplier": 1.5}
    ]
  },
  "base_payout": 200,
  "duration_range_days": [1, 3],
  "risk_margin": 0.20
}
```

---

## 6. Data Models

### 6.1 Entity Relationship Overview

```
User 1──1 Wallet 1──* WalletTransaction
 │
 ├──* Policy *──1 InsuranceProduct
 │     │
 │     └──* Claim
 │
 ├──* Notification
 ├──* ChatSession
 └──* SimulationSession

InsuranceProduct ──* RiskData (via category)
InsuranceProduct ──* Policy

ApiMonitorLog (standalone)
```

### 6.2 Model Definitions

#### `User`
| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | UUID | PK, default uuid4 | |
| email | VARCHAR(255) | UNIQUE, NOT NULL, indexed | |
| password_hash | VARCHAR(255) | NOT NULL | bcrypt hashed |
| full_name | VARCHAR(100) | NOT NULL | |
| role | ENUM('USER','ADMIN') | NOT NULL, default 'USER' | |
| phone_number | VARCHAR(20) | nullable | For KYC and profile |
| kyc_status | ENUM('NOT_SUBMITTED','PENDING','VERIFIED','REJECTED') | NOT NULL, default 'NOT_SUBMITTED' | Must be VERIFIED for transactions |
| kyc_submitted_at | TIMESTAMP | nullable | When user last submitted KYC |
| kyc_rejection_reason | VARCHAR(500) | nullable | Admin's reason if REJECTED |
| is_active | BOOLEAN | NOT NULL, default TRUE | Soft delete |
| created_at | TIMESTAMP | NOT NULL, default now() | |
| updated_at | TIMESTAMP | NOT NULL, auto-update | |

#### `Wallet`
| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | UUID | PK | |
| user_id | UUID | FK → User.id, UNIQUE, NOT NULL | One wallet per user |
| balance | DECIMAL(15,2) | NOT NULL, default 0, CHECK ≥ 0 | |
| currency | VARCHAR(10) | NOT NULL, default 'SC' | SimCoin |
| created_at | TIMESTAMP | NOT NULL, default now() | |
| updated_at | TIMESTAMP | NOT NULL, auto-update | |

#### `WalletTransaction`
| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | UUID | PK | |
| wallet_id | UUID | FK → Wallet.id, NOT NULL | |
| type | ENUM('TOP_UP','PREMIUM_PAYMENT','PAYOUT','REFUND') | NOT NULL | |
| amount | DECIMAL(15,2) | NOT NULL | Always positive; type determines direction |
| balance_after | DECIMAL(15,2) | NOT NULL | Wallet balance after this transaction |
| description | VARCHAR(500) | | Human-readable description |
| policy_id | UUID | FK → Policy.id, nullable | Set for PREMIUM_PAYMENT and REFUND |
| claim_id | UUID | FK → Claim.id, nullable | Set for PAYOUT |
| created_at | TIMESTAMP | NOT NULL, default now() | Immutable audit log |

**Index:** `(wallet_id, created_at DESC)` for transaction history queries.

#### `InsuranceProduct`
| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | UUID | PK | |
| name | VARCHAR(200) | NOT NULL | |
| category | ENUM('FLIGHT_DELAY','CROP_WEATHER','GADGET','NATURAL_DISASTER','RAINFALL_EVENT') | NOT NULL | |
| description | TEXT | NOT NULL | Full description |
| short_description | VARCHAR(300) | | For card previews |
| icon_url | VARCHAR(500) | nullable | Product icon |
| base_payout | DECIMAL(15,2) | NOT NULL | Default payout amount |
| min_duration_days | INTEGER | NOT NULL | |
| max_duration_days | INTEGER | NOT NULL | |
| risk_margin | DECIMAL(5,4) | NOT NULL, default 0.25 | e.g., 0.25 = 25% |
| parameters_schema | JSONB | NOT NULL | Defines user input form (see Section 5) |
| trigger_conditions | JSONB | NOT NULL | Defines when auto-claim fires |
| is_active | BOOLEAN | NOT NULL, default TRUE | |
| created_by | UUID | FK → User.id, nullable | Admin who created |
| created_at | TIMESTAMP | NOT NULL, default now() | |
| updated_at | TIMESTAMP | NOT NULL, auto-update | |

**Index:** `(category, is_active)` for catalog browsing.

#### `Policy`
| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | UUID | PK | |
| user_id | UUID | FK → User.id, NOT NULL | |
| product_id | UUID | FK → InsuranceProduct.id, NOT NULL | |
| premium_paid | DECIMAL(15,2) | NOT NULL | Actual premium calculated at purchase |
| payout_amount | DECIMAL(15,2) | NOT NULL | Agreed payout (may differ from product default) |
| status | ENUM('ACTIVE','EXPIRED','CLAIMED','CANCELLED') | NOT NULL, default 'ACTIVE' | |
| parameters | JSONB | NOT NULL | User-provided values (flight#, location, etc.) |
| start_date | TIMESTAMP | NOT NULL | |
| end_date | TIMESTAMP | NOT NULL | |
| created_at | TIMESTAMP | NOT NULL, default now() | |
| updated_at | TIMESTAMP | NOT NULL, auto-update | |

**Indexes:**
- `(user_id, status)` — "my active policies"
- `(status, end_date)` — background job: find active policies to check / expire
- `(product_id)` — admin analytics: policies per product

#### `Claim`
| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | UUID | PK | |
| policy_id | UUID | FK → Policy.id, NOT NULL | |
| trigger_type | ENUM('AUTOMATIC','MANUAL') | NOT NULL | Parametric vs. gadget claims |
| trigger_event | VARCHAR(500) | | Human-readable: "Flight VN123 delayed 180 min" |
| trigger_data | JSONB | nullable | Raw API response that triggered the claim |
| evidence_urls | JSONB | nullable | For manual claims: photo evidence URLs |
| status | ENUM('PENDING','AUTO_APPROVED','MANUAL_REVIEW','APPROVED','PAID','REJECTED') | NOT NULL | |
| payout_amount | DECIMAL(15,2) | NOT NULL | May differ from policy payout (multipliers) |
| reviewed_by | UUID | FK → User.id, nullable | Admin who reviewed (for manual claims) |
| processed_at | TIMESTAMP | nullable | When payout was executed |
| created_at | TIMESTAMP | NOT NULL, default now() | |

**Index:** `(status)` for admin claims queue.

#### `RiskData`
| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | UUID | PK | |
| product_category | ENUM (same as InsuranceProduct.category) | NOT NULL | |
| region | VARCHAR(100) | nullable | Geographic region or "GLOBAL" |
| event_date | DATE | NOT NULL | When the event occurred |
| event_type | VARCHAR(100) | NOT NULL | e.g., "flight_delay", "heavy_rainfall" |
| event_severity | DECIMAL(10,2) | nullable | Numeric severity (delay mins, rainfall mm) |
| event_data | JSONB | | Full event details |
| source | VARCHAR(100) | NOT NULL | API name or "SEED_DATA" |
| created_at | TIMESTAMP | NOT NULL, default now() | |

**Indexes:**
- `(product_category, region, event_date)` — probability calculations
- `(product_category, event_date)` — time-series queries

This table is populated by:
1. **Seed data** — Historical datasets loaded during setup
2. **API collection** — Trigger monitor stores events as they occur
3. **Admin upload** — Bulk historical data import

#### `Notification`
| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | UUID | PK | |
| user_id | UUID | FK → User.id, NOT NULL | |
| type | ENUM('CLAIM_TRIGGERED','PAYOUT_RECEIVED','POLICY_EXPIRING','POLICY_EXPIRED','SYSTEM') | NOT NULL | |
| title | VARCHAR(200) | NOT NULL | |
| message | TEXT | NOT NULL | |
| is_read | BOOLEAN | NOT NULL, default FALSE | |
| reference_type | VARCHAR(20) | nullable | 'policy', 'claim', etc. |
| reference_id | UUID | nullable | Links to related entity |
| created_at | TIMESTAMP | NOT NULL, default now() | |

**Index:** `(user_id, is_read, created_at DESC)` — unread notifications first.

#### `ChatSession`
| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | UUID | PK | |
| user_id | UUID | FK → User.id, NOT NULL | |
| context_product_id | UUID | FK → InsuranceProduct.id, nullable | Product user was viewing |
| messages | JSONB | NOT NULL, default '[]' | Array of {role, content, timestamp} |
| created_at | TIMESTAMP | NOT NULL, default now() | |
| updated_at | TIMESTAMP | NOT NULL, auto-update | |

#### `SimulationSession`
| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | UUID | PK | |
| user_id | UUID | FK → User.id, NOT NULL | Logged-in users only |
| product_id | UUID | FK → InsuranceProduct.id, NOT NULL | |
| input_parameters | JSONB | NOT NULL | Slider values at time of session |
| triggers_activated | JSONB | NOT NULL | Which thresholds were crossed |
| created_at | TIMESTAMP | NOT NULL, default now() | |

#### `ApiMonitorLog`
| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | UUID | PK | |
| api_name | VARCHAR(50) | NOT NULL | e.g., "openweathermap", "aviationstack" |
| endpoint | VARCHAR(500) | NOT NULL | Full URL called |
| method | VARCHAR(10) | NOT NULL, default 'GET' | |
| status_code | INTEGER | nullable | HTTP status (null if timeout) |
| response_time_ms | INTEGER | nullable | |
| response_summary | JSONB | nullable | Key fields from response |
| error_message | TEXT | nullable | |
| checked_at | TIMESTAMP | NOT NULL, default now() | |

**Index:** `(api_name, checked_at DESC)` — recent health per API.

### 6.3 Enum Definitions (Python)

```python
import enum

class UserRole(str, enum.Enum):
    USER = "USER"
    ADMIN = "ADMIN"

class KycStatus(str, enum.Enum):
    NOT_SUBMITTED = "NOT_SUBMITTED"
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"

class TransactionType(str, enum.Enum):
    TOP_UP = "TOP_UP"
    PREMIUM_PAYMENT = "PREMIUM_PAYMENT"
    PAYOUT = "PAYOUT"
    REFUND = "REFUND"

class ProductCategory(str, enum.Enum):
    FLIGHT_DELAY = "FLIGHT_DELAY"
    CROP_WEATHER = "CROP_WEATHER"
    GADGET = "GADGET"
    NATURAL_DISASTER = "NATURAL_DISASTER"
    RAINFALL_EVENT = "RAINFALL_EVENT"

class PolicyStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    CLAIMED = "CLAIMED"
    CANCELLED = "CANCELLED"

class TriggerType(str, enum.Enum):
    AUTOMATIC = "AUTOMATIC"
    MANUAL = "MANUAL"

class ClaimStatus(str, enum.Enum):
    PENDING = "PENDING"
    AUTO_APPROVED = "AUTO_APPROVED"
    MANUAL_REVIEW = "MANUAL_REVIEW"
    APPROVED = "APPROVED"
    PAID = "PAID"
    REJECTED = "REJECTED"

class NotificationType(str, enum.Enum):
    CLAIM_TRIGGERED = "CLAIM_TRIGGERED"
    PAYOUT_RECEIVED = "PAYOUT_RECEIVED"
    POLICY_EXPIRING = "POLICY_EXPIRING"
    POLICY_EXPIRED = "POLICY_EXPIRED"
    SYSTEM = "SYSTEM"

    # SimulationType enum removed — simulation is now a single
    # trigger-explorer experience, no type distinction needed
```

---

## 7. API Design

Base URL: `http://localhost:8000/api/v1`

### 7.1 Authentication
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/auth/register` | Create user account | None |
| POST | `/auth/login` | Get JWT tokens | None |
| POST | `/auth/refresh` | Refresh access token | Refresh token |
| GET | `/auth/me` | Get current user profile | JWT |
| POST | `/auth/kyc/submit` | Submit KYC verification (phone + identity) | USER |
| GET | `/auth/kyc/status` | Check own KYC status | USER |

### 7.2 Wallet
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/wallet` | Get wallet balance | USER |
| POST | `/wallet/topup` | Add SimCoins | USER |
| GET | `/wallet/transactions` | Transaction history (paginated) | USER |

### 7.3 Insurance Products
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/insurance/products` | List active products | USER |
| GET | `/insurance/products/{id}` | Product detail + risk score | USER |
| POST | `/insurance/products` | Create product | ADMIN |
| PUT | `/insurance/products/{id}` | Update product | ADMIN |
| PATCH | `/insurance/products/{id}/status` | Activate/deactivate | ADMIN |

### 7.4 Policies
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/policies/calculate-premium` | Calculate premium (preview) | USER |
| POST | `/policies/purchase` | Purchase a policy | USER |
| GET | `/policies` | List user's policies | USER |
| GET | `/policies/{id}` | Policy detail | USER |
| POST | `/policies/{id}/cancel` | Cancel policy | USER |

### 7.5 Claims
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/claims` | Submit manual claim (gadget) | USER |
| GET | `/claims` | List user's claims | USER |
| GET | `/claims/{id}` | Claim detail | USER |

### 7.6 Simulation
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/simulation/products/{product_id}/config` | Get slider config + thresholds for a product | USER |
| POST | `/simulation/products/{product_id}/check-trigger` | Check if given parameter values trigger a claim | USER |
| POST | `/simulation/products/{product_id}/log` | Log a simulation session (analytics) | USER |

### 7.7 Chatbot
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/chat/message` | Send message, get AI response | USER |
| GET | `/chat/sessions` | List chat sessions | USER |
| GET | `/chat/sessions/{id}` | Get chat history | USER |

### 7.8 Admin
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/admin/dashboard` | Dashboard metrics | ADMIN |
| GET | `/admin/kyc/pending` | List users with PENDING KYC | ADMIN |
| PATCH | `/admin/kyc/{user_id}` | Approve or reject KYC (with reason) | ADMIN |
| GET | `/admin/users` | List all users (paginated) | ADMIN |
| GET | `/admin/policies` | All policies (filterable) | ADMIN |
| GET | `/admin/claims` | All claims (filterable) | ADMIN |
| PUT | `/admin/claims/{id}/review` | Approve/reject manual claim | ADMIN |
| GET | `/admin/risk-analytics` | Risk data & loss ratios | ADMIN |
| GET | `/admin/api-monitor` | External API health | ADMIN |
| POST | `/admin/risk-data/import` | Import historical data | ADMIN |

### 7.9 Notifications
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/notifications` | List notifications (paginated) | USER |
| GET | `/notifications/unread-count` | Unread count | USER |
| PATCH | `/notifications/{id}/read` | Mark as read | USER |
| PATCH | `/notifications/read-all` | Mark all as read | USER |

---

## 8. Project Structure

### 8.1 Recommended Layout

```
Insurance-Simulator/
│
├── backend/                          # FastAPI backend
│   ├── app.py                        # FastAPI app entry + router registration
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py               # Pydantic BaseSettings (env vars)
│   │   └── database.py               # SQLAlchemy engine, SessionLocal, Base
│   ├── models/
│   │   ├── __init__.py               # Import all models (for Alembic discovery)
│   │   ├── base.py                   # Base model with id, created_at, updated_at
│   │   ├── user.py                   # User model
│   │   ├── wallet.py                 # Wallet + WalletTransaction models
│   │   ├── insurance_product.py      # InsuranceProduct model
│   │   ├── policy.py                 # Policy model
│   │   ├── claim.py                  # Claim model
│   │   ├── risk_data.py              # RiskData model
│   │   ├── notification.py           # Notification model
│   │   ├── chat_session.py           # ChatSession model
│   │   ├── simulation_session.py     # SimulationSession model
│   │   └── api_monitor_log.py        # ApiMonitorLog model
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── auth.py                   # Register, Login, Token schemas
│   │   ├── user.py                   # UserResponse, UserUpdate
│   │   ├── wallet.py                 # TopUp, TransactionResponse
│   │   ├── insurance.py              # ProductCreate, ProductResponse
│   │   ├── policy.py                 # PurchaseRequest, PolicyResponse
│   │   ├── claim.py                  # ClaimCreate, ClaimResponse
│   │   ├── simulation.py             # SimulationRequest, SimulationResult
│   │   ├── chat.py                   # ChatMessage, ChatResponse
│   │   └── notification.py           # NotificationResponse
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── wallet.py
│   │   ├── insurance.py
│   │   ├── policies.py
│   │   ├── claims.py
│   │   ├── simulation.py
│   │   ├── chatbot.py
│   │   ├── notifications.py
│   │   └── admin.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py           # JWT creation, password hashing
│   │   ├── wallet_service.py         # Balance operations with locking
│   │   ├── insurance_service.py      # Product CRUD
│   │   ├── policy_service.py         # Purchase flow, status management
│   │   ├── claims_engine.py          # Auto-claim processing
│   │   ├── risk_engine.py            # Probability calculations
│   │   ├── simulation_engine.py      # Trigger exploration, threshold checking
│   │   ├── chatbot_service.py        # LLM API integration
│   │   └── trigger_monitor.py        # External API polling + mock service
│   ├── middleware/
│   │   ├── __init__.py
│   │   └── auth.py                   # JWT verification, role checking
│   ├── utils/
│   │   ├── __init__.py
│   │   └── helpers.py                # Shared utilities
│   ├── alembic/
│   │   ├── env.py
│   │   ├── script.py.mako
│   │   └── versions/                 # Migration files
│   ├── seed/
│   │   ├── __init__.py
│   │   ├── seed_data.py              # Script to populate initial data
│   │   ├── products.json             # 5 product definitions
│   │   └── risk_data.json            # Historical event data for risk engine
│   ├── alembic.ini
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── .env.example
│   └── README.md
│
├── frontend-user/                    # Vue 3 — End user app
│   ├── src/
│   │   ├── main.js
│   │   ├── App.vue
│   │   ├── router/
│   │   │   └── index.js
│   │   ├── stores/                   # Pinia state management
│   │   │   ├── auth.js
│   │   │   ├── wallet.js
│   │   │   ├── insurance.js
│   │   │   └── notification.js
│   │   ├── views/
│   │   │   ├── HomeView.vue
│   │   │   ├── LoginView.vue
│   │   │   ├── RegisterView.vue
│   │   │   ├── DashboardView.vue
│   │   │   ├── InsuranceListView.vue
│   │   │   ├── InsuranceDetailView.vue  # Includes risk section, chatbot, simulation trigger
│   │   │   ├── WalletView.vue
│   │   │   ├── MyPoliciesView.vue
│   │   │   └── NotificationsView.vue
│   │   ├── components/
│   │   │   ├── common/               # Header, Footer, Loading, etc.
│   │   │   ├── insurance/            # ProductCard, RiskGauge, PremiumCalc
│   │   │   ├── simulation/           # SimulationModal, TriggerSlider, ThresholdBar, ScenarioAnimation
│   │   │   ├── wallet/               # BalanceCard, TransactionList
│   │   │   └── chat/                 # ChatWidget, ChatMessage
│   │   ├── services/                 # Axios API wrappers
│   │   ├── assets/
│   │   └── utils/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   ├── .env.example
│   ├── Dockerfile
│   └── README.md
│
├── frontend-admin/                   # Vue 3 — Admin dashboard
│   ├── src/
│   │   ├── main.js
│   │   ├── App.vue
│   │   ├── router/
│   │   ├── stores/
│   │   ├── views/
│   │   │   ├── LoginView.vue
│   │   │   ├── DashboardView.vue
│   │   │   ├── ProductsView.vue
│   │   │   ├── ProductFormView.vue
│   │   │   ├── PoliciesView.vue
│   │   │   ├── ClaimsView.vue
│   │   │   ├── RiskAnalyticsView.vue
│   │   │   ├── ApiMonitorView.vue
│   │   │   └── UsersView.vue
│   │   ├── components/
│   │   │   ├── common/
│   │   │   ├── dashboard/            # StatsCard, RevenueChart, ClaimsChart
│   │   │   ├── products/             # ProductTable, SchemaEditor
│   │   │   └── monitoring/           # ApiStatusCard, TriggerLogTable
│   │   ├── services/
│   │   ├── assets/
│   │   └── utils/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   ├── .env.example
│   ├── Dockerfile
│   └── README.md
│
├── docker-compose.yml                # Orchestrates: DB + Backend + User App + Admin App
├── SPEC.md                           # This file
└── README.md                         # Project overview
```

### 8.2 Notes on Structure

- **Rename from current**: `InsuranceSimulatorBackend/` → `backend/`, `InsuranceSimulatorFrontend/` → `frontend-user/`, add `frontend-admin/`. The current folder names work too — this is a suggestion for cleanliness.
- **Two frontend apps** share no runtime code. If shared utilities emerge, extract to a local npm package or copy as needed.
- **Backend follows a layered pattern**: Router → Service → Model. Routers handle HTTP, services handle business logic, models handle persistence.

---

## 9. Tech Stack

### Backend
| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.10+ | Runtime |
| FastAPI | 0.104+ | Web framework |
| SQLAlchemy | 2.0+ | ORM |
| Alembic | 1.13+ | Database migrations |
| PostgreSQL | 15 | Database |
| Pydantic | 2.5+ | Request/response validation |
| Uvicorn | 0.24+ | ASGI server |
| PyJWT / python-jose | latest | JWT token handling |
| bcrypt / passlib | latest | Password hashing |
| httpx | 0.25+ | Async HTTP client (external APIs) |
| APScheduler | 3.10+ | Background job scheduling (trigger monitor) |
| google-generativeai | latest | Gemini API (chatbot) |
| numpy | latest | Risk calculations, Monte Carlo |
| pytest | 7.4+ | Testing |

### Frontend (both apps)
| Technology | Version | Purpose |
|------------|---------|---------|
| Vue.js | 3.3+ | UI framework |
| Vite | 5.0+ | Build tool |
| Vue Router | 4.3+ | Client-side routing |
| Pinia | 2.1+ | State management |
| Axios | 1.6+ | HTTP client |
| TailwindCSS | 3.4+ | Utility-first CSS |
| PrimeVue | 4.0+ | Component library (tables, forms, dialogs) |
| ApexCharts + vue3-apexcharts | latest | Interactive charts (simulation, analytics) |

**Why TailwindCSS + PrimeVue**: TailwindCSS provides full design control for custom layouts and branding. PrimeVue provides pre-built complex components (DataTable, Calendar, Dialog, Toast) that would take weeks to build from scratch, plus built-in themes that look professional out of the box.

### External APIs
| API | Free Tier | Purpose |
|-----|-----------|---------|
| Google Gemini 2.0 Flash | 15 RPM, 1M tokens/day | AI chatbot |
| OpenWeatherMap | 60 calls/min, 1M calls/month | Weather data (crop, typhoon, rainfall) |
| AviationStack | 100 requests/month | Flight status data |

### Infrastructure
| Technology | Purpose |
|------------|---------|
| Docker + Docker Compose | Containerized local deployment |
| Git | Version control |

---

## 10. Commands

### Backend
```bash
# Setup
python -m venv venv
source venv/Scripts/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Database
alembic upgrade head               # Run migrations
python -m seed.seed_data            # Seed initial data

# Run
uvicorn app:app --reload --port 8000

# Test
pytest
pytest --cov=.                      # With coverage

# Migrations
alembic revision --autogenerate -m "description"
alembic upgrade head
alembic downgrade -1                # Rollback one step
```

### Frontend (both apps)
```bash
# Setup
npm install

# Run
npm run dev                         # User app: 5173, Admin app: 5174

# Build
npm run build

# Lint
npm run lint
```

### Docker (from project root)
```bash
docker-compose up -d                # Start all services
docker-compose down                 # Stop all services
docker-compose logs -f backend      # View backend logs
docker-compose exec db psql -U postgres -d insurance_simulator_db  # DB shell
```

---

## 11. Code Style & Conventions

### Python (Backend)
- **Formatter**: Black (line length 88)
- **Linter**: Ruff
- **Naming**: `snake_case` for functions/variables, `PascalCase` for classes, `UPPER_SNAKE_CASE` for constants
- **Type hints**: Required on all function signatures
- **Docstrings**: Only on service-layer public methods (not every function)
- **Imports**: stdlib → third-party → local, separated by blank lines
- **Async**: Use `async def` for all route handlers and service methods that do I/O

### JavaScript/Vue (Frontend)
- **Formatter**: Prettier
- **Linter**: ESLint with `eslint-plugin-vue`
- **Components**: `<script setup>` composition API (no Options API)
- **Naming**: `PascalCase` for components, `camelCase` for functions/variables, `kebab-case` for CSS classes
- **State**: Pinia stores, no direct prop drilling beyond 2 levels
- **API calls**: Always in `services/` files, never directly in components

### Error Handling (Backend)
- **Structured logging**: Use Python `logging` module with format `[%(asctime)s] %(levelname)s %(name)s: %(message)s`
- **Log levels**: DEBUG (dev detail), INFO (request flow, wallet ops), WARNING (recoverable issues), ERROR (failures, external API errors)
- **Log targets**: All API requests, wallet operations, trigger checks, claim processing, KYC actions
- **Custom exceptions**: Define business-logic exceptions (`InsufficientBalanceError`, `KycNotVerifiedError`, `PolicyNotFoundError`, `InvalidPolicyStateError`, etc.)
- **Exception handlers**: Register FastAPI exception handlers that return consistent JSON error responses:
  ```json
  {"detail": "KYC verification required", "error_code": "KYC_NOT_VERIFIED"}
  ```
- **Never** expose internal stack traces or database errors to the client — log them server-side, return a generic message with an error code

### Git
- **Branch naming**: `feature/description`, `fix/description`, `db/description`
- **Commit messages**: Conventional Commits (`feat:`, `fix:`, `refactor:`, `docs:`, `test:`)
- **PR rule**: No direct push to `main`. All changes via PR with at least 1 review.

---

## 12. Testing Strategy

### Backend
| Layer | What to Test | Tool |
|-------|-------------|------|
| Models | Model creation, relationships, constraints | pytest + SQLAlchemy test session |
| Schemas | Pydantic validation (valid/invalid inputs) | pytest |
| Services | Business logic (premium calc, wallet ops, claims) | pytest + mock DB |
| Routers | HTTP status codes, auth, request/response shape | pytest + httpx TestClient |
| Integration | Full flows (register → topup → purchase → claim) | pytest + test DB |

### Frontend
| Layer | What to Test | Tool |
|-------|-------------|------|
| Components | Render, user interaction, prop behavior | Vitest + Vue Test Utils |
| Stores | State mutations, actions, getters | Vitest |
| E2E | Full user flows in browser | Cypress or Playwright (optional) |

### Minimum test targets
- All wallet operations (top-up, purchase deduction, payout credit, insufficient funds)
- Premium calculation formula with different inputs
- Policy lifecycle state transitions
- Auth flow (register, login, token refresh, role-based access)
- Claims engine (trigger detection, payout, notification creation)

---

## 13. Development Phases

### Phase 1 — Foundation (MVP with Seed Data)
> Goal: Demonstrate all core features using seeded/fake data. No real API calls.

- Database models + Alembic migrations
- Seed data (products, risk data, sample users)
- Auth system (register, login, JWT, KYC verification flow)
- KYC: user submission form, admin review queue, status enforcement on transactions
- Wallet (top-up, balance, transactions)
- Insurance catalog (browse, detail, risk score display)
- Policy purchase flow (premium calculation, wallet deduction)
- Basic automated claims with mock trigger service
- Notification system
- User app: Home, Login, Register, Dashboard, Insurance List/Detail, Wallet, My Policies
- Admin app: Login, Dashboard, Products, Policies, Claims, KYC Review Queue

**Deliverable**: Fully functional local demo with fake data that shows all features end-to-end.

### Phase 2 — Intelligence
> Goal: Add AI features and interactive tools that differentiate the platform.

- AI chatbot integration (Gemini API) on Insurance Detail page
- Risk probability engine (historical data analysis) displayed on Insurance Detail page
- Simulation mode: Trigger Explorer with sliders + threshold visualization (within Detail page)
- Simulation enhancement: Animated scenarios per product category (CSS/SVG)
- Interactive charts for risk data visualization
- Admin risk analytics dashboard

### Phase 3 — Real-World Integration
> Goal: Connect to real external APIs for production-grade parametric triggers.

- OpenWeatherMap integration (weather products)
- AviationStack integration (flight products)
- Background trigger monitor service
- API health monitoring dashboard
- Fallback to mock data when APIs are unavailable

### Phase 4 — Polish & Hardening
> Goal: Production readiness.

- UI/UX refinement, responsive design
- Error handling and edge cases
- Performance optimization (query optimization, pagination)
- Security audit (input validation, rate limiting, SQL injection prevention)
- Docker Compose for full-stack deployment
- Final documentation

---

## 14. Boundaries

### Always Do
- Validate all user inputs server-side (never trust the frontend)
- Enforce KYC verification (`kyc_status = VERIFIED`) before wallet top-up and policy purchase
- Use parameterized queries (SQLAlchemy handles this by default)
- Hash passwords with bcrypt before storing
- Return appropriate HTTP status codes (400, 401, 403, 404, 422, 500)
- Use database transactions for multi-step operations (purchase = debit wallet + create policy)
- Log all wallet transactions immutably
- Use structured logging for all backend operations; never expose internal errors to clients
- Keep the two frontends independent (no shared runtime state)

### Ask First
- Before adding a new insurance product category (requires schema + trigger design)
- Before changing the premium calculation formula
- Before adding new external API dependencies
- Before modifying the database schema after Phase 1 is delivered
- Before changing any accepted feature behavior

### Never Do
- Store plaintext passwords
- Allow wallet balance to go negative
- Delete wallet transactions (append-only audit log)
- Let the chatbot execute actions (purchases, transfers) — advisory only
- Skip database migrations (no manual SQL changes)
- Expose internal error details to the client in production
- Store real financial data or accept real payments
