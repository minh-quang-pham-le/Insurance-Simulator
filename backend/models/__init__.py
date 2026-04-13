# Import all models here so Alembic can discover them for auto-migrations.

from models.user import User
from models.wallet import Wallet, WalletTransaction
from models.insurance_product import InsuranceProduct
from models.policy import Policy
from models.claim import Claim
from models.risk_data import RiskData
from models.notification import Notification
from models.chat_session import ChatSession
from models.simulation_session import SimulationSession
from models.api_monitor_log import ApiMonitorLog

__all__ = [
    "User",
    "Wallet",
    "WalletTransaction",
    "InsuranceProduct",
    "Policy",
    "Claim",
    "RiskData",
    "Notification",
    "ChatSession",
    "SimulationSession",
    "ApiMonitorLog",
]
