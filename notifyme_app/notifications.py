"""
Notification management for the NotifyMe application.

This module handles displaying Windows toast notifications for different
reminder types with appropriate messages and sound settings.
"""

import logging
import random
import time

from PIL import Image
from winotify import Notification, audio

from notifyme_app.constants import (
    APP_NAME,
    APP_REMINDER_APP_ID,
    REMINDER_MESSAGES,
    REMINDER_TITLES,
)
from notifyme_app.utils import format_elapsed, get_resource_path


class NotificationManager:
    """Manages toast notifications for reminders."""

    def __init__(self):
        """Initialize the notification manager."""
        self.icon_file = get_resource_path("icon.png")
        self.icon_file_ico = get_resource_path("icon.ico")
        self._ensure_ico_exists()

    def _ensure_ico_exists(self) -> None:
        """Ensure an .ico icon exists for toast notifications."""
        if not self.icon_file_ico.exists() and self.icon_file.exists():
            try:
                img = Image.open(self.icon_file)
                img.save(self.icon_file_ico, format="ICO")
                logging.info("Created icon.ico from %s", self.icon_file.name)
            except Exception as e:
                logging.error("Failed to create .ico file: %s", e)

    def _get_icon_path(self):
        """Get the path to the notification icon."""
        if self.icon_file_ico.exists():
            return str(self.icon_file_ico)
        elif self.icon_file.exists():
            return str(self.icon_file)
        return None

    def show_notification(
        self,
        title: str,
        messages: list[str],
        last_shown_at=None,
        sound_enabled: bool = False,
    ) -> str:
        """Display a Windows toast notification for a reminder."""
        message = random.choice(messages)  # noqa: S311
        if last_shown_at:
            elapsed = max(0, time.time() - last_shown_at)
            message = f"{message}\nLast reminder: {format_elapsed(elapsed)} ago."

        try:
            icon_path = self._get_icon_path()
            logging.info("Showing notification: %s", message)

            # Create notification using winotify
            toast_args = {
                "app_id": APP_REMINDER_APP_ID,
                "title": title,
                "msg": message,
            }
            if icon_path:
                toast_args["icon"] = icon_path

            toast = Notification(**toast_args)

            # Set audio based on sound settings. Default is silent.
            if sound_enabled:
                toast.set_audio(audio.Default, loop=False)

            toast.show()
            # Return the selected message so callers can optionally use it (e.g. for TTS)
            return message
        except Exception as e:
            logging.error("Error showing notification: %s", e)
            return message

    def show_reminder_notification(
        self,
        reminder_type: str,
        last_shown_at=None,
        sound_enabled: bool = False,
    ) -> str:
        """Display a reminder notification for the specified reminder type."""
        title = REMINDER_TITLES.get(reminder_type, "Reminder")
        messages = REMINDER_MESSAGES.get(reminder_type, ["Time for a reminder"])

        if (
            reminder_type not in REMINDER_TITLES
            or reminder_type not in REMINDER_MESSAGES
        ):
            logging.warning("Unknown reminder type for notification: %s", reminder_type)

        return self.show_notification(title, messages, last_shown_at, sound_enabled)

    def show_update_notification(self, latest_version: str) -> None:
        """Show a toast notification for an available app update."""
        try:
            message = f"{APP_NAME} {latest_version} is available. Open the tray menu to update."
            toast = Notification(
                app_id=APP_REMINDER_APP_ID,
                title="Update Available",
                msg=message,
            )
            toast.set_audio(audio.Default, loop=False)
            toast.show()
        except Exception as e:
            logging.error("Error showing update notification: %s", e)

    def show_welcome_notification(self) -> None:
        """Show a welcome notification when the app starts."""
        try:
            icon_path = self._get_icon_path()

            message = (
                f"{APP_NAME} is now installed and running in your system tray!\n"
                "Right-click the tray icon to access controls and settings.\n"
                "Reminders are enabled and ready to help you stay healthy."
            )

            toast_args = {
                "app_id": APP_REMINDER_APP_ID,
                "title": f"🎉 Welcome to {APP_NAME}!",
                "msg": message,
            }
            if icon_path:
                toast_args["icon"] = icon_path

            toast = Notification(**toast_args)
            toast.set_audio(audio.Default, loop=False)
            toast.show()

            logging.info("Showed welcome notification")
        except Exception as e:
            logging.error("Error showing welcome notification: %s", e)
