"""
logger.py — Application-wide logger.

All modules import `logger` from here and call logger.info() / logger.error() etc.
Using Python's built-in logging module gives us proper log levels, consistent
formatting, and easy future extensibility (file handlers, external services).
"""
import logging
import sys


def _build_logger() -> logging.Logger:
    log = logging.getLogger("EMABot")
    log.setLevel(logging.DEBUG)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter(
            fmt="[%(asctime)s]  %(levelname)-8s  %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    log.addHandler(handler)
    return log


logger = _build_logger()
