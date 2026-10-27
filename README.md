# Autonomous Multi-Market Quantitative Trading System (Equities & F&O)

An enterprise-grade, modular quantitative trading system engineered to operate across both **Indian Equities & Derivatives (NSE/BSE & NFO)** and **International Equities & Options (US NYSE/NASDAQ)**. Features dynamic stock detail inspection, complete Futures & Options (F&O) contract chains, Black-Scholes Greeks, SEBI-compliant morning authentication, dual Telegram & WhatsApp mobile notifications, and cryptographic licensing governance.

---

## 1. Supported Markets & Asset Classes

| Feature | Indian Market (NSE / BSE / NFO) | International Market (NYSE / NASDAQ) |
| :--- | :--- | :--- |
| **Market Code** | `--market INDIA` | `--market US` |
| **Account Currency** | Indian Rupee (**INR / ₹**) | US Dollar (**USD / $**) |
| **Asset Classes** | **Cash Equities** + **Futures & Options (F&O)** | **Equities** + **Equity Options** |
| **F&O Lot Sizes** | Stock-specific (e.g., RELIANCE: 250, NIFTY: 25) | 100 shares per contract standard |
| **Macro Benchmark** | **NIFTY 50** (`NIFTY_50` / `^NSEI`) | **S&P 500** (`SPY` / `^GSPC`) |
| **Trading Window** | 09:15 – 15:30 IST (UTC+5:30) | 09:30 – 16:00 EST (19:00 – 01:30 IST) |
| **Capital Baseline** | ₹10,000 (₹1,000 profit lock / -₹300 shield) | $1,000 ($100 profit lock / -$30 shield) |
| **Derivatives Pricing** | Black-Scholes Greeks (Delta, Theta, Gamma, IV) | Black-Scholes Greeks (Delta, Theta, Gamma, IV) |
| **Broker API** | **Angel One SmartAPI** (100% free tier) | **Alpaca Markets** (100% free paper & live tier) |
| **Mobile Alerts** | **Telegram Bot** + **WhatsApp (CallMeBot)** | **Telegram Bot** + **WhatsApp (CallMeBot)** |

---

## 2. Real-Time Telegram & WhatsApp Mobile Alerts

The system includes a dual mobile notification engine (`NotificationService`) that instantly broadcasts alerts to your phone whenever:
* 🚀 An order is entered (`BUY` with LTP, quantity, stop-loss, and target).
* 💰 A position is exited (`SELL` with realized P&L and win/loss reason).
* 🎯 Daily Profit Lock is reached (+₹1,000 / +$100 shutdown).
* 🛡️ Daily Loss Shield is triggered (-₹300 / -$30 shutdown).
* 🚨 Terminal Circuit Breaker kill-switch is hit.

### Setting Up Free Telegram Alerts (2 Minutes)
1. Open Telegram, search for `@BotFather`, and send `/newbot`.
2. Follow the prompt to name your bot and copy your `HTTP API Token` (`bot_token`).
3. Search for `@userinfobot` in Telegram, click Start, and copy your `Id` (`chat_id`).
4. Send any test message to your newly created bot so it has permission to chat with you.

### Setting Up Free WhatsApp Alerts (CallMeBot Gateway)
1. Save the CallMeBot phone number to your phone contacts: `+34 911 06 14 30` (or check [callmebot.com](https://www.callmebot.com/blog/free-api-whatsapp-messages/)).
2. Send this exact message to CallMeBot on WhatsApp: `"I allow callmebot to send me messages"`.
3. CallMeBot will reply with your personal `apikey`.

### Activating Notifications in the Bot
1. Copy `config/notify_config.template.json` to `config/notify_config.json`:
   ```bash
   cp config/notify_config.template.json config/notify_config.json
   ```
2. Open `config/notify_config.json`, set `"enabled": true`, and enter your tokens:
   ```json
   {
     "enabled": true,
     "telegram": {
       "bot_token": "123456789:ABCdefGHIjklMNOpqrSTUvwxYZ",
       "chat_id": "987654321"
     },
     "whatsapp": {
       "phone": "+919876543210",
       "apikey": "123456"
     }
   }
   ```
3. Test your connection:
   ```bash
   python main.py --test-notify
   ```
   Both Telegram and WhatsApp will instantly receive a test alert.

---

## 3. Stock Lookup & F&O Derivatives Features

### 1. Spot Stock Detail Lookup (`--quote <SYMBOL>`)
Fetch real-time/simulated metrics for any entered stock name or ticker:
```bash
python main.py --quote RELIANCE
python main.py --quote AAPL
```
* **Output Details**: Last Traded Price (LTP), Day Low / High range, Previous Close, Open, 52-Week Range, Daily Volume, 14-period ATR Volatility, Market Cap Tier, and F&O Eligibility status.

### 2. Complete F&O Contract & Option Chain Lookup (`--fno <SYMBOL>`)
Inspect active Futures contracts and multi-strike Option Chains with Greeks:
```bash
python main.py --fno RELIANCE
python main.py --fno NIFTY
python main.py --fno AAPL
```
* **Futures Contract**: Active monthly contract code, Futures LTP, Basis (Premium/Discount), Lot Size, Total Contract Value, and Margin Requirement (~20% NSE).
* **Option Chain**: Strike table displaying ATM (At-The-Money), ITM, and OTM strikes with:
  * Call (CE) & Put (PE) Last Traded Price (LTP)
  * Option Greeks: Delta and Theta (daily time decay)
  * Open Interest (OI) per strike
  * Put-Call Ratio (PCR) and estimated Max Pain

### 3. Interactive Lookup Terminal (`--interactive`)
Launch a continuous terminal prompt where you can type any stock symbol anytime:
```bash
python main.py --interactive
```

---

## 4. Quick Setup Guide

### Option A: Visual Studio Code (VS Code)

1. **Open the Project**:
   - In VS Code, click **File** > **Open Folder...** and select the unzipped `trading_agent` directory.
2. **Create and Activate Virtual Environment**:
   - Open terminal (`Ctrl + ~` or **Terminal** > **New Terminal**):
     - **Windows (PowerShell)**:
       ```powershell
       python -m venv venv
       .\\venv\\Scripts\\Activate.ps1
       ```
     - **Windows (CMD)**:
       ```cmd
       python -m venv venv
       .\\venv\\Scripts\\activate.bat
       ```
     - **macOS / Linux**:
       ```bash
       python3 -m venv venv
       source venv/bin/activate
       ```
3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Configure Credentials**:
   - **Broker Config (India)**: Copy `config/angel_config.template.json` to `config/angel_config.json`.
   - **Broker Config (US)**: Copy `config/alpaca_config.template.json` to `config/alpaca_config.json`.
   - **Notifications Config**: Copy `config/notify_config.template.json` to `config/notify_config.json`.
5. **1-Click Run & Debug**:
   - Press `Ctrl + Shift + D` (or `Cmd + Shift + D` on macOS).
   - Select any pre-configured target and press **F5**:
     - `1. Indian Equities Paper Trading (NSE/BSE - ₹)`
     - `2. US / Global Equities Paper Trading (NYSE/NASDAQ - $)`
     - `3. F&O Option Chain & Futures Lookup (NSE: RELIANCE)`
     - `4. F&O Option Chain Lookup (US: AAPL)`
     - `5. Interactive Stock & F&O Console`
     - `6. Test Telegram & WhatsApp Alerts`
     - `7. Angel One India Morning Auth`
     - `8. Alpaca US Market Auth Check`
     - `9. Admin License Dashboard`

---

### Option B: IntelliJ IDEA / PyCharm

1. **Open the Project**:
   - In IntelliJ IDEA / PyCharm, click **Open** and select the `trading_agent` directory.
2. **Configure Python SDK**:
   - Go to **File** > **Project Structure...** (`Ctrl + Alt + Shift + S` or `Cmd + ;` on macOS).
   - Under **Platform Settings**, click **SDKs** > **+** > **Add Python SDK...**
   - Select **Virtualenv Environment** > **New environment** (Python 3.9+) and click **OK**.
3. **Mark Sources Root**:
   - In the Project view on the left, right-click the root folder `trading_agent`.
   - Select **Mark Directory as** > **Sources Root**.
4. **Install Dependencies**:
   - Open the **Terminal** tab (`Alt + F12`) and run: `pip install -r requirements.txt`.
5. **Run Configurations**:
   - Right-click `main.py` and select **Run 'main'**.
   - To query a stock: Click the configuration dropdown > **Edit Configurations...** > add `--fno RELIANCE` or `--test-notify` to **Script parameters**.

---

## 5. Command-Line Execution Cheatsheet

```bash
# ==========================================
# 1. MOBILE ALERTS & NOTIFICATIONS
# ==========================================
# Test Telegram & WhatsApp connection:
python main.py --test-notify

# ==========================================
# 2. STOCK DETAILS & F&O LOOKUP
# ==========================================
# Fetch spot stock details:
python main.py --quote RELIANCE
python main.py --quote AAPL

# Fetch Futures & Option Chain with Greeks:
python main.py --fno RELIANCE
python main.py --fno NIFTY
python main.py --fno AAPL

# Launch interactive stock & F&O console:
python main.py --interactive

# ==========================================
# 3. MULTI-MARKET TRADING AGENT
# ==========================================
# Run Indian Equities (NSE/BSE) paper trading:
python main.py --market INDIA

# Run US / Global Equities paper trading:
python main.py --market US

# Perform morning Angel One SEBI authentication:
python main.py --market INDIA --auth

# ==========================================
# 4. LICENSING & USER ADMINISTRATION
# ==========================================
# Issue a 7-day trial license for a client:
python main.py --issue "FriendName" --days 7

# Inspect active licenses dashboard:
python main.py --dashboard

# Revoke a user's access instantly:
python main.py --revoke "FriendName"
```


## Groww Trading API Configuration (`config/groww_config.json`)

The system natively supports the official **Groww Trading API** (`https://api.groww.in/v1`) for both Equity (`CASH`) and Derivatives (`FNO`) across NSE and BSE.

### 1. Copy the Configuration Template
Copy `config/groww_config.template.json` to `config/groww_config.json`:

```json
{
  "auth_mode": "totp",
  "access_token": "YOUR_DAILY_ACCESS_TOKEN_IF_USING_TOKEN_MODE",
  "api_key": "YOUR_GROWW_API_KEY_OR_TOTP_TOKEN",
  "api_secret": "YOUR_GROWW_API_SECRET",
  "totp_secret": "YOUR_GROWW_BASE32_TOTP_SECRET"
}
```

### 2. Choose Your Authentication Flow (`auth_mode`)
Groww supports three authentication methods on the [Groww Cloud API Keys Portal](https://groww.in/trade-api/docs/curl):
1. **`"totp"` (Recommended Zero-Touch Flow)**:
   - On the Groww API Keys page, click **Generate API Key dropdown -> Generate TOTP token**.
   - Paste the generated token into `"api_key"` and the Base32 QR secret into `"totp_secret"`.
   - Our built-in `PureTOTP` engine automatically computes the 6-digit TOTP and exchanges it at `POST https://api.groww.in/v1/token/api/access`.
2. **`"approval"` (API Key + SHA-256 Secret Checksum Flow)**:
   - On the Groww API Keys page, click **Generate API key** and copy your **API Key** and **Secret**.
   - Paste them into `"api_key"` and `"api_secret"`. The bot automatically computes `SHA256(secret + epoch_timestamp)` and exchanges it for a daily Bearer token.
3. **`"access_token"` (Direct Daily Bearer Token)**:
   - In your Groww account -> **Settings -> Trading APIs -> Generate API keys -> Access Token**.
   - Paste the daily token into `"access_token"` (expires daily at 6:00 AM IST).

### 3. Authenticate & Run with Groww
```bash
# Authenticate live with Groww
python main.py --broker GROWW --auth

# Or initialize a mock Groww session for offline paper trading
python main.py --broker GROWW --auth-mock

# Run the trading bot with Groww
python main.py --market INDIA --broker GROWW
```


---

# Multi-Broker Architecture & Configuration Guide (All 15 Brokers)

The trading bot features a modular **Unified Broker Abstraction Layer (`BrokerInterface`)**. Any of the 15 Indian brokers can be selected on demand using the `--broker` flag. All trading algorithms, macro regime filters, Black-Scholes Greeks, trailing stops, circuit breakers, and Telegram/WhatsApp notifications remain completely identical regardless of which broker executes the trade.

---

## 1. Broker Master Matrix (Free vs. Paid & Authentication)

| Broker | CLI Flag | Config File | API Cost | Auth Mode | Segment Support |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Angel One** | `--broker ANGEL` | `config/angel_config.json` | **₹0 Free** | TOTP + PIN + API Key | Cash + F&O |
| **Dhan** | `--broker DHAN` | `config/dhan_config.json` | **₹0 Free** | Permanent Access Token | Cash + F&O |
| **FYERS** | `--broker FYERS` | `config/fyers_config.json` | **₹0 Free** | TOTP + App ID + PIN | Cash + F&O |
| **Upstox** | `--broker UPSTOX` | `config/upstox_config.json` | **₹0 Free** | OAuth 2.0 / Morning Token | Cash + F&O |
| **Kotak Neo** | `--broker KOTAK` | `config/kotak_config.json` | **₹0 Free** | Consumer Key + Mobile TOTP | Cash + F&O |
| **m.Stock** | `--broker MSTOCK` | `config/mstock_config.json` | **₹0 Free** | API Key + Secret | Cash + F&O |
| **ICICI Direct** | `--broker ICICI` | `config/icici_config.json` | **₹0 Free** | Breeze Session Key + API Key | Cash + F&O |
| **5paisa** | `--broker 5PAISA` | `config/5paisa_config.json` | **₹0 Free** | User Key + Encryption Key + TOTP | Cash + F&O |
| **Paytm Money** | `--broker PAYTM` | `config/paytm_config.json` | **₹0 Free** | API Key + API Secret + Request Token | Cash + F&O |
| **HDFC Sky** | `--broker HDFCSKY` | `config/hdfcsky_config.json` | **₹0 Free** | API Key + Access Token | Cash + F&O |
| **AxisDirect** | `--broker AXIS` | `config/axis_config.json` | **₹0 Free** | RapidAPI Key + Token | Cash + F&O |
| **Sharekhan** | `--broker SHAREKHAN` | `config/sharekhan_config.json` | **₹0 Free** | Customer ID + API Key + Token | Cash + F&O |
| **Motilal Oswal** | `--broker MOTILAL` | `config/motilal_config.json` | **₹0 Free** | User ID + API Key + Password | Cash + F&O |
| **Zerodha** | `--broker ZERODHA` | `config/zerodha_config.json` | **₹500 / mo** *(Free if ≥ ₹2k brokerage)* | API Key + Secret + Morning Token | Cash + F&O |
| **Groww** | `--broker GROWW` | `config/groww_config.json` | **₹499 + GST / mo** | TOTP Token / API Key + Checksum | Cash + F&O |

---

## 2. Configuration Setup for Each Broker

### 1. Angel One SmartAPI (100% Free)
* **Portal**: [smartapi.angelbroking.com](https://smartapi.angelbroking.com/)
* **Config (`config/angel_config.json`)**:
```json
{
  "api_key": "YOUR_ANGEL_API_KEY",
  "client_code": "YOUR_CLIENT_ID",
  "pin": "YOUR_4_DIGIT_PIN",
  "totp_secret": "YOUR_BASE32_TOTP_SECRET"
}
```
* **Run**: `python main.py --broker ANGEL --auth` (or `--auth-mock` for paper trading)

### 2. Dhan DhanHQ API (100% Free)
* **Portal**: [dhanhq.co](https://dhanhq.co/) (Profile -> Access DhanHQ APIs -> Generate Access Token)
* **Config (`config/dhan_config.json`)**:
```json
{
  "client_id": "YOUR_DHAN_CLIENT_ID",
  "access_token": "YOUR_DHAN_PERMANENT_ACCESS_TOKEN"
}
```
* **Run**: `python main.py --broker DHAN --auth`

### 3. FYERS API v3 (100% Free)
* **Portal**: [myapi.fyers.in](https://myapi.fyers.in/)
* **Config (`config/fyers_config.json`)**:
```json
{
  "app_id": "YOUR_FYERS_APP_ID",
  "secret_key": "YOUR_FYERS_SECRET_KEY",
  "client_id": "YOUR_FYERS_USER_ID",
  "pin": "YOUR_4_DIGIT_PIN",
  "totp_secret": "YOUR_BASE32_TOTP_SECRET"
}
```
* **Run**: `python main.py --broker FYERS --auth`

### 4. Upstox Developer API (100% Free)
* **Portal**: [developer.upstox.com](https://developer.upstox.com/)
* **Config (`config/upstox_config.json`)**:
```json
{
  "api_key": "YOUR_UPSTOX_API_KEY",
  "api_secret": "YOUR_UPSTOX_API_SECRET",
  "redirect_uri": "http://127.0.0.1:5000/callback"
}
```
* **Run**: `python main.py --broker UPSTOX --auth`

### 5. Kotak Neo Trade API (100% Free)
* **Portal**: [kotaksecurities.com](https://www.kotaksecurities.com/) (Trade API Portal)
* **Config (`config/kotak_config.json`)**:
```json
{
  "consumer_key": "YOUR_KOTAK_CONSUMER_KEY",
  "consumer_secret": "YOUR_KOTAK_CONSUMER_SECRET",
  "mobile_number": "+91XXXXXXXXXX",
  "password": "YOUR_PASSWORD",
  "totp_secret": "YOUR_BASE32_TOTP_SECRET"
}
```
* **Run**: `python main.py --broker KOTAK --auth`

### 6. m.Stock Trading API Suite (100% Free)
* **Portal**: [mstock.com/trading-api](https://www.mstock.com/trading-api)
* **Config (`config/mstock_config.json`)**:
```json
{
  "api_key": "YOUR_MSTOCK_API_KEY",
  "api_secret": "YOUR_MSTOCK_API_SECRET",
  "client_id": "YOUR_MSTOCK_CLIENT_ID"
}
```
* **Run**: `python main.py --broker MSTOCK --auth`

### 7. ICICI Direct Breeze API (100% Free)
* **Portal**: [api.icicidirect.com](https://api.icicidirect.com/)
* **Config (`config/icici_config.json`)**:
```json
{
  "api_key": "YOUR_BREEZE_API_KEY",
  "api_secret": "YOUR_BREEZE_SECRET",
  "session_token": "YOUR_MORNING_SESSION_TOKEN"
}
```
* **Run**: `python main.py --broker ICICI --auth`

### 8. 5paisa Xstream API (100% Free)
* **Portal**: [xstream.5paisa.com](https://xstream.5paisa.com/)
* **Config (`config/5paisa_config.json`)**:
```json
{
  "user_key": "YOUR_5PAISA_USER_KEY",
  "encryption_key": "YOUR_5PAISA_ENCRYPTION_KEY",
  "client_code": "YOUR_5PAISA_CLIENT_CODE",
  "pin": "YOUR_PIN",
  "totp_secret": "YOUR_BASE32_TOTP_SECRET"
}
```
* **Run**: `python main.py --broker 5PAISA --auth`

### 9. Paytm Money Open API (100% Free)
* **Portal**: [developer.paytmmoney.com](https://developer.paytmmoney.com/)
* **Config (`config/paytm_config.json`)**:
```json
{
  "api_key": "YOUR_PAYTM_API_KEY",
  "api_secret": "YOUR_PAYTM_API_SECRET"
}
```
* **Run**: `python main.py --broker PAYTM --auth`

### 10. HDFC Sky API (100% Free)
* **Portal**: [hdfcsky.com](https://hdfcsky.com/) (Developer Section)
* **Config (`config/hdfcsky_config.json`)**:
```json
{
  "api_key": "YOUR_HDFC_SKY_API_KEY",
  "client_id": "YOUR_HDFC_SKY_CLIENT_ID",
  "access_token": "YOUR_ACCESS_TOKEN"
}
```
* **Run**: `python main.py --broker HDFCSKY --auth`

### 11. AxisDirect RapidAPI (100% Free)
* **Portal**: [simplehai.axisdirect.in/RapidAPI](https://simplehai.axisdirect.in/RapidAPI)
* **Config (`config/axis_config.json`)**:
```json
{
  "api_key": "YOUR_AXIS_RAPID_API_KEY",
  "client_id": "YOUR_AXIS_CLIENT_ID"
}
```
* **Run**: `python main.py --broker AXIS --auth`

### 12. Sharekhan / Espresso API (100% Free)
* **Portal**: [sharekhan.com/trading-api](https://www.sharekhan.com/trading-api)
* **Config (`config/sharekhan_config.json`)**:
```json
{
  "api_key": "YOUR_SHAREKHAN_API_KEY",
  "customer_id": "YOUR_CUSTOMER_ID",
  "access_token": "YOUR_ACCESS_TOKEN"
}
```
* **Run**: `python main.py --broker SHAREKHAN --auth`

### 13. Motilal Oswal MO API (100% Free)
* **Portal**: [invest.motilaloswal.com/moAPI](https://invest.motilaloswal.com/moAPI/)
* **Config (`config/motilal_config.json`)**:
```json
{
  "api_key": "YOUR_MO_API_KEY",
  "user_id": "YOUR_MO_USER_ID",
  "password": "YOUR_PASSWORD"
}
```
* **Run**: `python main.py --broker MOTILAL --auth`

### 14. Zerodha Kite Connect (Paid: ₹500/mo)
* **Portal**: [kite.trade](https://kite.trade/) (Waived if monthly brokerage ≥ ₹2,000)
* **Config (`config/zerodha_config.json`)**:
```json
{
  "api_key": "YOUR_KITE_API_KEY",
  "api_secret": "YOUR_KITE_API_SECRET",
  "redirect_url": "http://127.0.0.1:5000/callback"
}
```
* **Run**: `python main.py --broker ZERODHA --auth`

### 15. Groww Trade API (Paid: ₹499 + GST/mo)
* **Portal**: [groww.in/trade-api](https://groww.in/trade-api)
* **Config (`config/groww_config.json`)**:
```json
{
  "auth_mode": "totp",
  "api_key": "YOUR_GROWW_API_KEY_OR_TOTP_TOKEN",
  "api_secret": "YOUR_GROWW_API_SECRET",
  "totp_secret": "YOUR_GROWW_BASE32_TOTP_SECRET"
}
```
* **Run**: `python main.py --broker GROWW --auth`

---

## 3. How to Run the Bot with Any Broker

To run the algorithmic trading system with any broker, simply pass the `--broker` name:

```bash
# 1. Indian Market with Dhan
python main.py --market INDIA --broker DHAN

# 2. Indian Market with FYERS
python main.py --market INDIA --broker FYERS

# 3. Indian Market with Zerodha Kite
python main.py --market INDIA --broker ZERODHA

# 4. Indian Market with Groww
python main.py --market INDIA --broker GROWW

# 5. Offline Paper Trading Simulation (Any broker, 100% Free without credentials)
python main.py --market INDIA --broker DHAN --auth-mock
```


---

## 4. Complete Market Segments Coverage

The trading agent natively supports all primary regulated segments across Indian and International markets:

### 1. Exchange-Traded Currency Derivatives (Forex / NSE CDS)
* **Market Flag**: `--market FOREX`
* **Trading Window**: 09:00 – 17:00 IST
* **INR Pairs**: `USDINR`, `EURINR`, `GBPINR`, `JPYINR` (1,000 unit lot size; 100,000 for JPY).
* **Cross-Currency Pairs**: `EURUSD`, `GBPUSD`, `USDJPY`.
* **Commands**:
  ```bash
  # Inspect live spot & contract metrics
  python main.py --quote USDINR
  
  # Fetch complete option chain with Greeks & PCR for Forex
  python main.py --fno USDINR
  
  # Run paper trading on Forex currency derivatives
  python main.py --market FOREX --broker DHAN
  ```

### 2. Multi-Leg Automated Options Strategies
Construct, price, and execute multi-leg option strategies with real-time Black-Scholes Greeks, net debits/credits, and breakeven boundaries:
* **Bull Call Spread (Moderately Bullish)**:
  ```bash
  python main.py --spread NIFTY
  python main.py --spread RELIANCE
  ```
* **0-DTE Short Straddle (Expiry Neutral / Theta Decay)**:
  ```bash
  python main.py --straddle RELIANCE
  python main.py --straddle BANKNIFTY
  ```

### 3. Intraday 3:15 PM EOD Auto Square-Off
* Under SEBI regulations, open intraday MIS positions are liquidated automatically by broker RMS systems with penalty charges (₹50 + 18% GST per order).
* The bot enforces an internal **3:15 PM IST Auto Square-Off clock rule**: at 15:15 IST, all open intraday positions are closed automatically at market price to avoid broker penalties.

### 4. SQLite State Persistence & Crash Recovery (`--journal`)
* Open positions, trailing stop adjustments, and realized trade history are stored in a local SQLite database (`trading_data.db`).
* If your computer sleeps, restarts, or disconnects mid-session, the bot automatically restores active positions on startup.
* View your complete trade journal and performance statistics anytime:
  ```bash
  python main.py --journal
  ```

### 5. SME & Debt / Fixed Income Instruments
* **SME Equities (NSE Emerge / BSE SME)**: Quoting and lot verification for SME stocks (e.g., `CRAYONS` lot 2000, `VITAL` lot 1200, `KORE` lot 1600):
  ```bash
  python main.py --quote CRAYONS
  ```
* **Debt & Sovereign Gold Bonds (SGBs)**: Pricing for Sovereign Gold Bonds and Government Securities (`SGBGOLD`, `GSEC10Y`, `TBILL91`):
  ```bash
  python main.py --quote SGBGOLD
  python main.py --quote GSEC10Y
  ```
