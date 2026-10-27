"""
Universal Paper Trading Adapter (Works for Indian INR & International USD Equities)
"""
import logging
from typing import Dict, Optional
from .base_broker import BaseBrokerAdapter
from config.markets import MarketProfile

logger = logging.getLogger("PaperBroker")

class UniversalPaperBroker(BaseBrokerAdapter):
    def __init__(self, profile: MarketProfile):
        self.profile = profile
        self.cash = profile.default_capital
        self.positions: Dict[str, dict] = {}
        self.order_history = []

    def authenticate(self) -> bool:
        logger.info(f"[PAPER BROKER] Online for market: {self.profile.name} (Currency: {self.profile.currency_symbol})")
        return True

    def get_cash_balance(self) -> float:
        return self.cash

    def get_positions(self) -> Dict[str, dict]:
        return self.positions

    def place_order(self, symbol: str, quantity: float, side: str, order_type: str = "MARKET", price: Optional[float] = None) -> dict:
        fill_price = price or 100.0
        cost = (fill_price * quantity) + self.profile.brokerage_per_order
        if side.upper() == "BUY":
            if cost <= self.cash:
                self.cash -= cost
                self.positions[symbol] = {
                    "symbol": symbol,
                    "quantity": quantity,
                    "entry_price": fill_price
                }
                return {"status": "FILLED", "fill_price": fill_price}
        elif side.upper() == "SELL":
            if symbol in self.positions:
                pos = self.positions.pop(symbol)
                revenue = (fill_price * pos["quantity"]) - self.profile.brokerage_per_order
                self.cash += revenue
                return {"status": "FILLED", "fill_price": fill_price}
        return {"status": "REJECTED"}

    def cancel_order(self, order_id: str) -> bool:
        return True
