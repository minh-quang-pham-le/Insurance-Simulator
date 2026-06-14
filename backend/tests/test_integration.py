"""
INTEGRATION TESTS — AI-Powered Insurance Simulator
===================================================

Mức INTEGRATION: kiểm thử NHIỀU thành phần phối hợp với nhau trên một database
THẬT (SQLite trong bộ nhớ), ở tầng SERVICE (không qua HTTP). Mục tiêu là xác minh
các service + ORM + ràng buộc giao dịch hoạt động đúng khi ghép lại.

Phạm vi:
  * policy_service.purchase_policy  ⇄  risk_engine + wallet_service + DB  (SDD 6.5)
  * Tính ACID: thiếu số dư → rollback, KHÔNG tạo hợp đồng, số dư giữ nguyên  (SDD 7.2)
  * claims_engine.submit_auto_claim ⇄ Claim + Wallet + Policy + Notification (SDD 6.8)

Cách chạy (đứng ở thư mục backend/):
    python -m pytest test_integration.py -v
"""
# --- Bootstrap: SQLite + ánh xạ kiểu PostgreSQL-only (UUID, JSONB) sang SQLite ---
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DATABASE_URL", "sqlite://")
os.environ.setdefault("DEBUG", "False")

import asyncio
import uuid
from datetime import datetime, timezone, timedelta
from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.dialects.postgresql import UUID as _PG_UUID, JSONB as _PG_JSONB


@compiles(_PG_UUID, "sqlite")
def _uuid_sqlite(element, compiler, **kw):
    return "CHAR(36)"


@compiles(_PG_JSONB, "sqlite")
def _jsonb_sqlite(element, compiler, **kw):
    return "JSON"


import models  # noqa: F401 — đăng ký toàn bộ model lên Base.metadata
from config.database import Base
from models.user import User
from models.wallet import Wallet, WalletTransaction
from models.insurance_product import InsuranceProduct
from models.policy import Policy
from models.claim import Claim
from models.notification import Notification
from models.enums import (
    UserRole, KycStatus, PolicyStatus, ClaimStatus, TransactionType, NotificationType,
    ProductCategory,
)
from services import policy_service, claims_engine

# Một database SQLite trong bộ nhớ dùng chung, tạo bảng một lần.
_engine = create_engine(
    "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
)
Base.metadata.create_all(_engine)
_Session = sessionmaker(bind=_engine, autocommit=False, autoflush=False)


@pytest.fixture
def db():
    session = _Session()
    try:
        yield session
    finally:
        session.rollback()
        # Dọn sạch dữ liệu giữa các test để cô lập.
        for table in reversed(Base.metadata.sorted_tables):
            session.execute(table.delete())
        session.commit()
        session.close()


def _make_verified_user_with_balance(db, balance="5000.00"):
    user = User(
        email=f"u_{uuid.uuid4().hex[:8]}@example.com",
        password_hash="x",
        full_name="Integration User",
        role=UserRole.USER,
        kyc_status=KycStatus.VERIFIED,
    )
    db.add(user)
    db.flush()
    wallet = Wallet(user_id=user.id, balance=Decimal(balance), currency="SC")
    db.add(wallet)
    db.commit()
    return user, wallet


def _make_flight_product(db):
    product = InsuranceProduct(
        name="Flight Delay Protection",
        category=ProductCategory.FLIGHT_DELAY,
        description="Pays out on long flight delays.",
        base_payout=Decimal("500.00"),
        min_duration_days=1,
        max_duration_days=30,
        risk_margin=Decimal("0.25"),
        parameters_schema={"fields": [{"name": "delay_threshold_minutes", "default": 120}]},
        trigger_conditions={"rules": [
            {"field": "delay_minutes", "operator": ">=",
             "threshold_param": "delay_threshold_minutes", "payout_multiplier": 1.0}
        ]},
        is_active=True,
    )
    db.add(product)
    db.commit()
    return product


# ---------------------------------------------------------------------------
# 1) Mua hợp đồng: policy_service + risk_engine + wallet_service + DB (SDD 6.5)
# ---------------------------------------------------------------------------

class TestPurchaseIntegration:
    def test_purchase_deducts_wallet_and_persists_policy(self, db):
        user, wallet = _make_verified_user_with_balance(db)
        product = _make_flight_product(db)
        before = wallet.balance

        policy = asyncio.run(
            policy_service.purchase_policy(
                db=db,
                user_id=user.id,
                product_id=product.id,
                parameters={"delay_threshold_minutes": 120},
                duration_days=7,
            )
        )

        assert policy.status == PolicyStatus.ACTIVE
        assert policy.premium_paid > 0

        # Ví bị trừ đúng bằng phí.
        db.refresh(wallet)
        assert wallet.balance == before - policy.premium_paid

        # Có bản ghi giao dịch PREMIUM_PAYMENT gắn với hợp đồng.
        tx = (
            db.query(WalletTransaction)
            .filter(WalletTransaction.policy_id == policy.id)
            .first()
        )
        assert tx is not None
        assert tx.type == TransactionType.PREMIUM_PAYMENT

    def test_insufficient_balance_rolls_back_atomically(self, db):
        """SDD 7.2 (ACID): không đủ tiền ⇒ rollback, không tạo hợp đồng, số dư giữ nguyên."""
        user, wallet = _make_verified_user_with_balance(db, balance="0.00")
        product = _make_flight_product(db)

        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc:
            asyncio.run(
                policy_service.purchase_policy(
                    db=db,
                    user_id=user.id,
                    product_id=product.id,
                    parameters={"delay_threshold_minutes": 120},
                    duration_days=7,
                )
            )
        assert exc.value.status_code == 400

        # Không có hợp đồng nào được lưu, số dư vẫn = 0.
        assert db.query(Policy).filter(Policy.user_id == user.id).count() == 0
        db.refresh(wallet)
        assert wallet.balance == Decimal("0.00")


# ---------------------------------------------------------------------------
# 2) Bồi thường tự động: claims_engine + Wallet + Policy + Notification (SDD 6.8)
# ---------------------------------------------------------------------------

class TestAutoClaimIntegration:
    def test_auto_claim_pays_out_and_updates_all_records(self, db):
        user, wallet = _make_verified_user_with_balance(db, balance="0.00")
        product = _make_flight_product(db)
        policy = Policy(
            user_id=user.id,
            product_id=product.id,
            premium_paid=Decimal("75.00"),
            payout_amount=Decimal("500.00"),
            status=PolicyStatus.ACTIVE,
            parameters={"delay_threshold_minutes": 120},
            start_date=datetime.now(timezone.utc),
            end_date=datetime.now(timezone.utc) + timedelta(days=7),
        )
        db.add(policy)
        db.commit()

        claim = asyncio.run(
            claims_engine.submit_auto_claim(
                db=db,
                policy_id=policy.id,
                trigger_event="Flight delayed 180 minutes",
                trigger_data={"delay_minutes": 180},
            )
        )

        db.refresh(claim)
        db.refresh(policy)
        db.refresh(wallet)

        # Claim đã trả, hợp đồng chuyển CLAIMED, ví được cộng tiền bồi thường.
        assert claim.status == ClaimStatus.PAID
        assert policy.status == PolicyStatus.CLAIMED
        assert wallet.balance == Decimal("500.00")

        # Có giao dịch PAYOUT và thông báo cho người dùng.
        payout_tx = (
            db.query(WalletTransaction)
            .filter(WalletTransaction.claim_id == claim.id)
            .first()
        )
        assert payout_tx is not None
        assert payout_tx.type == TransactionType.PAYOUT

        notif = (
            db.query(Notification)
            .filter(
                Notification.user_id == user.id,
                Notification.type == NotificationType.PAYOUT_RECEIVED,
            )
            .first()
        )
        assert notif is not None
