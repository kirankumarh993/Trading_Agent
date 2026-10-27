import logging
import numpy as np
import pandas as pd
from typing import Tuple, Dict

logger = logging.getLogger("SignalAgent")

class MultiFactorSignalAgent:
    def __init__(self, vol_mult: float = 1.25):
        self.vol_mult = vol_mult

    def analyze_asset(self, df: pd.DataFrame, symbol: str) -> Tuple[bool, float, Dict[str, float]]:
        if len(df) < 25:
            return False, 0.0, {}
        close = df['close']
        volume = df['volume']
        high = df['high']
        low = df['low']

        ema_20 = close.ewm(span=20, adjust=False).mean()
        ema_slope = (ema_20.iloc[-1] - ema_20.iloc[-4]) / (ema_20.iloc[-4] + 1e-9)
        trend_score = 1.0 if (close.iloc[-1] > ema_20.iloc[-1] and ema_slope > 0.0) else 0.0

        avg_vol = volume.rolling(15).mean().iloc[-2]
        vol_ratio = volume.iloc[-1] / (avg_vol + 1e-9)
        vol_score = 1.0 if vol_ratio >= self.vol_mult else (0.6 if vol_ratio >= 1.0 else 0.0)

        breakout = close.iloc[-1] >= high.iloc[-16:-1].max() * 0.999
        breakout_score = 1.0 if breakout else 0.0

        confidence = (trend_score * 0.40) + (vol_score * 0.35) + (breakout_score * 0.25)
        if confidence >= 0.65:
            entry = close.iloc[-1]
            atr = (high - low).rolling(14).mean().iloc[-1]
            if np.isnan(atr) or atr <= 0:
                atr = entry * 0.015
            return True, confidence, {
                "stop_loss": entry - (1.5 * atr),
                "take_profit": entry + (3.0 * atr),
                "atr": atr,
                "confidence": confidence,
                "volume_ratio": vol_ratio
            }
        return False, 0.0, {}
