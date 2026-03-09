"""
Centralized logging configuration for the NotifyMe application.
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from notifyme_app.utils import get_log_file_path


def setup_logging(log_file: Path | None = None) -> None:
    """Set up logging with rotating file handler and console output."""
    if log_file is None:
        log_file = get_log_file_path()

    # Check for debug flag
    is_debug = "--debug" in sys.argv
    level = logging.DEBUG if is_debug else logging.INFO

    logger = logging.getLogger()
    logger.setLevel(level)

    # Prevent adding handlers multiple times if setup_logging is called again
    if logger.handlers:
        # If already set up, but we want to change level (e.g. if root set it)
        # we don't do anything here as it's already configured.
        return

    # File handler
    try:
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=5 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8",
        )
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(level)
        logger.addHandler(file_handler)
    except Exception as e:
        print(f"Failed to set up file logging: {e}", file=sys.stderr)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_formatter = logging.Formatter(
        "%(levelname)s: %(message)s",
    )
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(level)
    logger.addHandler(console_handler)


def shutdown_logging() -> None:
    """Properly shutdown logging handlers."""
    logger = logging.getLogger()
    for handler in logger.handlers[:]:
        handler.flush()
        handler.close()
        logger.removeHandler(handler)


def get_logger(name: str) -> logging.Logger:
    """Return a logger instance with the given name."""
    return logging.getLogger(name)
