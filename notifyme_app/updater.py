"""
Update checking functionality for the NotifyMe application.

This module handles checking for application updates from GitHub releases
and managing update notifications.
"""

import json
import logging
import threading
from datetime import datetime, timezone
from urllib.request import Request, urlopen
from typing import Optional, Callable

from notifyme_app.constants import (
    APP_VERSION,
    GITHUB_RELEASES_API_URL,
    UPDATE_CHECK_TIMEOUT_SECONDS,
)
from notifyme_app.utils import parse_version


class UpdateChecker:
    """Manages application update checking and notifications."""

    def __init__(self, update_callback: Optional[Callable[[str], None]] = None):
        """Initialize the update checker.

        Args:
            update_callback: Optional callback to call when update is available
        """
        self.update_callback = update_callback
        self.update_available = False
        self.latest_version: Optional[str] = None
        self.last_update_check_at: Optional[datetime] = None

    def get_current_version(self) -> str:
        """Return the current application version string."""
        return APP_VERSION

    def check_for_updates(self) -> None:
        """Check GitHub releases to see if a newer version is available."""
        try:
            req = Request(
                GITHUB_RELEASES_API_URL,
                headers={"User-Agent": "NotifyMe"},
            )
            with urlopen(req, timeout=UPDATE_CHECK_TIMEOUT_SECONDS) as resp:
                payload = resp.read().decode("utf-8")

            data = json.loads(payload)
            tag = data.get("tag_name") or data.get("name")
            if not tag:
                return

            latest = str(tag).strip().lstrip("v")
            current = self.get_current_version()

            if parse_version(latest) > parse_version(current):
                self.update_available = True
                self.latest_version = latest
                logging.info("Update available: %s (current: %s)", latest, current)

                # Call update callback if provided
                if self.update_callback:
                    self.update_callback(latest)
            else:
                self.update_available = False
                self.latest_version = latest
                logging.info("No update available (current: %s)", current)

        except Exception as e:
            logging.error("Failed to check for updates: %s", e)
        finally:
            self.last_update_check_at = datetime.now(timezone.utc)

    def check_for_updates_async(self) -> None:
        """Run update check in a background thread."""
        thread = threading.Thread(target=self.check_for_updates, daemon=True)
        thread.start()

    def is_update_available(self) -> bool:
        """Check if an update is available."""
        return self.update_available

    def get_latest_version(self) -> Optional[str]:
        """Get the latest available version."""
        return self.latest_version

    def get_last_check_time(self) -> Optional[datetime]:
        """Get the timestamp of the last update check."""
        return self.last_update_check_at
