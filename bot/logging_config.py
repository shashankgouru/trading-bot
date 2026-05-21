# bot/logging_config.py
# -------------------------------------------------------
# Logging Configuration for the Trading Bot
# -------------------------------------------------------
# This module sets up logging for the entire project.
# All other modules import `get_logger()` from here.
#
# Two handlers are configured:
#   1. FileHandler   → writes DEBUG+ logs to logs/trading_bot.log
#   2. StreamHandler → writes WARNING+ logs to the console
#
# This means:
#   - The terminal stays clean (only warnings/errors shown)
#   - The log file captures everything (useful for submission)
# -------------------------------------------------------

import logging
import os
from logging.handlers import RotatingFileHandler

# -------------------------------------------------------
# Constants
# -------------------------------------------------------

# Name of the log file inside the logs/ folder
LOG_FILE = "logs/trading_bot.log"

# Log format: timestamp | level | module name | message
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"

# Timestamp format used in every log line
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging():
    """
    Sets up the root logger with:
      - A file handler (DEBUG level) → logs/trading_bot.log
      - A console handler (WARNING level) → terminal

    Call this ONCE at application startup (inside cli.py).
    All modules then use get_logger(__name__) to get their own logger.
    """

    # Create the logs/ directory if it doesn't exist yet
    # exist_ok=True means no error if it already exists
    os.makedirs("logs", exist_ok=True)

    # Get the root logger — this is the parent of all loggers
    root_logger = logging.getLogger()

    # Set root logger to DEBUG so all messages flow through
    # Individual handlers then filter what they actually write
    root_logger.setLevel(logging.DEBUG)

    # Avoid adding duplicate handlers if setup_logging() is called more than once
    if root_logger.handlers:
        return

    # -------------------------------------------------------
    # Handler 1: File Handler
    # -------------------------------------------------------
    # RotatingFileHandler automatically creates a new log file
    # when the current one reaches maxBytes (1 MB here)
    # backupCount=3 means it keeps the last 3 old log files
    file_handler = RotatingFileHandler(
        filename=LOG_FILE,
        maxBytes=1 * 1024 * 1024,  # 1 MB
        backupCount=3,
        encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)  # Capture everything in file
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))

    # -------------------------------------------------------
    # Handler 2: Console Handler
    # -------------------------------------------------------
    # Only shows WARNING and above in the terminal
    # This keeps the terminal output clean for the user
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)  # Less noise in terminal
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))

    # Attach both handlers to the root logger
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)


def get_logger(name: str) -> logging.Logger:
    """
    Returns a named logger for any module.

    Usage in any other file:
        from bot.logging_config import get_logger
        logger = get_logger(__name__)
        logger.info("This will go to the log file")
        logger.error("This will go to both file and terminal")

    Args:
        name: Typically passed as __name__ so the log shows
              which module generated each message.

    Returns:
        A configured logging.Logger instance.
    """
    return logging.getLogger(name)