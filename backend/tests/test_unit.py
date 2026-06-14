"""
UNIT TESTS — AI-Powered Insurance Simulator
============================================

Mức UNIT: kiểm thử MỘT thành phần ở trạng thái cô lập, KHÔNG dùng database,
KHÔNG gọi HTTP. Logic nghiệp vụ thuần tuý được xác minh trực tiếp.

Phạm vi:
  * AuthService.hash_password / verify_password  (băm mật khẩu — SDD 6.2)
  * simulation_engine.check_trigger              (đánh giá điều kiện kích hoạt — SDD 6.7)

Cách chạy (đứng ở thư mục backend/):
    python -m pytest test_unit.py -v
"""
# --- Bootstrap: làm cho việc import an toàn mà không cần PostgreSQL/psycopg2 ---
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # đảm bảo import được package backend
os.environ.setdefault("DATABASE_URL", "sqlite://")  # engine ở config.database dùng SQLite khi test
os.environ.setdefault("DEBUG", "False")

from decimal import Decimal
from types import SimpleNamespace

import pytest

from services.auth_service import AuthService
from services import simulation_engine


# ---------------------------------------------------------------------------
# 1) Băm mật khẩu (SDD 6.2 — không bao giờ lưu mật khẩu thô)
# ---------------------------------------------------------------------------

class TestPasswordHashing:
    def test_hash_is_not_plaintext(self):
        hashed = AuthService.hash_password("Passw0rd!")
        assert hashed != "Passw0rd!"
        assert hashed.startswith("$2")  # dấu hiệu của bcrypt

    def test_verify_accepts_correct_password(self):
        hashed = AuthService.hash_password("Passw0rd!")
        assert AuthService.verify_password("Passw0rd!", hashed) is True

    def test_verify_rejects_wrong_password(self):
        hashed = AuthService.hash_password("Passw0rd!")
        assert AuthService.verify_password("WrongPass1!", hashed) is False

    def test_same_password_produces_different_hashes(self):
        """bcrypt thêm salt ngẫu nhiên nên hai lần băm phải khác nhau."""
        assert AuthService.hash_password("Passw0rd!") != AuthService.hash_password("Passw0rd!")


# ---------------------------------------------------------------------------
# 2) Đánh giá điều kiện kích hoạt (SDD 6.7)
#    Dùng đối tượng "product" giả lập (SimpleNamespace) — không chạm DB.
# ---------------------------------------------------------------------------

def _flight_product():
    """Sản phẩm trễ chuyến: kích hoạt khi delay_minutes >= delay_threshold_minutes."""
    return SimpleNamespace(
        id="00000000-0000-0000-0000-000000000001",
        name="Flight Delay Protection",
        base_payout=Decimal("500.00"),
        parameters_schema={
            "fields": [
                {"name": "delay_threshold_minutes", "type": "number", "default": 120}
            ]
        },
        trigger_conditions={
            "type": "PARAMETRIC",
            "rules": [
                {
                    "field": "delay_minutes",
                    "operator": ">=",
                    "threshold_param": "delay_threshold_minutes",
                    "payout_multiplier": 1.0,
                }
            ],
        },
    )


class TestCheckTrigger:
    def test_value_above_threshold_triggers_full_payout(self):
        result = simulation_engine.check_trigger(
            _flight_product(), {"delay_minutes": 180}
        )
        assert result["triggered"] is True
        assert result["payout_amount"] == 500.0
        assert result["payout_multiplier"] == 1.0

    def test_value_below_threshold_does_not_trigger(self):
        result = simulation_engine.check_trigger(
            _flight_product(), {"delay_minutes": 60}
        )
        assert result["triggered"] is False
        assert result["payout_amount"] == 0.0

    def test_value_equal_to_threshold_triggers(self):
        """Toán tử '>=' nên kích hoạt đúng tại ngưỡng (biên)."""
        result = simulation_engine.check_trigger(
            _flight_product(), {"delay_minutes": 120}
        )
        assert result["triggered"] is True

    def test_missing_field_is_safe(self):
        """Thiếu tham số đầu vào thì không kích hoạt (không lỗi)."""
        result = simulation_engine.check_trigger(_flight_product(), {})
        assert result["triggered"] is False
