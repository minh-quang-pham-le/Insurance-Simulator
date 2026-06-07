"""
Idempotent seed script.
Creates: admin user, test user with 10000 SC wallet, 2 products, 120 risk data records.

Usage: python -m seed.seed_data
"""
import json
import uuid
from pathlib import Path
from decimal import Decimal
from datetime import date

import pandas as pd
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
    """Load insurance products from products.json. Always syncs schema/labels."""
    with open(SEED_DIR / "products.json") as f:
        products_data = json.load(f)

    for p in products_data:
        exists = db.query(InsuranceProduct).filter(
            InsuranceProduct.name == p["name"]
        ).first()
        if exists:
            exists.parameters_schema = p["parameters_schema"]
            exists.trigger_conditions = p["trigger_conditions"]
            exists.description = p["description"]
            exists.short_description = p.get("short_description")
            print(f"  Updated product schema: {p['name']}")
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
    """Seed risk_data table from ml_data CSV files. Idempotent — skips if already loaded."""
    ML_DATA_DIR = SEED_DIR.parent / "ml_data"

    csv_count = db.query(RiskData).filter(RiskData.source.like("ml_data/%")).count()
    if csv_count > 0:
        print(f"  Risk data already seeded from CSV ({csv_count} records)")
        return

    db.query(RiskData).delete()
    db.flush()

    count = 0

    # --- Weather data ---
    weather_path = ML_DATA_DIR / "weather_data.csv"
    if weather_path.exists():
        df = pd.read_csv(weather_path)
        for _, row in df.iterrows():
            severity = None
            if pd.notna(row.get("rain")):
                severity = float(row["rain"])
            elif pd.notna(row.get("temperature")):
                severity = float(row["temperature"])

            event_data = {}
            if pd.notna(row.get("temperature")):
                event_data["temperature"] = float(row["temperature"])
            if pd.notna(row.get("rain")):
                event_data["rain"] = float(row["rain"])
            if pd.notna(row.get("weather_code")):
                event_data["weather_code"] = int(row["weather_code"])

            db.add(RiskData(
                id=uuid.uuid4(),
                product_category=ProductCategory.CROP_WEATHER,
                region=str(row["location"]) if pd.notna(row.get("location")) else None,
                event_date=date.fromisoformat(str(row["date"])),
                event_type="WEATHER_EVENT" if row.get("event_occurred", 0) == 1 else "NORMAL_DAY",
                event_severity=Decimal(str(round(severity, 2))) if severity is not None else None,
                event_data=event_data or None,
                source="ml_data/weather_data.csv",
            ))
            count += 1
    else:
        print(f"  Warning: {weather_path} not found")

    # --- Flight data ---
    flight_path = ML_DATA_DIR / "vietnam_airlines_flights.csv"
    if flight_path.exists():
        df = pd.read_csv(flight_path, encoding="utf-8-sig")
        df["arr_actual"] = pd.to_datetime(df["Arrival Time"], errors="coerce")
        df["arr_sched"] = pd.to_datetime(df["Estimated Arrival"], errors="coerce")
        df["delay_min"] = (df["arr_actual"] - df["arr_sched"]).dt.total_seconds() / 60

        for _, row in df.iterrows():
            if pd.isna(row.get("arr_actual")):
                continue
            delay = float(row["delay_min"]) if pd.notna(row.get("delay_min")) else 0.0
            db.add(RiskData(
                id=uuid.uuid4(),
                product_category=ProductCategory.FLIGHT_DELAY,
                region=str(row.get("Departure City", "Unknown")),
                event_date=row["arr_actual"].date(),
                event_type=str(row.get("Flight Status", "unknown")).upper(),
                event_severity=Decimal(str(round(max(delay, 0.0), 2))),
                event_data={
                    "airline_code": str(row.get("Airline Code", "")),
                    "flight_number": str(row.get("Flight Number", "")),
                    "departure_city": str(row.get("Departure City", "")),
                    "arrival_city": str(row.get("Arrival City", "")),
                    "delay_minutes": round(delay, 1),
                },
                source="ml_data/vietnam_airlines_flights.csv",
            ))
            count += 1
    else:
        print(f"  Warning: {flight_path} not found")

    db.flush()
    print(f"  Loaded {count} risk data records from ml_data CSV files")


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
