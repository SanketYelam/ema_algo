# EMA 9/12 Crossover Trading Bot

Automated MetaTrader 5 trading bot using an EMA 9/12 crossover strategy.  
Trades BTCUSDm (or any symbol) on Exness with clean risk management.

---

## Strategy at a Glance

| Item        | Value                                         |
|-------------|-----------------------------------------------|
| Indicator   | EMA 9 and EMA 12                              |
| Entry       | Open of the candle after the crossover        |
| BUY SL      | Low of the crossover candle                   |
| SELL SL     | High of the crossover candle                  |
| Take Profit | 1 : 3 Risk/Reward                             |
| Break Even  | Move SL to entry after 1 : 1 profit           |

---

## Project Structure

```
ema9_12/
├── main.py          # Entry point — connect, run, disconnect
├── strategy.py      # All trading logic
├── mt5_connection.py# MT5 login / logout
├── config.py        # Broker credentials  ← KEEP PRIVATE
├── logger.py        # Timestamped console logging
├── requirements.txt # Python dependencies
└── README.md        # This file
```

---

## Requirements

- Python 3.8 or later
- MetaTrader 5 desktop terminal installed and logged in
- An Exness live or demo account

---

## Installation

**Step 1 — Clone or copy the project folder**

```
ema9_12/
```

**Step 2 — Install Python dependencies**

```bash
pip install -r requirements.txt
```

**Step 3 — Set your broker credentials in `config.py`**

```python
LOGIN    = 123456789         # Your MT5 account number
PASSWORD = "your_password"   # Your MT5 password
SERVER   = "Exness-MT5Real8" # Your broker server
```

> Find your server name in the MT5 terminal under  
> File → Open Account → look for the server dropdown.

---

## Running the Bot

```bash
python main.py
```

The bot will:
1. Connect to MT5 and log your account balance
2. Enable BTCUSDm in Market Watch
3. Start monitoring every second for EMA crossovers
4. Print timestamped logs for every event

To stop the bot cleanly, press **Ctrl+C**.

---

## Configuration Guide

All settings are at the top of `strategy.py`.

### Change the Trading Symbol

```python
SYMBOL = "EURUSDm"   # or XAUUSDm, ETHUSDm, NASDAQm, etc.
```

### Change the Lot Size

```python
LOT = 0.05   # Increase or decrease position size
```

> Minimum lot for BTCUSDm on Exness is usually 0.01.

### Change the EMA Periods

```python
EMA_FAST = 9    # Shorter period reacts faster
EMA_SLOW = 12   # Longer period is smoother
```

> The crossover fires when EMA_FAST crosses EMA_SLOW.

### Change the Timeframe

```python
TIMEFRAME = mt5.TIMEFRAME_M5    # 5-minute candles
TIMEFRAME = mt5.TIMEFRAME_M15   # 15-minute candles
TIMEFRAME = mt5.TIMEFRAME_H1    # 1-hour candles
TIMEFRAME = mt5.TIMEFRAME_H4    # 4-hour candles
TIMEFRAME = mt5.TIMEFRAME_D1    # Daily candles
```

### Change Risk/Reward

```python
RISK_REWARD = 2   # TP at 2x risk instead of 3x
```

### Change Break Even Level

```python
BREAK_EVEN = 1.5  # Move SL to entry after 1.5x risk in profit
```

---

## Sample Console Output

```
[2026-06-28 14:00:01]  MT5 Connected | Account: 433816875 | Balance: 1000.0 USD
[2026-06-28 14:00:01]  Symbol ready | BTCUSDm | Digits: 2 | Spread: 120 pts
[2026-06-28 14:00:01]  ============================================================
[2026-06-28 14:00:01]    EMA Crossover Bot  |  RUNNING
[2026-06-28 14:00:01]    Symbol      : BTCUSDm
[2026-06-28 14:00:01]    Timeframe   : 1
[2026-06-28 14:00:01]    EMA Fast    : 9  |  EMA Slow: 12
[2026-06-28 14:00:01]    Lot Size    : 0.01
[2026-06-28 14:00:01]    Risk/Reward : 1 : 3
[2026-06-28 14:00:01]    Break Even  : After 1 : 1
[2026-06-28 14:00:01]  ============================================================
[2026-06-28 14:01:00]  ────────────────────────────────────────────────────────────
[2026-06-28 14:01:00]  New Candle | 2026-06-28  14:01 UTC  |  Current Time: 14:01:00
[2026-06-28 14:01:00]  EMA9: 64821.35  |  EMA12: 64815.22
[2026-06-28 14:01:00]  Signal: BUY  | Crossover bar @ 14:00 UTC | EMA9: 64821.35 > EMA12: 64815.22
[2026-06-28 14:01:00]  BUY Opened  | Entry: 64835.00 | SL: 64720.00 | TP: 65180.00 | Risk: 115.00
[2026-06-28 14:04:30]  Break Even Activated | BUY | SL moved to Entry: 64835.00
[2026-06-28 14:06:00]  Trade Closed
```

---

## Important Notes

- **config.py contains your password** — never upload it to GitHub or share it.
- The bot must run on a machine where the **MT5 terminal is open and logged in**.
- Exness has minimum stop distance requirements — if an order is rejected,  
  check that the SL is far enough from the entry price.
- Always test on a **demo account** before going live.

---

## Troubleshooting

| Problem | Solution |
|---|---|
| `MT5 initialize() failed` | Open the MT5 terminal manually first |
| `MT5 login failed` | Double-check LOGIN, PASSWORD, SERVER in config.py |
| `BUY/SELL rejected` | SL may be too close to price; try a higher timeframe |
| `No valid tick` | Market is closed (weekend) or symbol is not active |
| `Cannot select symbol` | Symbol name may differ on your broker (check Market Watch) |
