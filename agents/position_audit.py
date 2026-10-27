import logging
import pandas as pd
from typing import Dict, List, Tuple
from .models import Position
from config import settings

logger = logging.getLogger("PositionAuditAgent")

class PositionAuditAgent:
    def __init__(self, trailing_stop_pct: float = settings.TRAILING_STOP_PCT, max_stagnation_bars: int = settings.MAX_STAGNATION_BARS):
        self.trailing_stop_pct = trailing_stop_pct
        self.max_stagnation_bars = max_stagnation_bars

    def inspect_positions(self, positions: Dict[str, Position], current_prices: Dict[str, float], timestamp: pd.Timestamp) -> List[Tuple[str, str]]:
        exits = []
        
        # Hard Rule 0: 3:15 PM IST Auto Square-Off for Intraday MIS
        # Prevents broker penalty charges (RMS auto-square-off fees of ₹50 + GST)
        if hasattr(timestamp, 'hour') and (timestamp.hour > 15 or (timestamp.hour == 15 and timestamp.minute >= 15)):
            for symbol in list(positions.keys()):
                exits.append((symbol, "INTRADAY_EOD_SQUAREOFF_315PM (Auto-exit before RMS penalty)"))
            return exits

        for symbol, pos in list(positions.items()):
            p = current_prices.get(symbol, pos.current_price)
            pos.current_price = p
            pos.bars_held += 1

            if p > pos.highest_price:
                pos.highest_price = p
                new_trail = p * (1.0 - self.trailing_stop_pct)
                if new_trail > pos.trailing_stop:
                    pos.trailing_stop = new_trail

            if p <= pos.stop_loss:
                exits.append((symbol, f"HARD_STOP ({p:.2f} <= {pos.stop_loss:.2f})"))
                continue
            if p <= pos.trailing_stop and pos.highest_price >= pos.entry_price * 1.02:
                exits.append((symbol, f"TRAILING_STOP_LOCK ({p:.2f} <= {pos.trailing_stop:.2f})"))
                continue
            if p >= pos.take_profit:
                exits.append((symbol, f"TAKE_PROFIT ({p:.2f} >= {pos.take_profit:.2f})"))
                continue
            if pos.bars_held >= self.max_stagnation_bars and pos.unrealized_pnl <= 0:
                exits.append((symbol, f"THESIS_INVALIDATION (Held {pos.bars_held} bars without momentum)"))
                continue
        return exits
