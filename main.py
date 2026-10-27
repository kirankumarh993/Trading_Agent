"""
Unified CLI Entrypoint for Multi-Market Quantitative Trading & F&O Derivatives System
Supports all 15 Indian Brokers (Angel, Dhan, FYERS, Upstox, Zerodha, Groww, etc.) + US Alpaca
"""
import os
import sys
import argparse
import datetime
from core.licensing import LicenseAuthority, LicenseGuard
from core.auth import BrokerFactory, StockFnoService, MultiLegStrategyService, DatabaseManager
from core import NotificationService
from simulation.market_simulator import run_simulation
from config import get_market_profile
from config.settings import CLIENT_LICENSE_FILE

SUPPORTED_BROKERS = [
    "ANGEL", "DHAN", "FYERS", "UPSTOX", "KOTAK", "MSTOCK", "ICICI",
    "5PAISA", "PAYTM", "HDFCSKY", "AXIS", "SHAREKHAN", "MOTILAL",
    "ZERODHA", "GROWW", "ALPACA"
]

def interactive_lookup_loop():
    print("=" * 80)
    print("INTERACTIVE STOCK & DERIVATIVES (F&O) LOOKUP CONSOLE")
    print("Supports Indian (NSE: RELIANCE, NIFTY, TATAMOTORS) & US (AAPL, NVDA, SPY)")
    print("Type 'exit' or 'q' to quit.")
    print("=" * 80)

    while True:
        try:
            user_input = input("\nEnter Stock Name or Symbol (e.g. RELIANCE, NIFTY, AAPL): ").strip()
            if not user_input or user_input.lower() in ["exit", "q", "quit"]:
                print("Exiting lookup console.")
                break
            StockFnoService.print_fno_dashboard(user_input)
        except (KeyboardInterrupt, EOFError):
            print("\nExiting lookup console.")
            break
        except Exception as e:
            print(f"[ERROR] Could not fetch details for '{user_input}': {e}")

def main():
    parser = argparse.ArgumentParser(description="Autonomous Quantitative Trading System (All 15 Indian Brokers + US Alpaca)")
    parser.add_argument("--market", type=str, default="INDIA", choices=["INDIA", "US", "FOREX", "CDS", "GLOBAL", "india", "us", "forex", "cds"],
                        help="Select market: 'INDIA' (NSE/BSE, INR) or 'US' (NYSE/NASDAQ, USD). Default: INDIA")
    parser.add_argument("--broker", type=str, default="ANGEL",
                        help=f"Select broker: {', '.join(SUPPORTED_BROKERS)}. Default: ANGEL")
    parser.add_argument("--quote", type=str, metavar="SYMBOL", help="Fetch spot details for entered stock")
    parser.add_argument("--fno", type=str, metavar="SYMBOL", help="Fetch complete F&O derivatives chain")
    parser.add_argument("--spread", type=str, metavar="SYMBOL", help="Construct and price automated Bull Call Spread option strategy")
    parser.add_argument("--straddle", type=str, metavar="SYMBOL", help="Construct and price 0-DTE Short Straddle option strategy")
    parser.add_argument("--journal", action="store_true", help="Display SQLite local trade journal & performance summary")
    parser.add_argument("--interactive", action="store_true", help="Launch interactive stock & F&O lookup terminal")
    parser.add_argument("--test-notify", action="store_true", help="Test Telegram and WhatsApp alert delivery")
    parser.add_argument("--auth", action="store_true", help="Run morning broker authentication for the selected broker")
    parser.add_argument("--auth-mock", action="store_true", help="Initialize offline mock session token for paper trading")
    parser.add_argument("--issue", type=str, metavar="NAME", help="ADMIN: Issue cryptographic license key for a user")
    parser.add_argument("--days", type=int, default=7, help="ADMIN: Number of days license is valid (default: 7)")
    parser.add_argument("--revoke", type=str, metavar="NAME", help="ADMIN: Revoke access for a user")
    parser.add_argument("--dashboard", action="store_true", help="ADMIN: View active licenses & accounts")
    parser.add_argument("--install", type=str, metavar="KEY", help="CLIENT: Install license key on local machine")
    parser.add_argument("--check-license", action="store_true", help="CLIENT: Verify local machine license validity")
    parser.add_argument("--test-daily-goal", action="store_true", help="Test daily profit target shutdown")
    parser.add_argument("--test-crash", action="store_true", help="Test market crash protection kill-switch")
    parser.add_argument("--no-license-check", action="store_true", help="Bypass license check for owner testing")
    args = parser.parse_args()

    auth = LicenseAuthority()
    guard = LicenseGuard()
    broker_name = args.broker.upper().strip()

    if args.test_notify:
        NotificationService.test_connection()
    elif args.interactive:
        interactive_lookup_loop()
    elif args.fno:
        StockFnoService.print_fno_dashboard(args.fno)
    elif args.spread:
        res = MultiLegStrategyService.build_bull_call_spread(args.spread)
        print("=" * 80)
        print(f"MULTI-LEG STRATEGY: {res.strategy_name.upper()}")
        print(f"Underlying: {res.underlying} | Spot: ₹{res.spot_price:,.2f}")
        print("=" * 80)
        for idx, leg in enumerate(res.legs, 1):
            print(f"Leg {idx}: {leg.action} {leg.ratio}x {leg.symbol} (Strike: ₹{leg.strike}, LTP: ₹{leg.entry_price:.2f}, Delta: {leg.delta:.2f})")
        print("-" * 80)
        print(f"Net Premium (Debit)  : ₹{abs(res.net_debit_credit):,.2f}")
        print(f"Maximum Profit       : ₹{res.max_profit:,.2f}")
        print(f"Maximum Risk / Loss  : ₹{res.max_loss:,.2f}")
        print(f"Breakeven Point(s)   : ₹{', ₹'.join(str(b) for b in res.breakeven_points)}")
        print(f"Execution Target     : {res.recommended_timeframe}")
        print("=" * 80)
    elif args.straddle:
        res = MultiLegStrategyService.build_short_straddle(args.straddle)
        print("=" * 80)
        print(f"MULTI-LEG STRATEGY: {res.strategy_name.upper()}")
        print(f"Underlying: {res.underlying} | Spot: ₹{res.spot_price:,.2f}")
        print("=" * 80)
        for idx, leg in enumerate(res.legs, 1):
            print(f"Leg {idx}: {leg.action} {leg.ratio}x {leg.symbol} (Strike: ₹{leg.strike}, Premium: ₹{leg.entry_price:.2f}, Delta: {leg.delta:.2f})")
        print("-" * 80)
        print(f"Net Premium (Credit) : ₹{res.net_debit_credit:,.2f} (Max Gain)")
        print(f"Upper Breakeven      : ₹{res.breakeven_points[1]:,.2f}")
        print(f"Lower Breakeven      : ₹{res.breakeven_points[0]:,.2f}")
        print(f"EOD Auto-Exit Rule   : Mandatory liquidation by 15:15 IST (RMS protection)")
        print("=" * 80)
    elif args.journal:
        db = DatabaseManager()
        s = db.get_trade_summary()
        open_pos = db.restore_open_positions()
        print("=" * 80)
        print("SQLITE LOCAL TRADE JOURNAL & PERSISTENT DATABASE AUDIT")
        print("=" * 80)
        print(f"Database File Location : {db.db_path}")
        print(f"Total Completed Trades : {s['total_trades']}")
        print(f"Net Realized P&L       : ₹{s['net_pnl']:,.2f}")
        print(f"Historical Win Rate    : {s['win_rate']:.1f}%")
        print(f"Active Open Positions  : {len(open_pos)}")
        if open_pos:
            print("-" * 80)
            print(f"{'Symbol':<12} {'Qty':<6} {'Entry':<10} {'Current':<10} {'SL':<10} {'Trailing SL':<12}")
            print("-" * 80)
            for p in open_pos:
                print(f"{p['symbol']:<12} {p['quantity']:<6} ₹{p['entry_price']:<9.2f} ₹{p['current_price']:<9.2f} ₹{p['stop_loss']:<9.2f} ₹{p['trailing_stop']:<11.2f}")
        print("=" * 80)
    elif args.quote:
        StockFnoService.print_stock_overview(args.quote)
    elif args.issue:
        key = auth.generate_license(args.issue, args.days)
        print("=" * 80)
        print(f"NEW LICENSE ISSUED FOR: {args.issue.upper()}")
        print(f"Days Allowed: {args.days} | Expires: {datetime.date.today() + datetime.timedelta(days=args.days)}")
        print("=" * 80)
        print(f"\n{key}\n")
        print("=" * 80)
    elif args.revoke:
        if auth.revoke_license(args.revoke):
            print(f"[REVOKED] Access revoked for user '{args.revoke}'.")
        else:
            print(f"[NOT FOUND] User '{args.revoke}' not found in registry.")
    elif args.dashboard:
        d = auth.get_dashboard_summary()
        print("=" * 80)
        print("OWNER ACCESS CONTROL & USER DASHBOARD")
        print("=" * 80)
        print(f"Total: {d['total']} | Active: {d['active']} | Expired: {d['expired']} | Revoked: {d['revoked']}")
        print("-" * 80)
        print(f"{'User':<18} {'Issued':<12} {'Expires':<12} {'Status':<10}")
        print("-" * 80)
        for u in d["users"]:
            print(f"{u['User']:<18} {u['Issued']:<12} {u['Expires']:<12} {u['Status']:<10}")
        print("=" * 80)
    elif args.install:
        with open(CLIENT_LICENSE_FILE, 'w', encoding='utf-8') as f:
            f.write(args.install.strip())
        ok, msg = guard.verify_access()
        print(f"[INSTALLED] {msg}")
    elif args.check_license:
        ok, msg = guard.verify_access()
        print(f"Status: {msg}")
    elif args.auth:
        try:
            adapter = BrokerFactory.get_adapter(broker_name)
            adapter.authenticate_live()
        except Exception as e:
            print(f"[{broker_name} AUTH ERROR] {e}")
    elif args.auth_mock:
        try:
            adapter = BrokerFactory.get_adapter(broker_name)
            adapter.create_mock_session()
        except Exception as e:
            print(f"[{broker_name} MOCK AUTH ERROR] {e}")
    else:
        run_simulation(
            market=args.market,
            test_daily_goal=args.test_daily_goal,
            test_crash=args.test_crash,
            enforce_license=not args.no_license_check
        )

if __name__ == '__main__':
    main()
