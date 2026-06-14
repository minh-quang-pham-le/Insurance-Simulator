"""Shared test fixtures for unit, integration, and acceptance tests."""
import uuid
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from models.enums import (
    ClaimStatus,
    KycStatus,
    PolicyStatus,
    TriggerType,
    UserRole,
)


# ---------------------------------------------------------------------------
# Object factories (return plain MagicMock instances — no DB required)
# ---------------------------------------------------------------------------

def make_user(
    kyc_status: KycStatus = KycStatus.VERIFIED,
    role: UserRole = UserRole.USER,
    email: str = "test@example.com",
) -> MagicMock:
    user = MagicMock()
    user.id = uuid.uuid4()
    user.email = email
    user.full_name = "Test User"
    user.kyc_status = kyc_status
    user.role = role
    user.is_active = True
    return user


def make_wallet(
    user_id=None,
    balance: Decimal = Decimal("1000.00"),
) -> MagicMock:
    wallet = MagicMock()
    wallet.id = uuid.uuid4()
    wallet.user_id = user_id or uuid.uuid4()
    wallet.balance = balance
    wallet.currency = "SC"
    return wallet


def make_product(
    category: str = "FLIGHT_DELAY",
    base_payout: Decimal = Decimal("500.00"),
) -> MagicMock:
    product = MagicMock()
    product.id = uuid.uuid4()
    product.name = "Flight Delay Protection"
    product.base_payout = base_payout
    product.risk_margin = 0.25
    product.is_active = True
    product.parameters_schema = {
        "fields": [
            {
                "name": "delay_threshold_minutes",
                "type": "number",
                "default": 120,
                "min": 60,
                "max": 360,
            },
            {
                "name": "duration_days",
                "type": "number",
                "default": 3,
                "min": 1,
                "max": 7,
            },
        ]
    }
    product.trigger_conditions = {
        "type": "PARAMETRIC",
        "rules": [
            {
                "field": "delay_minutes",
                "operator": ">=",
                "threshold_param": "delay_threshold_minutes",
                "payout_multiplier": 1.0,
            },
            {
                "field": "status",
                "operator": "==",
                "value": "CANCELLED",
                "payout_multiplier": 1.5,
            },
        ],
    }
    return product


def make_weather_product() -> MagicMock:
    product = MagicMock()
    product.id = uuid.uuid4()
    product.name = "Weather Insurance"
    product.base_payout = Decimal("1000.00")
    product.risk_margin = 0.30
    product.is_active = True
    product.parameters_schema = {
        "fields": [
            {
                "name": "weather_metric",
                "type": "select",
                "options": [
                    {"value": "rainfall_mm", "label": "Rainfall (mm)"},
                    {"value": "temp_celsius", "label": "Temperature (°C)"},
                ],
            },
            {"name": "threshold", "type": "number"},
            {
                "name": "comparison",
                "type": "select",
                "options": [
                    {"value": "ABOVE", "label": "Above threshold"},
                    {"value": "BELOW", "label": "Below threshold"},
                ],
            },
        ]
    }
    product.trigger_conditions = {
        "type": "PARAMETRIC",
        "api_source": "openweathermap",
        "rules": [
            {
                "field": "{weather_metric}",
                "operator": "{comparison}",
                "threshold_param": "threshold",
                "payout_multiplier": 1.0,
            }
        ],
    }
    return product


def make_policy(
    user_id=None,
    product_id=None,
    status: PolicyStatus = PolicyStatus.ACTIVE,
    payout_amount: Decimal = Decimal("500.00"),
) -> MagicMock:
    policy = MagicMock()
    policy.id = uuid.uuid4()
    policy.user_id = user_id or uuid.uuid4()
    policy.product_id = product_id or uuid.uuid4()
    policy.status = status
    policy.payout_amount = payout_amount
    policy.premium_paid = Decimal("75.00")
    policy.end_date = datetime.now(timezone.utc) + timedelta(days=7)
    return policy


# ---------------------------------------------------------------------------
# pytest fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_db():
    """A MagicMock that looks like a SQLAlchemy Session."""
    db = MagicMock()
    db.flush.return_value = None
    db.commit.return_value = None
    db.refresh.return_value = None
    db.add.return_value = None
    db.rollback.return_value = None
    return db


@pytest.fixture
def verified_user():
    return make_user(kyc_status=KycStatus.VERIFIED)


@pytest.fixture
def unverified_user():
    return make_user(kyc_status=KycStatus.NOT_SUBMITTED)


@pytest.fixture
def flight_product():
    return make_product()


@pytest.fixture
def weather_product():
    return make_weather_product()
