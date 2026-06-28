"""
config.py — Single source of truth for all bot settings.

Credentials are loaded from .env so they never appear in source code.
Trading parameters are edited directly here.
"""
import os

import MetaTrader5 as mt5
from dotenv import load_dotenv

load_dotenv()

# ── Credentials (from .env — never hard-code these) ──────────────────────
try:
    LOGIN    = int(os.environ["MT5_LOGIN"])
    PASSWORD = os.environ["MT5_PASSWORD"]
    SERVER   = os.environ["MT5_SERVER"]
except KeyError as missing:
    raise RuntimeError(
        f"Missing environment variable {missing}. "
        "Copy .env.example → .env and fill in your MT5 credentials."
    ) from missing

# ── Symbol & Timeframe ────────────────────────────────────────────────────
SYMBOL    = "BTCUSDm"
TIMEFRAME = mt5.TIMEFRAME_M1   # M1 | M5 | M15 | H1 | H4 | D1

# ── Order Parameters ──────────────────────────────────────────────────────
LOT      = 0.01
SLIPPAGE = 500    # max allowed slippage in broker points
MAGIC    = 1001   # unique ID to tag all orders from this bot

# ── Strategy Parameters ───────────────────────────────────────────────────
EMA_FAST    = 9
EMA_SLOW    = 12
RISK_REWARD = 3   # TP = Risk × 3
BREAK_EVEN  = 1   # move SL to entry after Risk × 1 in profit
