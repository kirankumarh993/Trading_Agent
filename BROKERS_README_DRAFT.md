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
