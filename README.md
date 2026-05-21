# Binance Futures Testnet Trading Bot

A Python CLI application to place **MARKET** and **LIMIT** orders on
Binance Futures Testnet (USDT-M).

Built with a clean layered architecture — separate API, validation, order,
and CLI layers — with structured logging and proper error handling.

---

## Project Structure

```
trading_bot/
├── bot/
│   ├── __init__.py           # Makes bot/ a Python package
│   ├── client.py             # Binance API client wrapper
│   ├── orders.py             # Order placement logic
│   ├── validators.py         # Input validation
│   └── logging_config.py    # Logging configuration
├── logs/
│   └── trading_bot.log       # Auto-generated log file (not committed)
├── cli.py                    # CLI entry point (Typer)
├── .env                      # Your real API keys — NEVER commit this
├── .env.example              # Template showing required keys — safe to commit
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Prerequisites

- Python 3.10 or higher
- A Binance Futures Testnet account (free, takes 2 minutes)
- Git

---

## Step 1 — Get Testnet API Keys

You need your own Binance Futures Testnet API credentials.

1. Go to **https://testnet.binancefuture.com**
2. Click **"Log In with GitHub"** (only login option — no email needed)
3. After login, click your **profile icon** in the top right
4. Click **"API Key"** then **"Generate API Key"**
5. Copy both the **API Key** and **Secret Key** immediately
   > The Secret Key is shown only once — copy it before closing the page

---

## Step 2 — Clone the Repository

```bash
git clone https://github.com/yourusername/trading_bot.git
cd trading_bot
```

---

## Step 3 — Create Your .env File

The `.env` file holds your real API keys. It is listed in `.gitignore`
so it will never be pushed to GitHub.

Create it by copying the provided template:

**Windows (PowerShell):**
```powershell
copy .env.example .env
```

**Mac/Linux:**
```bash
cp .env.example .env
```

Now open `.env` and replace the placeholder values with your real keys:

```env
API_KEY=your_actual_api_key_here
API_SECRET=your_actual_api_secret_here
```

> Never share this file or commit it to version control.

---

## Step 4 — Create and Activate Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Mac/Linux:**
```bash
python -m venv venv
source venv/bin/activate
```

You should see `(venv)` at the start of your terminal prompt.

---

## Step 5 — Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Step 6 — Run the Bot

### Place a MARKET order

```bash
# BUY MARKET order
python cli.py --symbol BTCUSDT --side BUY --order-type MARKET --quantity 0.001

# SELL MARKET order
python cli.py --symbol ETHUSDT --side SELL --order-type MARKET --quantity 0.01
```

### Place a LIMIT order

```bash
# BUY LIMIT order — price must be within range of current market price
python cli.py --symbol BTCUSDT --side BUY --order-type LIMIT --quantity 0.001 --price 70000.0

# SELL LIMIT order
python cli.py --symbol BTCUSDT --side SELL --order-type LIMIT --quantity 0.001 --price 74000.0
```

### View help

```bash
python cli.py --help
```

---

## Example Output

```
==================================================
        BINANCE FUTURES TESTNET BOT
==================================================
  ORDER REQUEST SUMMARY
--------------------------------------------------
  Symbol     : BTCUSDT
  Side       : BUY
  Order Type : MARKET
  Quantity   : 0.001
  Price      : N/A (MARKET)
--------------------------------------------------
  Connecting to Binance Futures Testnet...
  Connection successful!
  Placing MARKET order...

==================================================
  ORDER RESPONSE
--------------------------------------------------
  Order ID     : 13171749033
  Symbol       : BTCUSDT
  Side         : BUY
  Type         : MARKET
  Quantity     : 0.0010
  Status       : NEW
  Executed Qty : 0.0000
  Avg Price    : 0.00
--------------------------------------------------
  SUCCESS: Order placed successfully!
==================================================
```

---

## Logging

All activity is automatically logged to `logs/trading_bot.log`.

| Level   | What is logged |
|---------|---------------|
| DEBUG   | API request params, validation steps, raw responses |
| INFO    | Order placement, connection status, success events |
| WARNING | Invalid input attempts |
| ERROR   | API errors, network failures, unexpected exceptions |

Example log entries:

```
2026-05-21 15:52:00 | DEBUG    | bot.client  | API credentials loaded successfully from .env
2026-05-21 15:52:00 | INFO     | bot.client  | Successfully connected to Binance Futures Testnet
2026-05-21 15:52:01 | INFO     | bot.orders  | Placing MARKET order | BUY 0.001 BTCUSDT
2026-05-21 15:52:01 | INFO     | bot.orders  | MARKET order placed successfully | OrderId: 13171749033 | Status: NEW
```

The log file rotates automatically at 1 MB and keeps the last 3 files.

---

## Error Handling

The bot catches and displays all errors clearly without crashing.

| Error Type | Example | How it is handled |
|------------|---------|-------------------|
| Missing API keys | Empty `.env` file | Clear message with setup instructions |
| Invalid symbol | `BTCUSD` instead of `BTCUSDT` | Validation error with example |
| Invalid side | `HOLD` instead of `BUY/SELL` | Validation error listing valid options |
| Missing price | LIMIT order without `--price` | Specific error asking for price |
| Price out of range | LIMIT price too far from market | Binance error code and message shown |
| Network failure | No internet connection | Connection error with details |

---

## Assumptions

- Designed for **Binance Futures Testnet (USDT-M)** only — not for live trading
- Minimum order quantity varies by symbol (0.001 BTC, 0.01 ETH, etc.)
- LIMIT order price must be within Binance's allowed range of the current market price
- MARKET orders on Testnet may show status `NEW` instead of `FILLED` — this is normal Testnet behaviour
- Testnet balances are fake — no real money is involved

---

## Tech Stack

| Library | Version | Purpose |
|---------|---------|---------|
| `python-binance` | 1.0.19 | Binance Futures API client |
| `typer` | 0.9.0 | CLI framework |
| `python-dotenv` | 1.0.0 | Load API keys from `.env` |
| `logging` | stdlib | Structured file and console logging |