import logging
import numpy as np
import pandas as pd
from typing import Tuple
from .models import MarketRegime

logger = logging.getLogger("MacroRegimeAgent")

class MacroRegimeAgent:
    def __init__(self, trend_window: int = 40, vol_window: int = 20):
        self.trend_window = trend_window
        self.vol_window = vol_window

    def diagnose_regime(self, benchmark_df: pd.DataFrame) -> Tuple[MarketRegime, bool]:
        if len(benchmark_df) < max(self.trend_window, self.vol_window) + 2:
            return MarketRegime.COMPRESSION_CHOP, False
        close = benchmark_df['close']
        sma_short = close.rolling(15).mean()
        sma_long = close.rolling(self.trend_window).mean()
        returns = close.pct_change().dropna()
        recent_vol = returns.tail(self.vol_window).std() * np.sqrt(252)

        if returns.iloc[-1] < -0.03 or recent_vol > 0.45:
            logger.warning("[REGIME WARNING] High volatility crash regime! Halting new buys.")
            return MarketRegime.HIGH_VOLATILITY_CRASH, False
        if close.iloc[-1] > sma_short.iloc[-1] and sma_short.iloc[-1] >= sma_long.iloc[-1] * 0.998:
            return MarketRegime.BULLISH_TREND, True
        if close.iloc[-1] < sma_short.iloc[-1] and sma_short.iloc[-1] < sma_long.iloc[-1]:
            return MarketRegime.BEARISH_TREND, False
        return MarketRegime.COMPRESSION_CHOP, False
