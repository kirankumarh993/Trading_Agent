import logging
import datetime
import pandas as pd
from typing import Dict, Tuple, Optional
from .models import Position, AgentState
from config import MarketProfile, get_market_profile, settings
from core import NotificationService

logger = logging.getLogger("RiskAgent")

class FrictionAwareRiskAgent:
    def __init__(self, profile: MarketProfile):
        self.profile = profile
        self.initial_capital = profile.default_capital
        self.cash = profile.default_capital
        self.risk_per_trade_pct = profile.risk_per_trade_pct
        self.max_drawdown_pct = profile.max_drawdown_pct
        self.min_survival_capital = profile.default_capital * 0.05
        self.daily_profit_target = profile.daily_profit_target
        self.daily_loss_limit = profile.daily_loss_limit
        self.brokerage_per_order = profile.brokerage_per_order
        self.slippage_pct = profile.slippage_pct
        self.curr = profile.currency_symbol

        self.peak_equity = profile.default_capital
        self.state = AgentState.ACTIVE
        self.current_trading_day: Optional[datetime.date] = None
        self.day_start_equity = profile.default_capital
        self.day_halted = False
        self.day_halt_reason = ""

    def get_total_equity(self, positions: Dict[str, Position]) -> float:
        return self.cash + sum(p.current_price * p.quantity for p in positions.values())

    def update_session(self, current_time: pd.Timestamp, current_equity: float):
        day = current_time.date()
        if self.current_trading_day != day:
            self.current_trading_day = day
            self.day_start_equity = current_equity
            self.day_halted = False
            self.day_halt_reason = ""
            if self.state in [AgentState.PAUSED_DAY_TARGET_REACHED, AgentState.PAUSED_DAY_LOSS_LIMIT]:
                self.state = AgentState.ACTIVE
                logger.info(f"[{self.profile.market_id} SESSION START] Day {day} | Equity: {self.curr}{self.day_start_equity:.2f}")

    def validate_cost_to_reward_viability(self, price: float, quantity: float, take_profit: float) -> bool:
        gain = (take_profit - price) * quantity
        friction = (2 * self.brokerage_per_order) + (price * quantity * 2 * self.slippage_pct)
        if gain <= 0:
            return False
        ratio = friction / gain
        if ratio > settings.MAX_FRICTION_RATIO:
            logger.warning(f"[{self.profile.market_id} FRICTION REJECTION] Fees {self.curr}{friction:.2f} eat {ratio*100:.1f}% of reward {self.curr}{gain:.2f}.")
            return False
        return True

    def calculate_position_size(self, current_equity: float, price: float, stop_loss_price: float) -> float:
        budget = current_equity * self.risk_per_trade_pct
        risk_per_share = abs(price - stop_loss_price)
        if risk_per_share <= 0:
            return 0
        target = budget / risk_per_share
        max_afford = (self.cash * 0.90) / price

        if not self.profile.supports_fractional_shares:
            target = int(target)
            max_afford = int(max_afford)
            min_qty = max(1, int(min(2500.0, current_equity * 0.25) / price))
            return max(0, min(max(target, min_qty), max_afford))
        else:
            # Fractional shares supported (US / International)
            target = round(min(target, max_afford), 3)
            return target if target * price >= 10.0 else 0.0

    def evaluate_circuit_breakers(self, positions: Dict[str, Position], current_time: pd.Timestamp) -> Tuple[bool, bool]:
        if self.state == AgentState.DEAD:
            return False, False
        eq = self.get_total_equity(positions)
        self.update_session(current_time, eq)
        if eq > self.peak_equity:
            self.peak_equity = eq
        dd = (self.peak_equity - eq) / self.peak_equity if self.peak_equity > 0 else 1.0

        if eq <= self.min_survival_capital or dd >= self.max_drawdown_pct:
            self.state = AgentState.DEAD
            logger.critical(f"[{self.profile.market_id} TERMINAL KILL-SWITCH] Capital depleted or drawdown breached: {self.curr}{eq:.2f} (DD: {dd*100:.1f}%).")
            NotificationService.broadcast(
                title=f"{self.profile.market_id} TERMINAL KILL-SWITCH TRIGGERED",
                details=f"Current Equity: {self.curr}{eq:.2f}\nDrawdown Breached: {dd*100:.1f}%\nStatus: AGENT TERMINATED TO PROTECT REMAINING CAPITAL.",
                alert_type="KILL_SWITCH"
            )
            return False, False

        daily_pnl = eq - self.day_start_equity
        if not self.day_halted:
            if daily_pnl >= self.daily_profit_target:
                self.day_halted = True
                self.day_halt_reason = "DAILY_TARGET_REACHED"
                self.state = AgentState.PAUSED_DAY_TARGET_REACHED
                logger.info(f"[{self.profile.market_id} PROFIT LOCK] Hit target (+{self.curr}{daily_pnl:.2f}). Halting for the day.")
                NotificationService.broadcast(
                    title=f"{self.profile.market_id} DAILY PROFIT TARGET HIT (+{self.curr}{daily_pnl:.2f})",
                    details=(
                        f"Daily Target Reached: +{self.curr}{daily_pnl:.2f}\n"
                        f"Current Equity: {self.curr}{eq:.2f}\n"
                        f"Status: Trading HALTED for the day to lock in profit."
                    ),
                    alert_type="PROFIT_LOCK"
                )
                return True, False
            if daily_pnl <= -self.daily_loss_limit:
                self.day_halted = True
                self.day_halt_reason = "DAILY_LOSS_LIMIT_HIT"
                self.state = AgentState.PAUSED_DAY_LOSS_LIMIT
                logger.warning(f"[{self.profile.market_id} RISK SHIELD] Daily loss limit breached ({self.curr}{daily_pnl:.2f}). Halting for the day.")
                NotificationService.broadcast(
                    title=f"{self.profile.market_id} DAILY LOSS SHIELD TRIGGERED ({self.curr}{daily_pnl:.2f})",
                    details=(
                        f"Daily Loss Threshold Hit: {self.curr}{daily_pnl:.2f}\n"
                        f"Current Equity: {self.curr}{eq:.2f}\n"
                        f"Status: Trading HALTED for the day to preserve capital."
                    ),
                    alert_type="LOSS_SHIELD"
                )
                return True, False
        return True, not self.day_halted
