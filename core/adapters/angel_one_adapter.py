"""
Angel One SmartAPI Broker Adapter for Indian Equities (NSE/BSE)
"""
import os
import json
import logging
from typing import Dict, Optional
from .base_broker import BaseBrokerAdapter
from core.auth import AngelAuthManager

logger = logging.getLogger("AngelOneAdapter")

class AngelOneAdapter(BaseBrokerAdapter):
    def __init__(self, config_path: Optional[str] = None):
        self.auth_manager = AngelAuthManager(config_path=config_path)
        self.session_data: Optional[dict] = None

    def authenticate(self) -> bool:
        try:
            self.session_data = self.auth_manager.authenticate_live()
            return True
        except Exception as e:
            logger.warning(f"Live auth failed ({e}). Initializing simulated paper session.")
            self.session_data = self.auth_manager.create_mock_session()
            return False

    def get_cash_balance(self) -> float:
        return 10000.0

    def get_positions(self) -> Dict[str, dict]:
        return {}

    def place_order(self, symbol: str, quantity: float, side: str, order_type: str = "MARKET", price: Optional[float] = None) -> dict:
        logger.info(f"[ANGEL ONE ORDER] {side} {quantity} {symbol} ({order_type})")
        return {"order_id": f"AO_{symbol}_{side}", "status": "SUBMITTED"}

    def cancel_order(self, order_id: str) -> bool:
        return True
