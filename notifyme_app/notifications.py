"""
Notification management for the NotifyMe application.

This module handles displaying Windows toast notifications for different
reminder types with appropriate messages and sound settings.
"""

import random
import sys
import time

from PIL import Image
try:
    from plyer import notification as plyer_notification
except Exception:
    plyer_notification = None

try:
    if sys.platform == "win32":
        from winotify import Notification, audio
    else:
        Notification = None
        audio = None
except Exception:
    Notification = None
    audio = None

from notifyme_app.constants import (
    APP_NAME,
    APP_REMINDER_APP_ID,
    REMINDER_MESSAGES,
    REMINDER_TITLES,
)
from notifyme_app.logger import get_logger
from notifyme_app.utils import format_elapsed, get_resource_path


class NotificationManager:
    """Manages toast notifications for reminders."""

    def __init__(self):
        """Initialize the notification manager."""
        self.logger = get_logger(__name__)
        self.icon_file = get_resource_path("icon.png")
        self.icon_file_ico = get_resource_path("icon.ico")
        if self.supports_actions:
            self._ensure_ico_exists()

    @property
    def is_windows_toast_supported(self) -> bool:
        """Return whether winotify-backed Windows toasts are available."""
        return sys.platform == "win32" and Notification is not None

    @property
    def supports_actions(self) -> bool:
        """Return whether the active notification backend supports actions."""
        return self.is_windows_toast_supported

    def _ensure_ico_exists(self) -> None:
        """Ensure an .ico icon exists for toast notifications."""
        if not self.icon_file_ico.exists() and self.icon_file.exists():
            try:
                img = Image.open(self.icon_file)
                img.save(self.icon_file_ico, format="ICO")
                self.logger.info("Created icon.ico from %s", self.icon_file.name)
            except Exception as e:
                self.logger.error("Failed to create .ico file: %s", e)

    def get_icon_path(self):
        """Get the path to the notification icon."""
        if self.is_windows_toast_supported and self.icon_file_ico.exists():
            return str(self.icon_file_ico)
        if self.icon_file.exists():
            return str(self.icon_file)
        return None

    def _notify(
        self,
        title: str,
        message: str,
        *,
        sound_enabled: bool = False,
        launch: str | None = None,
        action_label: str | None = None,
    ) -> None:
        """Show a notification using the active backend."""
        icon_path = self.get_icon_path()

        if self.is_windows_toast_supported:
            toast_args = {
                "app_id": APP_REMINDER_APP_ID,
                "title": title,
                "msg": message,
            }
            if icon_path:
                toast_args["icon"] = icon_path

            toast = Notification(**toast_args)
            if sound_enabled and audio is not None:
                toast.set_audio(audio.Default, loop=False)
            if launch and action_label:
                toast.add_actions(label=action_label, launch=launch)
            toast.show()
            return

        if plyer_notification is not None:
            plyer_notification.notify(
                title=title,
                message=message,
                app_name=APP_NAME,
                app_icon=icon_path,
                timeout=10,
            )
            return

        self.logger.warning("No notification backend available for platform %s", sys.platform)

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
            self.logger.info("Showing notification: %s", message)
            self._notify(title, message, sound_enabled=sound_enabled)
            # Return the selected message so callers can optionally use it (e.g. for TTS)
            return message
        except Exception as e:
            self.logger.error("Error showing notification: %s", e)
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
            self.logger.warning(
                "Unknown reminder type for notification: %s", reminder_type
            )

        return self.show_notification(title, messages, last_shown_at, sound_enabled)

    def show_update_notification(self, latest_version: str) -> None:
        """Show a toast notification for an available app update."""
        try:
            message = f"{APP_NAME} {latest_version} is available. Open the tray menu to update."
            self._notify("Update Available", message, sound_enabled=True)
        except Exception as e:
            self.logger.error("Error showing update notification: %s", e)

    def show_welcome_notification(self) -> None:
        """Show a welcome notification when the app starts."""
        try:
            message = (
                f"{APP_NAME} is now installed and running in your system tray!\n"
                "Right-click the tray icon to access controls and settings.\n"
                "Reminders are enabled and ready to help you stay healthy."
            )
            self._notify(f"Welcome to {APP_NAME}!", message, sound_enabled=True)

            self.logger.info("Showed welcome notification")
        except Exception as e:
            self.logger.error("Error showing welcome notification: %s", e)

    def show_action_notification(
        self,
        title: str,
        message: str,
        *,
        action_label: str,
        launch: str,
        sound_enabled: bool = False,
    ) -> None:
        """Show a notification and attach an action when supported."""
        self._notify(
            title,
            message,
            sound_enabled=sound_enabled,
            action_label=action_label if self.supports_actions else None,
            launch=launch if self.supports_actions else None,
        )
