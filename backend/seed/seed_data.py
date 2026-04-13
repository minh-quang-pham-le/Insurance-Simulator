"""
Idempotent seed script.
Creates: admin user, test user with 10000 SC wallet, 5 products, 270+ risk data records.

Usage: python -m seed.seed_data
"""
import json
import uuid
from pathlib import Path
from decimal import Decimal
from datetime import date

from passlib.hash import bcrypt

from config.database import SessionLocal, engine, Base
from models.enums import (
    UserRole, KycStatus, TransactionType, ProductCategory,
)
from models.user import User
from models.wallet import Wallet, WalletTransaction
from models.insurance_product import InsuranceProduct
from models.risk_data import RiskData

SEED_DIR = Path(__file__).parent

ADMIN_EMAIL = "admin@insurance-sim.com"
ADMIN_PASSWORD = "admin123456"
TEST_USER_EMAIL = "testuser@insurance-sim.com"
TEST_USER_PASSWORD = "test123456"
TEST_USER_BALANCE = Decimal("10000.00")


def seed_users(db):
    """Create admin and test user if they don't exist."""
    admin = db.query(User).filter(User.email == ADMIN_EMAIL).first()
    if not admin:
        admin = User(
            id=uuid.uuid4(),
            email=ADMIN_EMAIL,
            password_hash=bcrypt.hash(ADMIN_PASSWORD),
            full_name="System Admin",
            role=UserRole.ADMIN,
            kyc_status=KycStatus.VERIFIED,
            is_active=True,
        )
        db.add(admin)
        admin_wallet = Wallet(
            id=uuid.uuid4(),
            user_id=admin.id,
            balance=Decimal("0"),
            currency="SC",
        )
        db.add(admin_wallet)
        print(f"  Created admin: {ADMIN_EMAIL}")
    else:
        print(f"  Admin already exists: {ADMIN_EMAIL}")

    test_user = db.query(User).filter(User.email == TEST_USER_EMAIL).first()
    if not test_user:
        test_user = User(
            id=uuid.uuid4(),
            email=TEST_USER_EMAIL,
            password_hash=bcrypt.hash(TEST_USER_PASSWORD),
            full_name="Test User",
            role=UserRole.USER,
            kyc_status=KycStatus.VERIFIED,
            phone_number="0901234567",
            is_active=True,
        )
        db.add(test_user)
        db.flush()

        test_wallet = Wallet(
            id=uuid.uuid4(),
            user_id=test_user.id,
            balance=TEST_USER_BALANCE,
            currency="SC",
        )
        db.add(test_wallet)
        db.flush()

        # Record the initial top-up transaction
        tx = WalletTransaction(
            id=uuid.uuid4(),
            wallet_id=test_wallet.id,
            type=TransactionType.TOP_UP,
            amount=TEST_USER_BALANCE,
            balance_after=TEST_USER_BALANCE,
            description="Initial seed balance",
        )
        db.add(tx)
        print(f"  Created test user: {TEST_USER_EMAIL} (balance: {TEST_USER_BALANCE} SC)")
    else:
        print(f"  Test user already exists: {TEST_USER_EMAIL}")

    db.flush()
    return admin


def seed_products(db, admin):
    """Load 5 insurance products from products.json."""
    existing = db.query(InsuranceProduct).count()
    if existing >= 5:
        print(f"  Products already seeded ({existing} found)")
        return

    with open(SEED_DIR / "products.json") as f:
        products_data = json.load(f)

    for p in products_data:
        exists = db.query(InsuranceProduct).filter(
            InsuranceProduct.name == p["name"]
        ).first()
        if exists:
            continue

        product = InsuranceProduct(
            id=uuid.uuid4(),
            name=p["name"],
            category=ProductCategory(p["category"]),
            description=p["description"],
            short_description=p.get("short_description"),
            base_payout=Decimal(str(p["base_payout"])),
            min_duration_days=p["min_duration_days"],
            max_duration_days=p["max_duration_days"],
            risk_margin=Decimal(str(p["risk_margin"])),
            parameters_schema=p["parameters_schema"],
            trigger_conditions=p["trigger_conditions"],
            is_active=True,
            created_by=admin.id,
        )
        db.add(product)
        print(f"  Created product: {p['name']}")

    db.flush()


def seed_risk_data(db):
    """Load historical risk data from risk_data.json."""
    existing = db.query(RiskData).count()
    if existing >= 250:
        print(f"  Risk data already seeded ({existing} records found)")
        return

    with open(SEED_DIR / "risk_data.json") as f:
        risk_records = json.load(f)

    for r in risk_records:
        record = RiskData(
            id=uuid.uuid4(),
            product_category=ProductCategory(r["product_category"]),
            region=r.get("region"),
            event_date=date.fromisoformat(r["event_date"]),
            event_type=r["event_type"],
            event_severity=Decimal(str(r["event_severity"])) if r.get("event_severity") is not None else None,
            event_data=r.get("event_data"),
            source=r["source"],
        )
        db.add(record)

    db.flush()
    print(f"  Loaded {len(risk_records)} risk data records")


def main():
    print("Seeding database...")

    db = SessionLocal()
    try:
        admin = seed_users(db)
        seed_products(db, admin)
        seed_risk_data(db)
        db.commit()
        print("Seed complete!")
    except Exception as e:
        db.rollback()
        print(f"Seed failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
