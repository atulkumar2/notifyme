#!/usr/bin/env python3
"""
NotifyMe - Health reminder application entry point.

This is the main entry point for the NotifyMe application. It sets up
logging and launches the main application.
"""

import logging
from logging.handlers import RotatingFileHandler

from notifyme_app import NotifyMeApp
from notifyme_app.utils import get_app_data_dir


def setup_logging():
    """Set up logging with rotating file handler."""
    # App data directory for logs
    app_data_dir = get_app_data_dir()
    
    # Configure logging with rolling file handler
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Create rotating file handler (5 MB per file, keep up to 5 backups)
    handler = RotatingFileHandler(
        app_data_dir / "notifyme.log",
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=5,
        encoding="utf-8",
    )
    
    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(handler)


def main():
    """Main entry point for the application."""
    setup_logging()
    
    app = NotifyMeApp()
    app.run()


if __name__ == "__main__":
    main()