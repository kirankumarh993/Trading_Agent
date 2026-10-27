import logging
import pandas as pd
from typing import Dict, List, Optional
from .models import Position, TradeRecord, AgentState
from .macro_regime import MacroRegimeAgent
from .signal_generator import MultiFactorSignalAgent
from .risk_governor import FrictionAwareRiskAgent
from .position_audit import PositionAuditAgent
from config import MarketProfile, get_market_profile
from core import NotificationService, DatabaseManager

logger = logging.getLogger("SupervisorAgent")

class SupervisorTradingAgent:
    def __init__(self, profile: MarketProfile, broker_name: str = "ANGEL"):
        self.profile = profile
        self.broker_name = broker_name.upper()
        self.curr = profile.currency_symbol
        self.macro_agent = MacroRegimeAgent()
        self.signal_agent = MultiFactorSignalAgent()
        self.risk_agent = FrictionAwareRiskAgent(profile=profile)
        self.position_agent = PositionAuditAgent()
        self.db = DatabaseManager()
        self.positions: Dict[str, Position] = {}
        self.closed_trades: List[TradeRecord] = []
        self._restore_positions_from_db()

    def _restore_positions_from_db(self):
        saved = self.db.restore_open_positions()
        for p in saved:
            if p["market"] == self.profile.market_id:
                self.positions[p["symbol"]] = Position(
                    symbol=p["symbol"], quantity=p["quantity"], entry_price=p["entry_price"],
                    current_price=p["current_price"], entry_time=pd.Timestamp(p["entry_time"]),
                    stop_loss=p["stop_loss"], take_profit=p["take_profit"],
                    trailing_stop=p["trailing_stop"], highest_price=p["highest_price"],
                    currency_symbol=self.curr
                )
        if self.positions:
            logger.info(f"[CRASH RECOVERY] Restored {len(self.positions)} active positions from SQLite database.")

    def execute_buy(self, symbol: str, price: float, metadata: Dict[str, float], timestamp: pd.Timestamp):
        exec_price = price * (1.0 + self.risk_agent.slippage_pct)
        stop_loss = metadata["stop_loss"]
        take_profit = metadata["take_profit"]
        eq = self.risk_agent.get_total_equity(self.positions)
        qty = self.risk_agent.calculate_position_size(eq, exec_price, stop_loss)
        if qty <= 0 or not self.risk_agent.validate_cost_to_reward_viability(exec_price, qty, take_profit):
            return
        cost = (exec_price * qty) + self.risk_agent.brokerage_per_order
        if cost > self.risk_agent.cash:
            return
        self.risk_agent.cash -= cost
        pos = Position(
            symbol=symbol, quantity=qty, entry_price=exec_price, current_price=exec_price,
            entry_time=timestamp, stop_loss=stop_loss, take_profit=take_profit,
            trailing_stop=stop_loss, highest_price=exec_price, currency_symbol=self.curr
        )
        self.positions[symbol] = pos
        # Save to SQLite Database
        self.db.save_position(
            symbol=symbol, quantity=qty, entry_price=exec_price, stop_loss=stop_loss,
            take_profit=take_profit, trailing_stop=stop_loss, highest_price=exec_price,
            entry_time=str(timestamp), market=self.profile.market_id, broker=self.broker_name
        )
        logger.info(
            f"[{self.profile.market_id} BUY] {symbol} | Qty: {qty} @ {self.curr}{exec_price:.2f} | "
            f"SL: {self.curr}{stop_loss:.2f} | TP: {self.curr}{take_profit:.2f} | Cash: {self.curr}{self.risk_agent.cash:.2f}"
        )
        # Instant Mobile Alert
        NotificationService.broadcast(
            title=f"{self.profile.market_id} BUY: {symbol}",
            details=(
                f"Asset: {symbol}\n"
                f"Action: BUY (Long Entry)\n"
                f"Quantity: {qty}\n"
                f"Price: {self.curr}{exec_price:.2f}\n"
                f"Target (TP): {self.curr}{take_profit:.2f}\n"
                f"Stop Loss (SL): {self.curr}{stop_loss:.2f}\n"
                f"Confidence: {metadata.get('confidence', 0.7)*100:.0f}%\n"
                f"Free Cash: {self.curr}{self.risk_agent.cash:.2f}"
            ),
            alert_type="BUY"
        )

    def execute_sell(self, symbol: str, price: float, reason: str, timestamp: pd.Timestamp):
        if symbol not in self.positions:
            return
        pos = self.positions.pop(symbol)
        exec_price = price * (1.0 - self.risk_agent.slippage_pct)
        rev = (exec_price * pos.quantity) - self.risk_agent.brokerage_per_order
        self.risk_agent.cash += rev
        pnl = (exec_price - pos.entry_price) * pos.quantity - (2 * self.risk_agent.brokerage_per_order)
        pnl_pct = (exec_price - pos.entry_price) / pos.entry_price * 100
        self.closed_trades.append(TradeRecord(
            symbol=symbol, side="SELL", quantity=pos.quantity, entry_price=pos.entry_price,
            exit_price=exec_price, pnl=pnl, pnl_pct=pnl_pct, entry_time=pos.entry_time,
            exit_time=timestamp, exit_reason=reason, strategy_used="MultiFactor_Composite",
            currency_symbol=self.curr
        ))
        # Update SQLite Database
        self.db.remove_position(symbol)
        self.db.record_closed_trade(
            symbol=symbol, side="SELL", quantity=pos.quantity, entry_price=pos.entry_price,
            exit_price=exec_price, pnl=pnl, pnl_pct=pnl_pct, entry_time=str(pos.entry_time),
            exit_time=str(timestamp), exit_reason=reason, market=self.profile.market_id, broker=self.broker_name
        )
        log_fn = logger.info if pnl >= 0 else logger.warning
        log_fn(
            f"[{self.profile.market_id} SELL] {symbol} | Qty: {pos.quantity} @ {self.curr}{exec_price:.2f} | "
            f"P&L: {self.curr}{pnl:+.2f} ({pnl_pct:+.2f}%) | Reason: {reason} | Cash: {self.curr}{self.risk_agent.cash:.2f}"
        )
        # Instant Mobile Alert
        NotificationService.broadcast(
            title=f"{self.profile.market_id} SELL: {symbol}",
            details=(
                f"Asset: {symbol}\n"
                f"Action: SELL (Position Closed)\n"
                f"Quantity: {pos.quantity}\n"
                f"Exit Price: {self.curr}{exec_price:.2f}\n"
                f"Realized P&L: {self.curr}{pnl:+.2f} ({pnl_pct:+.2f}%)\n"
                f"Exit Reason: {reason}\n"
                f"Updated Cash: {self.curr}{self.risk_agent.cash:.2f}"
            ),
            alert_type="SELL"
        )

    def process_tick(self, market_data: Dict[str, pd.DataFrame], current_time: pd.Timestamp):
        is_alive, can_trade = self.risk_agent.evaluate_circuit_breakers(self.positions, current_time)
        if not is_alive:
            for sym, pos in list(self.positions.items()):
                self.execute_sell(sym, pos.current_price, "CIRCUIT_BREAKER_KILLSWITCH", current_time)
            return

        current_prices = {sym: df['close'].iloc[-1] for sym, df in market_data.items() if len(df) > 0}
        exits = self.position_agent.inspect_positions(self.positions, current_prices, current_time)
        for sym, reason in exits:
            self.execute_sell(sym, current_prices[sym], reason, current_time)

        if self.risk_agent.day_halted and self.positions:
            for sym, pos in list(self.positions.items()):
                self.execute_sell(sym, current_prices[sym], f"SESSION_HALT_{self.risk_agent.day_halt_reason}", current_time)
            return

        if not can_trade:
            return

        bm_df = market_data.get(self.profile.benchmark_symbol)
        if bm_df is None or len(bm_df) < 15:
            return

        regime, allow_longs = self.macro_agent.diagnose_regime(bm_df)
        if not allow_longs:
            return

        for sym, df in market_data.items():
            if sym != self.profile.benchmark_symbol and sym not in self.positions:
                sig, conf, meta = self.signal_agent.analyze_asset(df, sym)
                if sig:
                    self.execute_buy(sym, current_prices[sym], meta, current_time)
