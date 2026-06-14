"""
ACCEPTANCE TESTS — AI-Powered Insurance Simulator
==================================================

Mức ACCEPTANCE: kiểm thử hộp đen, đầu-cuối (end-to-end) qua REST API bằng
FastAPI TestClient — đúng cách hai ứng dụng SPA gọi backend. Xác minh các use
case người dùng/quản trị trong Ma trận truy vết của SDD (§7.1) và các yêu cầu
phi chức năng (§7.2).

Một kịch bản xuyên suốt: đăng ký → đăng nhập → KYC → admin duyệt → nạp ví →
xem sản phẩm → mua hợp đồng → nộp claim → admin duyệt chi trả. Kèm các kiểm tra
NFR: yêu cầu token, phân quyền RBAC, không lộ mật khẩu, ACID khi thiếu số dư.

LƯU Ý httpx: FastAPI 0.104.1 dùng "app shortcut" của httpx (bị bỏ ở httpx 0.28).
Hãy ghim:  httpx>=0.27,<0.28

Cách chạy (đứng ở thư mục backend/):
    python -m pytest test_acceptance.py -v
"""
# --- Bootstrap: SQLite + ánh xạ kiểu PostgreSQL-only (UUID, JSONB) ---
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DATABASE_URL", "sqlite://")
os.environ.setdefault("DEBUG", "False")

import uuid
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


import models  # noqa: F401
from config.database import Base, get_db
from app import app
from models.user import User
from models.wallet import Wallet
from models.insurance_product import InsuranceProduct
from models.enums import UserRole, KycStatus, ProductCategory

_engine = create_engine(
    "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
)
Base.metadata.create_all(_engine)
_Session = sessionmaker(bind=_engine, autocommit=False, autoflush=False)

VALID_PASSWORD = "Passw0rd!"  # thoả: hoa + số + ký tự đặc biệt


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(autouse=True)
def _clean():
    """Xoá sạch dữ liệu sau mỗi test để cô lập."""
    yield
    with _engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(table.delete())


@pytest.fixture
def db():
    s = _Session()
    try:
        yield s
    finally:
        s.close()


@pytest.fixture
def client():
    from fastapi.testclient import TestClient

    def _override_get_db():
        s = _Session()
        try:
            yield s
        finally:
            s.close()

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def register_and_login(client):
    def _make(email=None):
        email = email or f"user_{uuid.uuid4().hex[:8]}@example.com"
        r = client.post("/api/v1/auth/register",
                        json={"email": email, "password": VALID_PASSWORD, "full_name": "Test User"})
        assert r.status_code == 201, r.text
        login = client.post("/api/v1/auth/login",
                            json={"email": email, "password": VALID_PASSWORD})
        assert login.status_code == 200, login.text
        token = login.json()["access_token"]
        return r.json(), token, _auth(token)
    return _make


@pytest.fixture
def admin(client, register_and_login, db):
    email = f"admin_{uuid.uuid4().hex[:8]}@example.com"
    user_json, _, _ = register_and_login(email=email)
    row = db.query(User).filter(User.id == uuid.UUID(user_json["id"])).first()
    row.role = UserRole.ADMIN
    db.commit()
    login = client.post("/api/v1/auth/login",
                        json={"email": email, "password": VALID_PASSWORD})
    token = login.json()["access_token"]
    return user_json, token, _auth(token)


@pytest.fixture
def flight_product(db):
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
    db.refresh(product)
    return product


def _premium_body(product_id, days=7):
    return {
        "product_id": str(product_id),
        "parameters": {"airline_code": "VN", "delay_threshold_minutes": 120},
        "duration_days": days,
    }


# ---------------------------------------------------------------------------
# UC001/002/017 — Đăng ký, đăng nhập, hồ sơ + NFR bảo mật
# ---------------------------------------------------------------------------

class TestAuth:
    def test_register_then_login(self, client, register_and_login):
        user_json, token, headers = register_and_login()
        assert user_json["kyc_status"] == "NOT_SUBMITTED"
        me = client.get("/api/v1/auth/me", headers=headers)
        assert me.status_code == 200
        assert me.json()["email"] == user_json["email"]

    def test_password_hash_never_returned(self, client, register_and_login):
        """NFR §7.2: không lộ mật khẩu/băm mật khẩu ra client."""
        user_json, _, _ = register_and_login()
        assert "password" not in user_json and "password_hash" not in user_json

    def test_wrong_password_is_401(self, client, register_and_login):
        user_json, _, _ = register_and_login()
        r = client.post("/api/v1/auth/login",
                        json={"email": user_json["email"], "password": "WrongPass1!"})
        assert r.status_code == 401

    def test_protected_endpoint_requires_token(self, client):
        """NFR §7.2: API được bảo vệ phải có token hợp lệ."""
        assert client.get("/api/v1/auth/me").status_code in (401, 403)


# ---------------------------------------------------------------------------
# UC004/005 — Xem danh mục & chi tiết sản phẩm
# ---------------------------------------------------------------------------

class TestCatalogue:
    def test_list_and_detail(self, client, register_and_login, flight_product):
        _, _, headers = register_and_login()
        listing = client.get("/api/v1/insurance/products", headers=headers)
        assert listing.status_code == 200
        assert listing.json()["total"] >= 1

        detail = client.get(f"/api/v1/insurance/products/{flight_product.id}", headers=headers)
        assert detail.status_code == 200
        assert detail.json()["risk_score"] is not None  # UC005 hiển thị điểm rủi ro


# ---------------------------------------------------------------------------
# UC018 + UC013 — Admin duyệt KYC mở khoá nạp ví (ledger)
# ---------------------------------------------------------------------------

class TestKycAndWallet:
    def test_topup_blocked_until_admin_verifies_kyc(self, client, admin, register_and_login):
        _, _, admin_headers = admin
        user_json, _, user_headers = register_and_login()

        # Chưa KYC ⇒ nạp ví bị chặn 403.
        blocked = client.post("/api/v1/wallet/topup", json={"amount": 100}, headers=user_headers)
        assert blocked.status_code == 403

        # User nộp KYC ⇒ admin duyệt ⇒ VERIFIED.
        client.post("/api/v1/auth/kyc/submit", json={"phone_number": "+84901234567"}, headers=user_headers)
        approve = client.patch(f"/api/v1/admin/kyc/{user_json['id']}",
                               json={"action": "approve"}, headers=admin_headers)
        assert approve.status_code == 200 and approve.json()["kyc_status"] == "VERIFIED"

        # Nạp ví thành công + ghi sổ giao dịch (UC013).
        topup = client.post("/api/v1/wallet/topup", json={"amount": 1000}, headers=user_headers)
        assert topup.status_code == 200 and float(topup.json()["balance"]) == 1000.0
        txs = client.get("/api/v1/wallet/transactions", headers=user_headers).json()
        assert txs["total"] == 1 and txs["transactions"][0]["type"] == "TOP_UP"


# ---------------------------------------------------------------------------
# UC006/007/016/012 — Mua hợp đồng → nộp claim → admin chi trả (E2E)
# ---------------------------------------------------------------------------

class TestPurchaseClaimFlow:
    def _verified_funded(self, client, register_and_login, db):
        user_json, token, headers = register_and_login()
        row = db.query(User).filter(User.id == uuid.UUID(user_json["id"])).first()
        row.kyc_status = KycStatus.VERIFIED
        db.flush()
        wallet = db.query(Wallet).filter(Wallet.user_id == row.id).first()
        wallet.balance = Decimal("5000.00")
        db.commit()
        return user_json, token, headers

    def test_full_purchase_and_claim_payout(
        self, client, register_and_login, admin, flight_product, db
    ):
        _, _, headers = self._verified_funded(client, register_and_login, db)
        _, _, admin_headers = admin

        # UC006: mua hợp đồng ⇒ trừ ví, hợp đồng ACTIVE.
        before = float(client.get("/api/v1/wallet/", headers=headers).json()["balance"])
        buy = client.post("/api/v1/policies/purchase", json=_premium_body(flight_product.id), headers=headers)
        assert buy.status_code == 201, buy.text
        policy = buy.json()
        assert policy["status"] == "ACTIVE"
        after = float(client.get("/api/v1/wallet/", headers=headers).json()["balance"])
        assert round(before - after, 2) == round(float(policy["premium_paid"]), 2)

        # UC007: hợp đồng xuất hiện trong danh sách của user.
        assert client.get("/api/v1/policies", headers=headers).json()["total"] == 1

        # UC016: nộp claim thủ công ⇒ MANUAL_REVIEW.
        claim = client.post("/api/v1/claims",
                            json={"policy_id": policy["id"], "description": "Flight cancelled, please review."},
                            headers=headers)
        assert claim.status_code == 201 and claim.json()["status"] == "MANUAL_REVIEW"

        # UC012: admin duyệt ⇒ claim PAID, ví được cộng tiền bồi thường, hợp đồng CLAIMED.
        bal_before = float(client.get("/api/v1/wallet/", headers=headers).json()["balance"])
        review = client.put(f"/api/v1/admin/claims/{claim.json()['id']}/review",
                            json={"action": "approve"}, headers=admin_headers)
        assert review.status_code == 200 and review.json()["status"] == "PAID"
        bal_after = float(client.get("/api/v1/wallet/", headers=headers).json()["balance"])
        assert round(bal_after - bal_before, 2) == round(float(policy["payout_amount"]), 2)
        assert client.get(f"/api/v1/policies/{policy['id']}", headers=headers).json()["status"] == "CLAIMED"

    def test_purchase_requires_kyc(self, client, register_and_login, flight_product):
        """UC006: chưa VERIFIED ⇒ không mua được."""
        _, _, headers = register_and_login()
        r = client.post("/api/v1/policies/purchase", json=_premium_body(flight_product.id), headers=headers)
        assert r.status_code == 403

    def test_insufficient_balance_is_atomic(self, client, register_and_login, flight_product, db):
        """NFR §7.2 (ACID): verified nhưng số dư 0 ⇒ 400, không tạo hợp đồng, số dư giữ nguyên."""
        user_json, token, headers = register_and_login()
        row = db.query(User).filter(User.id == uuid.UUID(user_json["id"])).first()
        row.kyc_status = KycStatus.VERIFIED
        db.commit()

        r = client.post("/api/v1/policies/purchase", json=_premium_body(flight_product.id), headers=headers)
        assert r.status_code == 400
        assert client.get("/api/v1/policies", headers=headers).json()["total"] == 0
        assert float(client.get("/api/v1/wallet/", headers=headers).json()["balance"]) == 0.0


# ---------------------------------------------------------------------------
# UC014/019 + NFR — Phân quyền RBAC do backend cưỡng chế (SDD 5.6)
# ---------------------------------------------------------------------------

class TestAdminRbac:
    def test_user_cannot_reach_admin(self, client, register_and_login):
        _, _, headers = register_and_login()
        assert client.get("/api/v1/admin/dashboard", headers=headers).status_code == 403

    def test_admin_dashboard_ok(self, client, admin):
        _, _, headers = admin
        r = client.get("/api/v1/admin/dashboard", headers=headers)
        assert r.status_code == 200
        assert "total_users" in r.json()

    def test_only_admin_creates_products(self, client, register_and_login, admin):
        payload = {
            "name": f"Cover {uuid.uuid4().hex[:5]}", "category": "CROP_WEATHER",
            "description": "Rainfall cover", "base_payout": 1000,
            "min_duration_days": 1, "max_duration_days": 60, "risk_margin": 0.3,
            "parameters_schema": {"fields": []}, "trigger_conditions": {"rules": []},
        }
        _, _, user_headers = register_and_login()
        assert client.post("/api/v1/insurance/products", json=payload, headers=user_headers).status_code == 403

        _, _, admin_headers = admin
        assert client.post("/api/v1/insurance/products", json=payload, headers=admin_headers).status_code == 201
