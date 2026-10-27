"""
Dual-Market Quantitative Simulator: Indian Equities & International Equities
"""
import numpy as np
import pandas as pd
from agents.supervisor import SupervisorTradingAgent
from agents.models import AgentState
from core.licensing import LicenseGuard
from config import MarketProfile, get_market_profile

def generate_synthetic_data(symbol: str, base_price: float = 100.0, n_bars: int = 150, regime: str = "TRENDING", seed: int = 42) -> pd.DataFrame:
    np.random.seed(seed)
    timestamps = pd.date_range("2026-01-01 09:15", periods=n_bars, freq="5min")
    if regime == "TRENDING":
        trend = np.linspace(0, 0.22, n_bars)
        noise = np.random.normal(0, 0.005, n_bars)
    elif regime == "CRASH":
        trend = np.linspace(0, -0.40, n_bars)
        noise = np.random.normal(0, 0.02, n_bars)
    else:
        trend = np.zeros(n_bars)
        noise = np.random.normal(0, 0.007, n_bars)
    returns = trend / n_bars + noise
    price = base_price * np.exp(np.cumsum(returns))
    high = price * (1 + np.abs(np.random.normal(0, 0.003, n_bars)))
    low = price * (1 - np.abs(np.random.normal(0, 0.003, n_bars)))
    opens = price * (1 + np.random.normal(0, 0.001, n_bars))
    vol = np.random.randint(8000, 45000, n_bars)
    for i in range(1, n_bars):
        if price[i] > price[i-1] * 1.008:
            vol[i] = int(vol[i] * 2.5)
    return pd.DataFrame({"open": opens, "high": high, "low": low, "close": price, "volume": vol}, index=timestamps)

def run_simulation(market: str = "INDIA", test_daily_goal: bool = False, test_crash: bool = False, enforce_license: bool = True):
    profile = get_market_profile(market)
    curr = profile.currency_symbol

    print("=" * 80)
    print(f"MULTI-AGENT QUANTITATIVE ENGINE | MARKET: {profile.name}")
    print(f"Currency: {profile.currency_code} ({curr}) | Benchmark: {profile.benchmark_symbol} | Hours: {profile.market_hours}")
    print("=" * 80)

    if enforce_license:
        guard = LicenseGuard()
        ok, msg = guard.verify_access()
        if not ok:
            print(f"\n[SECURITY LOCKOUT] {msg}\n")
            return
        print(f"[SECURITY GUARD] {msg}\n")

    if test_daily_goal:
        profile.daily_profit_target = 150.0 if profile.market_id == "INDIA" else 15.0
    if test_crash:
        profile.max_drawdown_pct = 0.05

    agent = SupervisorTradingAgent(profile=profile)
    reg_b = "CRASH" if test_crash else "TRENDING"

    if profile.market_id == "INDIA":
        df_bench = generate_synthetic_data(profile.benchmark_symbol, base_price=24000.0, n_bars=150, regime="TRENDING", seed=50)
        df_a = generate_synthetic_data("RELIANCE", base_price=2900.0, n_bars=150, regime="TRENDING", seed=77)
        df_b = generate_synthetic_data("TATAMOTORS", base_price=980.0, n_bars=150, regime=reg_b, seed=88)
        market_feed = {profile.benchmark_symbol: df_bench, "RELIANCE": df_a, "TATAMOTORS": df_b}
    elif profile.market_id == "FOREX":
        df_bench = generate_synthetic_data(profile.benchmark_symbol, base_price=83.90, n_bars=150, regime="TRENDING", seed=50)
        df_a = generate_synthetic_data("EURINR", base_price=91.10, n_bars=150, regime="TRENDING", seed=77)
        df_b = generate_synthetic_data("GBPINR", base_price=109.20, n_bars=150, regime=reg_b, seed=88)
        market_feed = {profile.benchmark_symbol: df_bench, "EURINR": df_a, "GBPINR": df_b}
    else:
        df_bench = generate_synthetic_data(profile.benchmark_symbol, base_price=550.0, n_bars=150, regime="TRENDING", seed=50)
        df_a = generate_synthetic_data("AAPL", base_price=230.0, n_bars=150, regime="TRENDING", seed=77)
        df_b = generate_synthetic_data("NVDA", base_price=135.0, n_bars=150, regime=reg_b, seed=88)
        market_feed = {profile.benchmark_symbol: df_bench, "AAPL": df_a, "NVDA": df_b}

    for bar_idx in range(40, 150):
        t = df_bench.index[bar_idx]
        cur = {sym: df.iloc[:bar_idx+1] for sym, df in market_feed.items()}
        agent.process_tick(cur, current_time=t)
        if agent.risk_agent.state == AgentState.DEAD:
            print(f">>> Terminal circuit breaker triggered at bar {bar_idx}.")
            break

    equity = agent.risk_agent.get_total_equity(agent.positions)
    print("\n" + "=" * 80)
    print(f"PERFORMANCE AUDIT: {profile.name}")
    print("=" * 80)
    print(f"Agent State           : {agent.risk_agent.state.value}")
    print(f"Initial Capital       : {curr}{profile.default_capital:,.2f}")
    print(f"Final Total Equity    : {curr}{equity:,.2f}")
    print(f"Available Cash        : {curr}{agent.risk_agent.cash:,.2f}")
    print(f"Completed Trades      : {len(agent.closed_trades)}")
    profitable = [tr for tr in agent.closed_trades if tr.pnl > 0]
    win_rate = (len(profitable) / len(agent.closed_trades) * 100) if agent.closed_trades else 0.0
    print(f"Win Rate              : {win_rate:.1f}%")
    print("=" * 80)
