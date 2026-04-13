"""create all tables

Revision ID: a001
Revises:
Create Date: 2026-04-13 06:57:35.157629
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "a001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# --- Enum types ---
user_role = postgresql.ENUM("USER", "ADMIN", name="userrole", create_type=False)
kyc_status = postgresql.ENUM(
    "NOT_SUBMITTED", "PENDING", "VERIFIED", "REJECTED",
    name="kycstatus", create_type=False,
)
transaction_type = postgresql.ENUM(
    "TOP_UP", "PREMIUM_PAYMENT", "PAYOUT", "REFUND",
    name="transactiontype", create_type=False,
)
product_category = postgresql.ENUM(
    "FLIGHT_DELAY", "CROP_WEATHER", "GADGET", "NATURAL_DISASTER", "RAINFALL_EVENT",
    name="productcategory", create_type=False,
)
policy_status = postgresql.ENUM(
    "ACTIVE", "EXPIRED", "CLAIMED", "CANCELLED",
    name="policystatus", create_type=False,
)
trigger_type = postgresql.ENUM("AUTOMATIC", "MANUAL", name="triggertype", create_type=False)
claim_status = postgresql.ENUM(
    "PENDING", "AUTO_APPROVED", "MANUAL_REVIEW", "APPROVED", "PAID", "REJECTED",
    name="claimstatus", create_type=False,
)
notification_type = postgresql.ENUM(
    "CLAIM_TRIGGERED", "PAYOUT_RECEIVED", "POLICY_EXPIRING", "POLICY_EXPIRED", "SYSTEM",
    name="notificationtype", create_type=False,
)


def upgrade() -> None:
    # Create enum types first
    for enum in [
        user_role, kyc_status, transaction_type, product_category,
        policy_status, trigger_type, claim_status, notification_type,
    ]:
        enum.create(op.get_bind(), checkfirst=True)

    # 1. users
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), unique=True, nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(100), nullable=False),
        sa.Column("role", user_role, nullable=False, server_default="USER"),
        sa.Column("phone_number", sa.String(20), nullable=True),
        sa.Column("kyc_status", kyc_status, nullable=False, server_default="NOT_SUBMITTED"),
        sa.Column("kyc_submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("kyc_rejection_reason", sa.String(500), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_users_email", "users", ["email"])

    # 2. wallets
    op.create_table(
        "wallets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), unique=True, nullable=False),
        sa.Column("balance", sa.Numeric(15, 2), nullable=False, server_default="0"),
        sa.Column("currency", sa.String(10), nullable=False, server_default="SC"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("balance >= 0", name="ck_wallet_balance_non_negative"),
    )

    # 3. insurance_products
    op.create_table(
        "insurance_products",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("category", product_category, nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("short_description", sa.String(300), nullable=True),
        sa.Column("icon_url", sa.String(500), nullable=True),
        sa.Column("base_payout", sa.Numeric(15, 2), nullable=False),
        sa.Column("min_duration_days", sa.Integer(), nullable=False),
        sa.Column("max_duration_days", sa.Integer(), nullable=False),
        sa.Column("risk_margin", sa.Numeric(5, 4), nullable=False, server_default="0.2500"),
        sa.Column("parameters_schema", postgresql.JSONB(), nullable=False),
        sa.Column("trigger_conditions", postgresql.JSONB(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_insurance_products_category_active", "insurance_products", ["category", "is_active"])

    # 4. policies
    op.create_table(
        "policies",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("insurance_products.id"), nullable=False),
        sa.Column("premium_paid", sa.Numeric(15, 2), nullable=False),
        sa.Column("payout_amount", sa.Numeric(15, 2), nullable=False),
        sa.Column("status", policy_status, nullable=False, server_default="ACTIVE"),
        sa.Column("parameters", postgresql.JSONB(), nullable=False),
        sa.Column("start_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_policies_user_status", "policies", ["user_id", "status"])
    op.create_index("ix_policies_status_end_date", "policies", ["status", "end_date"])
    op.create_index("ix_policies_product_id", "policies", ["product_id"])

    # 5. claims
    op.create_table(
        "claims",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("policy_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("policies.id"), nullable=False),
        sa.Column("trigger_type", trigger_type, nullable=False),
        sa.Column("trigger_event", sa.String(500), nullable=True),
        sa.Column("trigger_data", postgresql.JSONB(), nullable=True),
        sa.Column("evidence_urls", postgresql.JSONB(), nullable=True),
        sa.Column("status", claim_status, nullable=False),
        sa.Column("payout_amount", sa.Numeric(15, 2), nullable=False),
        sa.Column("reviewed_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_claims_status", "claims", ["status"])

    # 6. wallet_transactions (depends on wallets, policies, claims)
    op.create_table(
        "wallet_transactions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("wallet_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("wallets.id"), nullable=False),
        sa.Column("type", transaction_type, nullable=False),
        sa.Column("amount", sa.Numeric(15, 2), nullable=False),
        sa.Column("balance_after", sa.Numeric(15, 2), nullable=False),
        sa.Column("description", sa.String(500), nullable=True),
        sa.Column("policy_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("policies.id"), nullable=True),
        sa.Column("claim_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("claims.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_wallet_transactions_wallet_created", "wallet_transactions", ["wallet_id", "created_at"])

    # 7. risk_data
    op.create_table(
        "risk_data",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("product_category", product_category, nullable=False),
        sa.Column("region", sa.String(100), nullable=True),
        sa.Column("event_date", sa.Date(), nullable=False),
        sa.Column("event_type", sa.String(100), nullable=False),
        sa.Column("event_severity", sa.Numeric(10, 2), nullable=True),
        sa.Column("event_data", postgresql.JSONB(), nullable=True),
        sa.Column("source", sa.String(100), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_risk_data_category_region_date", "risk_data", ["product_category", "region", "event_date"])
    op.create_index("ix_risk_data_category_date", "risk_data", ["product_category", "event_date"])

    # 8. notifications
    op.create_table(
        "notifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("type", notification_type, nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("is_read", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("reference_type", sa.String(20), nullable=True),
        sa.Column("reference_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_notifications_user_read_created", "notifications", ["user_id", "is_read", "created_at"])

    # 9. chat_sessions
    op.create_table(
        "chat_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("context_product_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("insurance_products.id"), nullable=True),
        sa.Column("messages", postgresql.JSONB(), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # 10. simulation_sessions
    op.create_table(
        "simulation_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("insurance_products.id"), nullable=False),
        sa.Column("input_parameters", postgresql.JSONB(), nullable=False),
        sa.Column("triggers_activated", postgresql.JSONB(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # 11. api_monitor_logs
    op.create_table(
        "api_monitor_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("api_name", sa.String(50), nullable=False),
        sa.Column("endpoint", sa.String(500), nullable=False),
        sa.Column("method", sa.String(10), nullable=False, server_default="GET"),
        sa.Column("status_code", sa.Integer(), nullable=True),
        sa.Column("response_time_ms", sa.Integer(), nullable=True),
        sa.Column("response_summary", postgresql.JSONB(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("checked_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_api_monitor_logs_name_checked", "api_monitor_logs", ["api_name", "checked_at"])


def downgrade() -> None:
    op.drop_table("api_monitor_logs")
    op.drop_table("simulation_sessions")
    op.drop_table("chat_sessions")
    op.drop_table("notifications")
    op.drop_table("risk_data")
    op.drop_table("wallet_transactions")
    op.drop_table("claims")
    op.drop_table("policies")
    op.drop_table("insurance_products")
    op.drop_table("wallets")
    op.drop_table("users")

    # Drop enum types
    for name in [
        "notificationtype", "claimstatus", "triggertype", "policystatus",
        "productcategory", "transactiontype", "kycstatus", "userrole",
    ]:
        sa.Enum(name=name).drop(op.get_bind(), checkfirst=True)
