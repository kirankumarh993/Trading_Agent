from dataclasses import dataclass
from enum import Enum
import pandas as pd

class AgentState(Enum):
    ACTIVE = "ACTIVE"
    PAUSED_DAY_TARGET_REACHED = "PAUSED (DAILY PROFIT TARGET HIT)"
    PAUSED_DAY_LOSS_LIMIT = "PAUSED (DAILY LOSS LIMIT HIT)"
    DEAD = "DEAD (KILL-SWITCH TRIGGERED / CAPITAL DEPLETED)"

class MarketRegime(Enum):
    BULLISH_TREND = "BULLISH_TREND"
    BEARISH_TREND = "BEARISH_TREND"
    COMPRESSION_CHOP = "COMPRESSION_CHOP"
    HIGH_VOLATILITY_CRASH = "HIGH_VOLATILITY_CRASH"

@dataclass
class Position:
    symbol: str
    quantity: float
    entry_price: float
    current_price: float
    entry_time: pd.Timestamp
    stop_loss: float
    take_profit: float
    trailing_stop: float
    highest_price: float
    bars_held: int = 0
    currency_symbol: str = "₹"

    @property
    def unrealized_pnl(self) -> float:
        return (self.current_price - self.entry_price) * self.quantity

    @property
    def pnl_pct(self) -> float:
        return (self.current_price - self.entry_price) / self.entry_price * 100 if self.entry_price > 0 else 0.0

@dataclass
class TradeRecord:
    symbol: str
    side: str
    quantity: float
    entry_price: float
    exit_price: float
    pnl: float
    pnl_pct: float
    entry_time: pd.Timestamp
    exit_time: pd.Timestamp
    exit_reason: str
    strategy_used: str
    currency_symbol: str = "₹"
