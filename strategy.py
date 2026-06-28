"""
strategy.py — EMA 9/12 Crossover Trading Strategy.

Contains only trading logic. All settings live in config.py.

Strategy summary:
  BUY   EMA_FAST crosses above EMA_SLOW + crossover candle is bullish
  SELL  EMA_FAST crosses below EMA_SLOW + crossover candle is bearish
  Entry Open of the candle after the crossover (market order)
  SL    Low (BUY) or High (SELL) of the crossover candle
  TP    Entry ± Risk × RISK_REWARD
  BE    Move SL to entry once price reaches Risk × BREAK_EVEN
"""
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Tuple

import MetaTrader5 as mt5
import numpy as np
import pandas as pd

from config import (
    BREAK_EVEN, EMA_FAST, EMA_SLOW, LOT, MAGIC,
    RISK_REWARD, SLIPPAGE, SYMBOL, TIMEFRAME,
)
from logger import logger

# Minimum closed bars needed before the strategy can evaluate signals
_MIN_BARS: int = max(EMA_FAST, EMA_SLOW) + 10


# ── State ────────────────────────────────────────────────────────────────

@dataclass
class _BotState:
    """Mutable runtime state. One instance lives for the duration of run_strategy()."""
    last_candle_time:     int  = 0
    last_signal_bar_time: int  = 0
    break_even_done:      bool = False
    had_position:         bool = False


# ── Symbol ───────────────────────────────────────────────────────────────

def select_symbol() -> bool:
    """Enable the symbol in Market Watch and verify it is tradeable."""
    if not mt5.symbol_select(SYMBOL, True):
        logger.error(f"Cannot select {SYMBOL} | {mt5.last_error()}")
        return False

    info = mt5.symbol_info(SYMBOL)
    if info is None or not info.visible:
        logger.error(f"Symbol {SYMBOL} unavailable or not visible in Market Watch")
        return False

    logger.info(f"Symbol ready | {SYMBOL} | Digits: {info.digits} | Spread: {info.spread} pts")
    return True


# ── Market Data ──────────────────────────────────────────────────────────

def get_rates(count: int = 100) -> Optional[np.ndarray]:
    """
    Fetch the last `count` OHLCV candles.
    rates[0] = oldest  |  rates[-2] = last closed bar  |  rates[-1] = live bar
    """
    rates = mt5.copy_rates_from_pos(SYMBOL, TIMEFRAME, 0, count)

    if rates is None:
        logger.error(f"get_rates() failed | {mt5.last_error()}")
        return None

    if len(rates) < _MIN_BARS:
        logger.warning(f"Insufficient bars | Got {len(rates)}, need {_MIN_BARS}")
        return None

    return rates


# ── EMA ──────────────────────────────────────────────────────────────────

def calculate_ema(rates: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute EMA_FAST and EMA_SLOW across all bars.
    Uses pandas ewm(adjust=False) — matches MT5's built-in EMA formula.
    Returns two numpy arrays aligned 1-to-1 with the rates array.
    """
    closes   = pd.Series([r['close'] for r in rates])
    ema_fast = closes.ewm(span=EMA_FAST, adjust=False).mean().values
    ema_slow = closes.ewm(span=EMA_SLOW, adjust=False).mean().values
    return ema_fast, ema_slow


# ── Candle Detection ─────────────────────────────────────────────────────

def is_new_candle(rates: np.ndarray, state: _BotState) -> bool:
    """Return True when rates[-1] carries a timestamp we haven't seen yet."""
    bar_time = int(rates[-1]['time'])
    if bar_time != state.last_candle_time:
        state.last_candle_time = bar_time
        return True
    return False


# ── Signals ──────────────────────────────────────────────────────────────

def check_buy_signal(
    rates: np.ndarray,
    ema_fast: np.ndarray,
    ema_slow: np.ndarray,
    state: _BotState,
) -> bool:
    """
    True when rates[-2] (last closed candle) shows a confirmed bullish crossover.
    Uses only closed-bar EMA values (rates[-3] → rates[-2]) — no repainting.
    """
    crossover_bar_time = int(rates[-2]['time'])
    if crossover_bar_time == state.last_signal_bar_time:
        return False

    crossed_up = ema_fast[-3] < ema_slow[-3] and ema_fast[-2] > ema_slow[-2]
    if not crossed_up:
        return False

    if rates[-2]['close'] <= rates[-2]['open']:   # crossover candle must be bullish
        return False

    logger.info(
        f"Signal: BUY  | Bar @ {_fmt_bar_time(crossover_bar_time)}"
        f" | EMA{EMA_FAST}: {ema_fast[-2]:.2f} > EMA{EMA_SLOW}: {ema_slow[-2]:.2f}"
    )
    return True


def check_sell_signal(
    rates: np.ndarray,
    ema_fast: np.ndarray,
    ema_slow: np.ndarray,
    state: _BotState,
) -> bool:
    """
    True when rates[-2] (last closed candle) shows a confirmed bearish crossover.
    """
    crossover_bar_time = int(rates[-2]['time'])
    if crossover_bar_time == state.last_signal_bar_time:
        return False

    crossed_down = ema_fast[-3] > ema_slow[-3] and ema_fast[-2] < ema_slow[-2]
    if not crossed_down:
        return False

    if rates[-2]['close'] >= rates[-2]['open']:   # crossover candle must be bearish
        return False

    logger.info(
        f"Signal: SELL | Bar @ {_fmt_bar_time(crossover_bar_time)}"
        f" | EMA{EMA_FAST}: {ema_fast[-2]:.2f} < EMA{EMA_SLOW}: {ema_slow[-2]:.2f}"
    )
    return True


# ── Position Helpers ─────────────────────────────────────────────────────

def has_open_position() -> bool:
    """True if any position on SYMBOL is tagged with our MAGIC number."""
    positions = mt5.positions_get(symbol=SYMBOL)
    return bool(positions and any(p.magic == MAGIC for p in positions))


def _get_filling_type() -> int:
    """Read the broker's supported filling mode for this symbol dynamically."""
    info = mt5.symbol_info(SYMBOL)
    if info and info.filling_mode & 2:
        return mt5.ORDER_FILLING_IOC
    if info and info.filling_mode & 1:
        return mt5.ORDER_FILLING_FOK
    return mt5.ORDER_FILLING_IOC


# ── Orders ───────────────────────────────────────────────────────────────

def open_buy(rates: np.ndarray, state: _BotState, tick) -> bool:
    """Place a market BUY. Entry = ask | SL = crossover low | TP = entry + risk×RR."""
    crossover = rates[-2]
    entry     = tick.ask
    sl        = crossover['low']
    risk      = entry - sl

    if risk <= 0:
        logger.error(f"BUY skipped | SL {sl:.2f} >= Entry {entry:.2f} — invalid risk")
        return False

    tp     = entry + risk * RISK_REWARD
    result = mt5.order_send(_build_order(mt5.ORDER_TYPE_BUY, entry, sl, tp))

    if result and result.retcode == mt5.TRADE_RETCODE_DONE:
        logger.info(f"BUY Opened  | Entry: {entry:.2f} | SL: {sl:.2f} | TP: {tp:.2f} | Risk: {risk:.2f}")
        state.last_signal_bar_time = int(crossover['time'])
        state.break_even_done      = False
        return True

    logger.error(f"BUY rejected | {getattr(result, 'retcode', mt5.last_error())} | {getattr(result, 'comment', '')}")
    return False


def open_sell(rates: np.ndarray, state: _BotState, tick) -> bool:
    """Place a market SELL. Entry = bid | SL = crossover high | TP = entry - risk×RR."""
    crossover = rates[-2]
    entry     = tick.bid
    sl        = crossover['high']
    risk      = sl - entry

    if risk <= 0:
        logger.error(f"SELL skipped | SL {sl:.2f} <= Entry {entry:.2f} — invalid risk")
        return False

    tp     = entry - risk * RISK_REWARD
    result = mt5.order_send(_build_order(mt5.ORDER_TYPE_SELL, entry, sl, tp))

    if result and result.retcode == mt5.TRADE_RETCODE_DONE:
        logger.info(f"SELL Opened | Entry: {entry:.2f} | SL: {sl:.2f} | TP: {tp:.2f} | Risk: {risk:.2f}")
        state.last_signal_bar_time = int(crossover['time'])
        state.break_even_done      = False
        return True

    logger.error(f"SELL rejected | {getattr(result, 'retcode', mt5.last_error())} | {getattr(result, 'comment', '')}")
    return False


def modify_sl(ticket: int, new_sl: float) -> bool:
    """Move the SL of position `ticket` to `new_sl`. TP is preserved."""
    positions = mt5.positions_get(ticket=ticket)
    if not positions:
        logger.error(f"modify_sl: ticket {ticket} not found")
        return False

    result = mt5.order_send({
        "action":   mt5.TRADE_ACTION_SLTP,
        "symbol":   SYMBOL,
        "position": ticket,
        "sl":       new_sl,
        "tp":       positions[0].tp,
    })

    if result and result.retcode == mt5.TRADE_RETCODE_DONE:
        return True

    logger.error(f"modify_sl rejected | {getattr(result, 'retcode', mt5.last_error())} | {getattr(result, 'comment', '')}")
    return False


def manage_break_even(state: _BotState, tick) -> None:
    """
    Move SL to entry price once price moves BREAK_EVEN × risk in our favour.
    Fires at most once per trade, guarded by state.break_even_done.
    Risk is reconstructed from TP to avoid storing it separately.
    """
    if state.break_even_done:
        return

    for pos in (mt5.positions_get(symbol=SYMBOL) or []):
        if pos.magic != MAGIC:
            continue

        entry, tp, sl = pos.price_open, pos.tp, pos.sl

        if pos.type == mt5.ORDER_TYPE_BUY:
            risk       = (tp - entry) / RISK_REWARD
            be_trigger = entry + risk * BREAK_EVEN
            if tick.bid >= be_trigger and (sl == 0 or sl < entry):
                if modify_sl(pos.ticket, entry):
                    state.break_even_done = True
                    logger.info(f"Break Even Activated | BUY | SL → {entry:.2f}")

        elif pos.type == mt5.ORDER_TYPE_SELL:
            risk       = (entry - tp) / RISK_REWARD
            be_trigger = entry - risk * BREAK_EVEN
            if tick.ask <= be_trigger and (sl == 0 or sl > entry):
                if modify_sl(pos.ticket, entry):
                    state.break_even_done = True
                    logger.info(f"Break Even Activated | SELL | SL → {entry:.2f}")


# ── Loop Helpers (Single Responsibility) ─────────────────────────────────

def _on_tick(state: _BotState, tick) -> bool:
    """Per-second work: detect trade closure + manage break-even. Returns position status."""
    currently_open = has_open_position()

    if state.had_position and not currently_open:
        logger.info("Trade Closed")
        state.break_even_done = False

    state.had_position = currently_open

    if currently_open:
        manage_break_even(state, tick)

    return currently_open


def _on_new_candle(rates: np.ndarray, state: _BotState, tick, currently_open: bool) -> None:
    """Per-candle work: log EMA values and evaluate entry signals."""
    candle_dt = datetime.utcfromtimestamp(int(rates[-1]['time']))
    logger.info("─" * 60)
    logger.info(
        f"New Candle | {candle_dt.strftime('%Y-%m-%d  %H:%M')} UTC"
        f"  |  Local: {datetime.now().strftime('%H:%M:%S')}"
    )

    ema_fast_arr, ema_slow_arr = calculate_ema(rates)
    logger.info(f"EMA{EMA_FAST}: {ema_fast_arr[-2]:.2f}  |  EMA{EMA_SLOW}: {ema_slow_arr[-2]:.2f}")

    if currently_open:
        logger.info("Position open — holding, no new entries")
        return

    if check_buy_signal(rates, ema_fast_arr, ema_slow_arr, state):
        open_buy(rates, state, tick)
    elif check_sell_signal(rates, ema_fast_arr, ema_slow_arr, state):
        open_sell(rates, state, tick)
    else:
        logger.info("No signal")


# ── Private Utilities ────────────────────────────────────────────────────

def _build_order(order_type: int, price: float, sl: float, tp: float) -> dict:
    """Build the MT5 order request dict. Shared by open_buy and open_sell."""
    return {
        "action":       mt5.TRADE_ACTION_DEAL,
        "symbol":       SYMBOL,
        "volume":       LOT,
        "type":         order_type,
        "price":        price,
        "sl":           sl,
        "tp":           tp,
        "deviation":    SLIPPAGE,
        "magic":        MAGIC,
        "comment":      "EMA_BUY" if order_type == mt5.ORDER_TYPE_BUY else "EMA_SELL",
        "type_time":    mt5.ORDER_TIME_GTC,
        "type_filling": _get_filling_type(),
    }


def _fmt_bar_time(unix_ts: int) -> str:
    return datetime.utcfromtimestamp(unix_ts).strftime('%H:%M')


# ── Entry Point ──────────────────────────────────────────────────────────

def run_strategy() -> None:
    """Main bot loop. Checks every second; evaluates signals once per new candle."""
    state = _BotState()

    if not select_symbol():
        logger.error("Symbol selection failed — exiting.")
        return

    logger.info("=" * 60)
    logger.info("  EMA Crossover Bot  |  RUNNING")
    logger.info(f"  Symbol : {SYMBOL}  |  Timeframe : {TIMEFRAME}")
    logger.info(f"  EMA    : {EMA_FAST} / {EMA_SLOW}  |  Lot : {LOT}")
    logger.info(f"  RR     : 1:{RISK_REWARD}  |  Break Even : 1:{BREAK_EVEN}")
    logger.info("=" * 60)

    while True:
        try:
            time.sleep(1)

            if mt5.terminal_info() is None:
                logger.error("MT5 terminal not responding — retrying in 5 s")
                time.sleep(5)
                continue

            tick = mt5.symbol_info_tick(SYMBOL)
            if tick is None or tick.ask == 0 or tick.bid == 0:
                logger.warning(f"No valid tick for {SYMBOL} — market may be closed")
                time.sleep(5)
                continue

            currently_open = _on_tick(state, tick)

            rates = get_rates()
            if rates is None:
                continue

            if not is_new_candle(rates, state):
                continue

            _on_new_candle(rates, state, tick, currently_open)

        except KeyboardInterrupt:
            logger.info("Bot stopped by user (Ctrl+C)")
            break

        except Exception as exc:
            logger.error(f"Unhandled error: {exc}", exc_info=True)
            time.sleep(5)
