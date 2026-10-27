"""
Global System Configuration, Licensing Parameters & Multi-Market Profiles
Supports both Indian Equities (NSE/BSE) and International Equities (US NYSE/NASDAQ)
"""
import os
from dataclasses import dataclass, field
from typing import List, Dict

MASTER_SECRET_KEY = os.getenv("APP_MASTER_SECRET", "MY_SUPER_SECURE_CREATOR_KEY_2026")
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTRY_FILE = os.path.join(ROOT_DIR, "license_registry.json")
CLIENT_LICENSE_FILE = os.path.join(ROOT_DIR, "license.key")
SESSION_FILE = os.path.join(ROOT_DIR, "session_token.json")

# Friction & Position Invalidation Defaults
MAX_FRICTION_RATIO = 0.35
TRAILING_STOP_PCT = 0.015
MAX_STAGNATION_BARS = 15
VOLUME_SURGE_MULTIPLIER = 1.25
MIN_SIGNAL_CONFIDENCE = 0.65

@dataclass
class MarketProfile:
    market_id: str                      # "INDIA" or "US"
    name: str                           # Display name
    currency_symbol: str                # "₹" or "$"
    currency_code: str                  # "INR" or "USD"
    benchmark_symbol: str               # "NIFTY_50" or "SPY"
    timezone: str                       # "Asia/Kolkata" or "America/New_York"
    market_hours: str                   # "09:15 - 15:30 IST" or "09:30 - 16:00 EST"
    default_capital: float              # 10,000 INR or 1,000 USD
    risk_per_trade_pct: float           # 2.5%
    max_drawdown_pct: float             # 25%
    daily_profit_target: float          # 1,000 INR or 100 USD
    daily_loss_limit: float             # 300 INR or 30 USD
    brokerage_per_order: float          # 10.0 INR (flat discount) or 0.0 USD (commission-free)
    slippage_pct: float                 # 0.0005 (India) or 0.0002 (US large caps)
    supports_fractional_shares: bool    # False (India) or True (US)
    default_watchlist: List[str] = field(default_factory=list)

MARKET_PROFILES: Dict[str, MarketProfile] = {
    "INDIA": MarketProfile(
        market_id="INDIA",
        name="Indian Equities (NSE/BSE)",
        currency_symbol="₹",
        currency_code="INR",
        benchmark_symbol="NIFTY_50",
        timezone="Asia/Kolkata",
        market_hours="09:15 - 15:30 IST",
        default_capital=10000.0,
        risk_per_trade_pct=0.025,
        max_drawdown_pct=0.25,
        daily_profit_target=1000.0,
        daily_loss_limit=300.0,
        brokerage_per_order=10.0,
        slippage_pct=0.0005,
        supports_fractional_shares=False,
        default_watchlist=["RELIANCE", "TCS", "INFY", "TATAMOTORS"]
    ),

    "FOREX": MarketProfile(
        market_id="FOREX",
        name="Exchange-Traded Currency Derivatives (NSE CDS)",
        currency_symbol="₹",
        currency_code="INR",
        benchmark_symbol="USDINR",
        timezone="Asia/Kolkata",
        market_hours="09:00 - 17:00 IST",
        default_capital=10000.0,
        risk_per_trade_pct=0.02,
        max_drawdown_pct=0.20,
        daily_profit_target=800.0,
        daily_loss_limit=250.0,
        brokerage_per_order=10.0,
        slippage_pct=0.0002,
        supports_fractional_shares=False,
        default_watchlist=["USDINR", "EURINR", "GBPINR", "JPYINR", "EURUSD"]
    ),
    "US": MarketProfile(
        market_id="US",
        name="International Equities (US NYSE/NASDAQ)",
        currency_symbol="$",
        currency_code="USD",
        benchmark_symbol="SPY",
        timezone="America/New_York",
        market_hours="09:30 - 16:00 EST (19:00 - 01:30 IST)",
        default_capital=1000.0,
        risk_per_trade_pct=0.025,
        max_drawdown_pct=0.25,
        daily_profit_target=100.0,
        daily_loss_limit=30.0,
        brokerage_per_order=0.0,
        slippage_pct=0.0002,
        supports_fractional_shares=True,
        default_watchlist=["AAPL", "NVDA", "MSFT", "TSLA"]
    )
}

def get_market_profile(market_id: str) -> MarketProfile:
    key = market_id.upper().strip()
    if key in ["IN", "INDIA", "NSE", "BSE"]:
        return MARKET_PROFILES["INDIA"]
    elif key in ["FOREX", "CDS", "CURRENCY", "FX"]:
        return MARKET_PROFILES["FOREX"]
    elif key in ["US", "USA", "INTERNATIONAL", "GLOBAL", "NASDAQ", "NYSE"]:
        return MARKET_PROFILES["US"]
    else:
        raise ValueError(f"Unknown market '{market_id}'. Supported markets: 'INDIA', 'US'.")
