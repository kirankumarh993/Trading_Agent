"""
Abstract Broker Adapter Interface for Multi-Market Routing
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional

class BaseBrokerAdapter(ABC):
    @abstractmethod
    def authenticate(self) -> bool:
        """Authenticates with broker API and generates daily session."""
        pass

    @abstractmethod
    def get_cash_balance(self) -> float:
        """Returns available unencumbered cash balance."""
        pass

    @abstractmethod
    def get_positions(self) -> Dict[str, dict]:
        """Returns map of symbol -> position details."""
        pass

    @abstractmethod
    def place_order(self, symbol: str, quantity: float, side: str, order_type: str = "MARKET", price: Optional[float] = None) -> dict:
        """Places a buy or sell order."""
        pass

    @abstractmethod
    def cancel_order(self, order_id: str) -> bool:
        """Cancels an open order."""
        pass
