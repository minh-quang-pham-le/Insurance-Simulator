# Entity Relationship Diagram — Insurance Simulator

> Auto-generated from SQLAlchemy models (Slice 1). Matches SPEC Section 6.2.

## ERD (Mermaid)

```mermaid
erDiagram
    %% ──────────────────────────────────────────────
    %% CORE ENTITIES
    %% ──────────────────────────────────────────────

    User {
        UUID id PK
        VARCHAR_255 email UK "UNIQUE, indexed"
        VARCHAR_255 password_hash "bcrypt hashed"
        VARCHAR_100 full_name
        ENUM_UserRole role "USER | ADMIN"
        VARCHAR_20 phone_number "nullable, for KYC"
        ENUM_KycStatus kyc_status "NOT_SUBMITTED | PENDING | VERIFIED | REJECTED"
        TIMESTAMP kyc_submitted_at "nullable"
        VARCHAR_500 kyc_rejection_reason "nullable"
        BOOLEAN is_active "default TRUE"
        TIMESTAMP created_at
        TIMESTAMP updated_at
    }

    Wallet {
        UUID id PK
        UUID user_id FK "UNIQUE → User.id"
        DECIMAL_15_2 balance "CHECK >= 0"
        VARCHAR_10 currency "default SC"
        TIMESTAMP created_at
        TIMESTAMP updated_at
    }

    WalletTransaction {
        UUID id PK
        UUID wallet_id FK "→ Wallet.id"
        ENUM_TransactionType type "TOP_UP | PREMIUM_PAYMENT | PAYOUT | REFUND"
        DECIMAL_15_2 amount "always positive"
        DECIMAL_15_2 balance_after
        VARCHAR_500 description "nullable"
        UUID policy_id FK "nullable → Policy.id"
        UUID claim_id FK "nullable → Claim.id"
        TIMESTAMP created_at "immutable audit log"
    }

    InsuranceProduct {
        UUID id PK
        VARCHAR_200 name
        ENUM_ProductCategory category "FLIGHT_DELAY | CROP_WEATHER | GADGET | NATURAL_DISASTER | RAINFALL_EVENT"
        TEXT description
        VARCHAR_300 short_description "nullable"
        VARCHAR_500 icon_url "nullable"
        DECIMAL_15_2 base_payout
        INTEGER min_duration_days
        INTEGER max_duration_days
        DECIMAL_5_4 risk_margin "default 0.25"
        JSONB parameters_schema "defines user input form"
        JSONB trigger_conditions "defines auto-claim rules"
        BOOLEAN is_active "default TRUE"
        UUID created_by FK "nullable → User.id"
        TIMESTAMP created_at
        TIMESTAMP updated_at
    }

    Policy {
        UUID id PK
        UUID user_id FK "→ User.id"
        UUID product_id FK "→ InsuranceProduct.id"
        DECIMAL_15_2 premium_paid
        DECIMAL_15_2 payout_amount
        ENUM_PolicyStatus status "ACTIVE | EXPIRED | CLAIMED | CANCELLED"
        JSONB parameters "user-provided values"
        TIMESTAMP start_date
        TIMESTAMP end_date
        TIMESTAMP created_at
        TIMESTAMP updated_at
    }

    Claim {
        UUID id PK
        UUID policy_id FK "→ Policy.id"
        ENUM_TriggerType trigger_type "AUTOMATIC | MANUAL"
        VARCHAR_500 trigger_event "nullable"
        JSONB trigger_data "nullable, raw API response"
        JSONB evidence_urls "nullable, photo evidence"
        ENUM_ClaimStatus status "PENDING | AUTO_APPROVED | MANUAL_REVIEW | APPROVED | PAID | REJECTED"
        DECIMAL_15_2 payout_amount
        UUID reviewed_by FK "nullable → User.id"
        TIMESTAMP processed_at "nullable"
        TIMESTAMP created_at
    }

    RiskData {
        UUID id PK
        ENUM_ProductCategory product_category
        VARCHAR_100 region "nullable"
        DATE event_date
        VARCHAR_100 event_type
        DECIMAL_10_2 event_severity "nullable"
        JSONB event_data "nullable"
        VARCHAR_100 source
        TIMESTAMP created_at
    }

    Notification {
        UUID id PK
        UUID user_id FK "→ User.id"
        ENUM_NotificationType type "CLAIM_TRIGGERED | PAYOUT_RECEIVED | POLICY_EXPIRING | POLICY_EXPIRED | SYSTEM"
        VARCHAR_200 title
        TEXT message
        BOOLEAN is_read "default FALSE"
        VARCHAR_20 reference_type "nullable"
        UUID reference_id "nullable"
        TIMESTAMP created_at
    }

    ChatSession {
        UUID id PK
        UUID user_id FK "→ User.id"
        UUID context_product_id FK "nullable → InsuranceProduct.id"
        JSONB messages "array of role-content-timestamp"
        TIMESTAMP created_at
        TIMESTAMP updated_at
    }

    SimulationSession {
        UUID id PK
        UUID user_id FK "→ User.id"
        UUID product_id FK "→ InsuranceProduct.id"
        JSONB input_parameters
        JSONB triggers_activated
        TIMESTAMP created_at
    }

    ApiMonitorLog {
        UUID id PK
        VARCHAR_50 api_name
        VARCHAR_500 endpoint
        VARCHAR_10 method "default GET"
        INTEGER status_code "nullable"
        INTEGER response_time_ms "nullable"
        JSONB response_summary "nullable"
        TEXT error_message "nullable"
        TIMESTAMP checked_at
    }

    %% ──────────────────────────────────────────────
    %% RELATIONSHIPS
    %% ──────────────────────────────────────────────

    User ||--|| Wallet : "has one"
    User ||--o{ Policy : "purchases"
    User ||--o{ Notification : "receives"
    User ||--o{ ChatSession : "starts"
    User ||--o{ SimulationSession : "runs"

    Wallet ||--o{ WalletTransaction : "logs"

    InsuranceProduct ||--o{ Policy : "is purchased as"
    InsuranceProduct ||--o{ ChatSession : "context for"
    InsuranceProduct ||--o{ SimulationSession : "simulated with"

    Policy ||--o{ Claim : "triggers"

    WalletTransaction }o--o| Policy : "references (premium/refund)"
    WalletTransaction }o--o| Claim : "references (payout)"

    Claim }o--o| User : "reviewed by (admin)"
    InsuranceProduct }o--o| User : "created by (admin)"
```

## Relationship Summary

| From | To | Cardinality | FK Column | Notes |
|------|----|-------------|-----------|-------|
| User | Wallet | 1:1 | `wallets.user_id` | UNIQUE constraint, one wallet per user |
| User | Policy | 1:N | `policies.user_id` | User purchases many policies |
| User | Notification | 1:N | `notifications.user_id` | |
| User | ChatSession | 1:N | `chat_sessions.user_id` | |
| User | SimulationSession | 1:N | `simulation_sessions.user_id` | |
| User | InsuranceProduct | 1:N | `insurance_products.created_by` | Admin creates products (nullable) |
| User | Claim | 1:N | `claims.reviewed_by` | Admin reviews claims (nullable) |
| Wallet | WalletTransaction | 1:N | `wallet_transactions.wallet_id` | Immutable audit log |
| InsuranceProduct | Policy | 1:N | `policies.product_id` | |
| InsuranceProduct | ChatSession | 1:N | `chat_sessions.context_product_id` | Optional context |
| InsuranceProduct | SimulationSession | 1:N | `simulation_sessions.product_id` | |
| Policy | Claim | 1:N | `claims.policy_id` | |
| Policy | WalletTransaction | 1:N | `wallet_transactions.policy_id` | PREMIUM_PAYMENT, REFUND |
| Claim | WalletTransaction | 1:N | `wallet_transactions.claim_id` | PAYOUT |
| RiskData | *(logical)* InsuranceProduct | via `product_category` | No FK | Linked by enum category value |
| ApiMonitorLog | — | Standalone | — | No foreign keys |

## Indexes

| Table | Index Name | Columns | Purpose |
|-------|-----------|---------|---------|
| users | ix_users_email | `email` | Login lookups |
| insurance_products | ix_insurance_products_category_active | `category, is_active` | Catalog browsing |
| policies | ix_policies_user_status | `user_id, status` | "My active policies" |
| policies | ix_policies_status_end_date | `status, end_date` | Expiry background job |
| policies | ix_policies_product_id | `product_id` | Admin analytics |
| claims | ix_claims_status | `status` | Admin claims queue |
| wallet_transactions | ix_wallet_transactions_wallet_created | `wallet_id, created_at` | Transaction history |
| risk_data | ix_risk_data_category_region_date | `product_category, region, event_date` | Probability calcs |
| risk_data | ix_risk_data_category_date | `product_category, event_date` | Time-series queries |
| notifications | ix_notifications_user_read_created | `user_id, is_read, created_at` | Unread-first listing |
| api_monitor_logs | ix_api_monitor_logs_name_checked | `api_name, checked_at` | Recent health per API |

## Enum Definitions

| Enum | Values |
|------|--------|
| **UserRole** | `USER`, `ADMIN` |
| **KycStatus** | `NOT_SUBMITTED`, `PENDING`, `VERIFIED`, `REJECTED` |
| **TransactionType** | `TOP_UP`, `PREMIUM_PAYMENT`, `PAYOUT`, `REFUND` |
| **ProductCategory** | `FLIGHT_DELAY`, `CROP_WEATHER`, `GADGET`, `NATURAL_DISASTER`, `RAINFALL_EVENT` |
| **PolicyStatus** | `ACTIVE`, `EXPIRED`, `CLAIMED`, `CANCELLED` |
| **TriggerType** | `AUTOMATIC`, `MANUAL` |
| **ClaimStatus** | `PENDING`, `AUTO_APPROVED`, `MANUAL_REVIEW`, `APPROVED`, `PAID`, `REJECTED` |
| **NotificationType** | `CLAIM_TRIGGERED`, `PAYOUT_RECEIVED`, `POLICY_EXPIRING`, `POLICY_EXPIRED`, `SYSTEM` |

## Constraints

| Table | Constraint | Type | Rule |
|-------|-----------|------|------|
| wallets | `ck_wallet_balance_non_negative` | CHECK | `balance >= 0` |
| wallets | `user_id` | UNIQUE | One wallet per user |
| users | `email` | UNIQUE | No duplicate accounts |
| wallet_transactions | — | Append-only by convention | Never delete transactions |
