"""
main.py — Entry point for the EMA 9/12 Crossover Trading Bot.
"""
from logger import logger
from mt5_connection import connect_mt5, disconnect_mt5
from strategy import run_strategy

if __name__ == "__main__":
    if connect_mt5():
        try:
            run_strategy()
        finally:
            disconnect_mt5()
    else:
        logger.error("Failed to connect to MT5. Check your .env file.")
