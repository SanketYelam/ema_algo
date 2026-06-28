"""
mt5_connection.py — MT5 terminal connection management.
"""
import MetaTrader5 as mt5

import config
from logger import logger


def connect_mt5() -> bool:
    """Initialize the MT5 terminal and log in to the broker account."""
    if not mt5.initialize():
        logger.error(f"mt5.initialize() failed | {mt5.last_error()}")
        return False

    if not mt5.login(login=config.LOGIN, password=config.PASSWORD, server=config.SERVER):
        logger.error(f"MT5 login failed | {mt5.last_error()}")
        mt5.shutdown()
        return False

    account = mt5.account_info()
    logger.info(f"MT5 Connected | Account: {account.login} | Balance: {account.balance} {account.currency}")
    return True


def disconnect_mt5() -> None:
    """Shut down the MT5 terminal connection."""
    mt5.shutdown()
    logger.info("MT5 Disconnected")
