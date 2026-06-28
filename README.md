# EMA 9/12 Crossover Trading Bot

An automated trading bot for **MetaTrader 5** that trades **BTCUSDm** on **Exness**
using the EMA 9/12 crossover strategy with built-in risk management.

---

## Strategy at a Glance

| Item | Details |
|---|---|
| Indicator | EMA 9 (fast) and EMA 12 (slow) |
| BUY Signal | EMA 9 crosses **above** EMA 12 + bullish candle |
| SELL Signal | EMA 9 crosses **below** EMA 12 + bearish candle |
| Entry | Open of the next candle after crossover |
| Stop Loss | Low (BUY) / High (SELL) of the crossover candle |
| Take Profit | 1 : 3 Risk/Reward |
| Break Even | SL moves to entry after price reaches 1 : 1 profit |

---

## Project Structure

```
ema9_12/
│
├── main.py            # Start the bot from here
├── strategy.py        # All trading logic
├── mt5_connection.py  # Connects and disconnects MT5
├── config.py          # All settings (symbol, lot, EMA, RR, etc.)
├── logger.py          # Handles all log printing
├── requirements.txt   # Python packages needed
├── .env               # Your secret credentials (NEVER share this)
├── .env.example       # Template showing what .env should look like
├── .gitignore         # Tells Git to ignore .env and other files
└── README.md          # This file
```

---

## What You Need Before Starting

Make sure you have all three of these installed on your PC:

### 1. Python 3.8 or later
Download from: https://www.python.org/downloads/

> During installation, check the box that says **"Add Python to PATH"**

Verify installation — open Command Prompt and type:
```
python --version
```
You should see something like: `Python 3.13.14`

---

### 2. Git
Download from: https://git-scm.com/downloads

Verify installation:
```
git --version
```
You should see something like: `git version 2.47.0`

---

### 3. MetaTrader 5 Terminal
Download from: https://www.metatrader5.com/en/download

- Install it
- Open the app
- Log in with your **Exness** demo or live account
- **Keep it open while the bot is running**

---

## Setup — Step by Step

Follow these steps in order. Do not skip any step.

---

### Step 1 — Download the Project

Open **Command Prompt** or **PowerShell** and run:

```
git clone https://github.com/SanketYelam/ema_algo.git
```

This creates a folder called `ema_algo` on your PC with all the bot files.

Then move into that folder:

```
cd ema_algo
```

---

### Step 2 — Create a Virtual Environment

A virtual environment keeps this project's packages separate from other Python projects on your PC.

```
python -m venv venv
```

You will see a new folder called `venv` appear inside the project. That is correct.

> **What is a virtual environment?**
> Think of it as a clean, isolated box for this project's Python packages.
> It prevents conflicts with other projects on your PC.

---

### Step 3 — Activate the Virtual Environment

**Windows (Command Prompt):**
```
venv\Scripts\activate
```

**Windows (PowerShell):**
```
venv\Scripts\Activate.ps1
```

**Mac / Linux:**
```
source venv/bin/activate
```

After activation, your terminal prompt will change to show `(venv)` at the start.
This tells you the virtual environment is active.

Example:
```
(venv) C:\Users\YourName\ema_algo>
```

> **Important:** You must activate the virtual environment **every time** you open
> a new terminal before running the bot.

---

### Step 4 — Install Required Packages

```
pip install -r requirements.txt
```

This installs all 4 required packages automatically:
- `MetaTrader5` — connects Python to the MT5 terminal
- `pandas` — used for EMA calculations
- `numpy` — required by pandas
- `python-dotenv` — reads your credentials from the `.env` file

Wait for it to finish. You will see `Successfully installed ...` at the end.

---

### Step 5 — Set Up Your Credentials

Your MT5 account credentials must be stored in a file called `.env`.

**Copy the template file:**

```
copy .env.example .env
```

Now open the `.env` file in any text editor (Notepad is fine) and fill in your details:

```
MT5_LOGIN=your_account_number
MT5_PASSWORD=your_password
MT5_SERVER=your_server_name
```

**Example:**
```
MT5_LOGIN=433816875
MT5_PASSWORD=MyPassword123
MT5_SERVER=Exness-MT5Trial7
```

> **How to find your Server Name:**
> Open MetaTrader 5 → click **File** → click **Open Account**
> → your server name is shown in the dropdown list.

> **Security Note:** The `.env` file is listed in `.gitignore`, which means
> Git will never upload it to GitHub. Your password stays on your PC only.

---

### Step 6 — Open MetaTrader 5

Before running the bot:
1. Open the **MetaTrader 5** desktop app
2. Make sure you are **logged in** to your account
3. Make sure **AutoTrading is enabled** (button in the top toolbar should be green)
4. **Leave MT5 open** — do not close it while the bot is running

---

### Step 7 — Run the Bot

Make sure your virtual environment is active (you see `(venv)` in the terminal), then run:

```
python main.py
```

The bot will start and print logs like this:

```
[2026-06-28 14:00:01]  INFO      MT5 Connected | Account: 433816875 | Balance: 1000.0 USD
[2026-06-28 14:00:01]  INFO      Symbol ready | BTCUSDm | Digits: 2 | Spread: 120 pts
[2026-06-28 14:00:01]  INFO      ============================================================
[2026-06-28 14:00:01]  INFO        EMA Crossover Bot  |  RUNNING
[2026-06-28 14:00:01]  INFO        Symbol : BTCUSDm  |  Timeframe : 1
[2026-06-28 14:00:01]  INFO        EMA    : 9 / 12   |  Lot : 0.01
[2026-06-28 14:00:01]  INFO        RR     : 1:3       |  Break Even : 1:1
[2026-06-28 14:00:01]  INFO      ============================================================
[2026-06-28 14:01:00]  INFO      ────────────────────────────────────────────────────────────
[2026-06-28 14:01:00]  INFO      New Candle | 2026-06-28  14:01 UTC  |  Local: 14:01:00
[2026-06-28 14:01:00]  INFO      EMA9: 64821.35  |  EMA12: 64815.22
[2026-06-28 14:01:00]  INFO      Signal: BUY  | Bar @ 14:00 UTC | EMA9: 64821.35 > EMA12: 64815.22
[2026-06-28 14:01:00]  INFO      BUY Opened  | Entry: 64835.00 | SL: 64720.00 | TP: 65180.00 | Risk: 115.00
[2026-06-28 14:04:30]  INFO      Break Even Activated | BUY | SL → 64835.00
[2026-06-28 14:06:00]  INFO      Trade Closed
```

---

### Step 8 — Stop the Bot

To stop the bot cleanly at any time, press:

```
Ctrl + C
```

The bot will print `Bot stopped by user (Ctrl+C)` and disconnect from MT5.

---

## Configuration Guide

All settings are in **`config.py`**. Open this file to change any of them.

### Change the Trading Symbol

```python
SYMBOL = "EURUSDm"    # Euro vs US Dollar
SYMBOL = "XAUUSDm"    # Gold vs US Dollar
SYMBOL = "ETHUSDm"    # Ethereum vs US Dollar
SYMBOL = "NASDAQm"    # NASDAQ index
```

> Make sure the symbol is available in your broker's Market Watch.

---

### Change the Lot Size

```python
LOT = 0.01    # Minimum size — good for testing
LOT = 0.05    # Medium size
LOT = 0.10    # Larger size
```

> For BTCUSDm on Exness, the minimum lot is `0.01`.
> Never increase lot size before testing on a demo account.

---

### Change the EMA Periods

```python
EMA_FAST = 9     # Reacts quickly to price changes
EMA_SLOW = 12    # Reacts more slowly — acts as a filter
```

> A crossover happens when EMA_FAST crosses above or below EMA_SLOW.
> Smaller numbers = more signals but more false signals.
> Larger numbers = fewer signals but stronger confirmation.

---

### Change the Timeframe

```python
TIMEFRAME = mt5.TIMEFRAME_M1    # 1 minute  — more trades, more noise
TIMEFRAME = mt5.TIMEFRAME_M5    # 5 minutes
TIMEFRAME = mt5.TIMEFRAME_M15   # 15 minutes
TIMEFRAME = mt5.TIMEFRAME_H1    # 1 hour    — fewer trades, more reliable
TIMEFRAME = mt5.TIMEFRAME_H4    # 4 hours
TIMEFRAME = mt5.TIMEFRAME_D1    # Daily
```

---

### Change Risk/Reward Ratio

```python
RISK_REWARD = 2    # TP at 2× risk
RISK_REWARD = 3    # TP at 3× risk (default)
```

---

### Change Break Even Level

```python
BREAK_EVEN = 1     # Move SL to entry after 1× risk in profit (default)
BREAK_EVEN = 1.5   # Move SL to entry after 1.5× risk in profit
```

---

## Push Code to GitHub

Follow these steps if you want to save your code or changes to GitHub.

### First Time Setup (only do this once)

```
git init
git remote add origin https://github.com/SanketYelam/ema_algo.git
git branch -M main
```

### Every Time You Want to Push Changes

**Step 1 — Check what files you changed:**
```
git status
```

**Step 2 — Stage your changes:**
```
git add .
```

> This stages all changed files. `.env` is automatically excluded by `.gitignore`
> so your password is never uploaded.

**Step 3 — Write a commit message describing what you changed:**
```
git commit -m "describe what you changed here"
```

Example:
```
git commit -m "Changed symbol to XAUUSDm and lot size to 0.05"
```

**Step 4 — Push to GitHub:**
```
git push origin main
```

**Step 5 — Verify on GitHub:**
Open https://github.com/SanketYelam/ema_algo in your browser.
You should see your latest files there.

---

## Quick Reference — All Commands Together

```
# Clone the project (only once)
git clone https://github.com/SanketYelam/ema_algo.git
cd ema_algo

# Create virtual environment (only once)
python -m venv venv

# Activate virtual environment (every time you open a new terminal)
venv\Scripts\activate              # Windows CMD
venv\Scripts\Activate.ps1         # Windows PowerShell

# Install packages (only once)
pip install -r requirements.txt

# Set up credentials (only once)
copy .env.example .env
# Then open .env and fill in your MT5 login, password, server

# Run the bot
python main.py

# Stop the bot
Ctrl + C

# Push changes to GitHub
git add .
git commit -m "your message here"
git push origin main
```

---

## Troubleshooting

| Problem | What it means | How to fix |
|---|---|---|
| `MT5 initialize() failed` | MT5 terminal is not open | Open MetaTrader 5 and log in first |
| `MT5 login failed` | Wrong credentials | Check `.env` — LOGIN, PASSWORD, SERVER |
| `Missing environment variable` | `.env` file is missing or incomplete | Run `copy .env.example .env` and fill in your details |
| `BUY/SELL rejected` | SL is too close to price | Try a higher timeframe like M5 or M15 |
| `No valid tick` | Market is closed | Crypto markets run 24/7 — check your internet connection |
| `Cannot select symbol` | Symbol name is wrong | Open MT5 → Market Watch and check the exact symbol name |
| `ModuleNotFoundError` | Packages not installed or venv not active | Run `venv\Scripts\activate` then `pip install -r requirements.txt` |
| `(venv) not showing in terminal` | Virtual environment is not active | Run `venv\Scripts\activate` before `python main.py` |

---

## Important Warnings

- **Always test on a DEMO account first.** Never run on a live account without testing.
- **Keep MetaTrader 5 open** while the bot is running. The bot talks to the MT5 app on your PC.
- **Never share your `.env` file.** It contains your account password.
- **Never push `.env` to GitHub.** The `.gitignore` file prevents this automatically.
- **AutoTrading must be enabled** in MT5 (green button in the toolbar) for orders to go through.
