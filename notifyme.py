#!/usr/bin/env python3
"""
NotifyMe - Health reminder application entry point and compatibility layer.
"""

import json
import logging
import os
import subprocess
import sys
import threading
import time
import webbrowser
from collections.abc import Iterable
from logging.handlers import RotatingFileHandler
from pathlib import Path

from PIL import Image
from winotify import Notification, audio

from notifyme_app import NotifyMeApp as _RuntimeNotifyMeApp
from notifyme_app.constants import (
    APP_NAME,
    APP_REMINDER_APP_ID,
    APP_VERSION,
    DEFAULT_INTERVALS_MIN,
    REMINDER_BLINK,
    REMINDER_PRANAYAMA,
    REMINDER_TITLES,
    REMINDER_WALKING,
    REMINDER_WATER,
    ConfigKeys,
    ReminderLabels,
)
from notifyme_app.utils import (
    get_config_path,
    get_exe_path,
    get_local_help_path,
    get_log_file_path,
)
from notifyme_app.utils import (
    get_idle_seconds as _get_idle_seconds,
)

try:
    from pystray import Menu as _PystrayMenu
    from pystray import MenuItem as _PystrayMenuItem

    MenuItem = _PystrayMenuItem  # type: ignore[assignment]
    Menu = _PystrayMenu  # type: ignore[assignment]
except Exception:  # pragma: no cover - fallback for environments without pystray

    class MenuItem:  # type: ignore[no-redef]
        """Simple MenuItem class to mimic pystray.MenuItem for environments
        where pystray is unavailable."""

        def __init__(self, text, action=None, **_kwargs):
            self.text = text
            self.action = action

    class Menu:  # type: ignore[no-redef]
        """Simple Menu class to mimic pystray.Menu for environments where pystray is unavailable."""

        def __init__(self, *items):
            self._items = list(items)

        @property
        def items(self):
            """Return menu items."""
            return self._items


__all__ = [
    "NotifyMeApp",
    "APP_VERSION",
    "get_app_data_dir",
    "get_resource_path",
    "get_idle_seconds",
]


def get_app_data_dir() -> Path:
    """Return the per-user app data directory for config and logs."""
    app_data = Path(os.environ.get("APPDATA", Path.home())) / APP_NAME
    app_data.mkdir(parents=True, exist_ok=True)
    return app_data


def get_resource_path(filename: str) -> Path:
    """Return path to a bundled or local resource (PyInstaller compatible)."""
    if getattr(sys, "frozen", False):
        base_path = Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
    else:
        base_path = Path(__file__).parent
    return base_path / filename


def get_idle_seconds() -> float | None:
    """Return system idle time in seconds, or None if unavailable."""
    return _get_idle_seconds()


APP_DATA_DIR = get_app_data_dir()


class NotifyMeApp:
    """Legacy API surface used by the test suite."""

    # pylint: disable-missing-function-docstring, no-self-use, too-many-instance-attributes

    def __init__(self):
        self.is_running = False
        self.is_paused = False

        # Parameterized interval minutes dictionary initialized from constants
        self.interval_minutes_map = DEFAULT_INTERVALS_MIN.copy()

        # Parameterized state dictionaries for all reminder types
        self.is_paused_map = {
            REMINDER_BLINK: False,
            REMINDER_WALKING: False,
            REMINDER_WATER: False,
            REMINDER_PRANAYAMA: False,
        }

        self.offset_seconds_map = {
            REMINDER_BLINK: 0,
            REMINDER_WALKING: 0,
            REMINDER_WATER: 0,
            REMINDER_PRANAYAMA: 0,
        }

        self.next_reminder_time_map: dict[str, float | None] = {
            REMINDER_BLINK: None,
            REMINDER_WALKING: None,
            REMINDER_WATER: None,
            REMINDER_PRANAYAMA: None,
        }

        self.idle_suppressed_map = {
            REMINDER_BLINK: False,
            REMINDER_WALKING: False,
            REMINDER_WATER: False,
            REMINDER_PRANAYAMA: False,
        }

        self.config = self.get_default_config()
        self.config_file = get_config_path()
        self.icon_file = get_resource_path("icon.png")
        self.icon_file_ico = get_resource_path("icon.ico")
        self.icon = None

    def get_default_config(self) -> dict:
        """Return default configuration."""
        return {
            ConfigKeys.BLINK_INTERVAL_MINUTES: 20,
            ConfigKeys.WALKING_INTERVAL_MINUTES: 60,
            ConfigKeys.WATER_INTERVAL_MINUTES: 30,
            ConfigKeys.PRANAYAMA_INTERVAL_MINUTES: 120,
            ConfigKeys.SOUND_ENABLED: False,
        }

    def load_config(self) -> dict:
        """Load configuration from file."""
        if self.config_file.exists():
            return json.loads(self.config_file.read_text(encoding="utf-8"))
        return self.get_default_config()

    def save_config(self) -> None:
        """Save current configuration to file."""
        self.config_file.write_text(json.dumps(self.config, indent=2), encoding="utf-8")

    # Generic interval setting method using dictionary

    def _set_reminder_interval(self, reminder_type: str, minutes: int):
        """Set interval for a specific reminder type.

        Returns a callable for use as a menu callback.
        """

        def _set():
            if reminder_type in self.interval_minutes_map:
                self.interval_minutes_map[reminder_type] = minutes
                config_key = f"{reminder_type}_interval_minutes"
                self.config[config_key] = minutes

        return _set

    def start_reminders(self) -> None:
        """Start all reminder timers."""
        self.is_running = True
        self.is_paused = False
        for reminder_type in self.interval_minutes_map:
            threading.Thread(
                target=self.reminder_timer_worker,
                args=(reminder_type,),
                daemon=True,
            ).start()

    def pause_reminders(self) -> None:
        """Pause all reminder timers."""
        self.is_paused = True

    def resume_reminders(self) -> None:
        """Resume all reminder timers."""
        self.is_paused = False
        for reminder_type in self.is_paused_map:
            self.is_paused_map[reminder_type] = False

    # Generic pause toggle method
    def _toggle_reminder_pause(self, reminder_type: str) -> None:
        """Toggle pause state for a specific reminder type."""
        if reminder_type in self.is_paused_map:
            self.is_paused_map[reminder_type] = not self.is_paused_map[reminder_type]

    def stop_reminders(self) -> None:
        """Stop all reminder timers."""
        self.is_running = False
        self.is_paused = False
        if self.icon is not None:
            try:
                self.icon.stop()
            except Exception:
                pass

    def open_log_location(self) -> None:
        """Open the folder containing the log file."""
        subprocess.run(["explorer", "/select,", str(get_log_file_path())], check=False)

    def open_exe_location(self) -> None:
        """Open the folder containing the executable."""
        subprocess.run(["explorer", "/select,", str(get_exe_path())], check=False)

    def open_config_location(self) -> None:
        """Open the folder containing the configuration file."""
        subprocess.run(["explorer", "/select,", str(self.config_file)], check=False)

    def open_help(self) -> None:
        """Open the help documentation in the default web browser."""
        webbrowser.open(str(get_local_help_path()))

    def update_icon_title(self) -> None:
        """Update the system tray icon title based on current state."""
        if not self.icon:
            return
        if self.is_paused:
            self.icon.title = f"{APP_NAME} - All Paused"
            return

        status_parts = []
        reminder_labels = {
            REMINDER_BLINK: ReminderLabels[REMINDER_BLINK],
            REMINDER_WALKING: ReminderLabels[REMINDER_WALKING],
            REMINDER_WATER: ReminderLabels[REMINDER_WATER],
            REMINDER_PRANAYAMA: ReminderLabels[REMINDER_PRANAYAMA],
        }

        for reminder_type, label in reminder_labels.items():
            is_paused = self.is_paused_map[reminder_type]
            interval_minutes = self.interval_minutes_map[reminder_type]
            status = "⏸" if is_paused else f"{interval_minutes}min"
            status_parts.append(f"{label}: {status}")

        self.icon.title = ", ".join(status_parts)

    def get_initial_title(self) -> str:
        """Get the initial title for the system tray icon."""
        retval = ""
        for reminder_type, label in ReminderLabels.items():
            interval_minutes = self.interval_minutes_map.get(reminder_type, 0)
            retval += f"{label}: {interval_minutes}min, "
        return retval.rstrip(", ")

    def show_notification(self, title: str, messages: Iterable[str]) -> None:
        """Show a notification with the given title and messages."""
        message = next(iter(messages), "")
        toast = Notification(app_id=APP_REMINDER_APP_ID, title=title, msg=message)
        toast.set_audio(audio.Default, loop=False)
        toast.show()

    def show_reminder_notification(self, reminder_type: str) -> None:
        """Show a notification for a specific reminder type."""
        notifications = {
            REMINDER_BLINK: (REMINDER_TITLES[REMINDER_BLINK], ["Blink now"]),
            REMINDER_WALKING: (REMINDER_TITLES[REMINDER_WALKING], ["Time to walk"]),
            REMINDER_WATER: (REMINDER_TITLES[REMINDER_WATER], ["Drink water"]),
            REMINDER_PRANAYAMA: (REMINDER_TITLES[REMINDER_PRANAYAMA], ["Breathe"]),
        }
        title, messages = notifications.get(reminder_type, ("Reminder", ["Reminder"]))
        self.show_notification(title, messages)

    def create_icon_image(self):
        """Load and return the icon image for the system tray."""
        return Image.open(self.icon_file).resize((64, 64))

    def create_menu(self):
        """Create and return the menu for the system tray icon."""
        return Menu(MenuItem("❓ Help", self.open_help))

    def _timer_loop(
        self,
        reminder_type: str,
        show_callback,
    ) -> None:
        while self.is_running:
            if self.is_paused or self.is_paused_map.get(reminder_type, False):
                time.sleep(1)
                continue

            now = time.time()
            interval_minutes = self.interval_minutes_map[reminder_type]
            offset_seconds = self.offset_seconds_map[reminder_type]
            interval_seconds = int(interval_minutes * 60)
            idle_seconds = get_idle_seconds()

            if idle_seconds is not None and idle_seconds >= interval_seconds:
                self.idle_suppressed_map[reminder_type] = True
                self.next_reminder_time_map[reminder_type] = now + idle_seconds
                time.sleep(1)
                continue

            next_time = self.next_reminder_time_map.get(reminder_type)
            if next_time is None:
                self.next_reminder_time_map[reminder_type] = (
                    now + interval_seconds + offset_seconds
                )
                time.sleep(1)
                continue

            if now >= next_time:
                show_callback()
                self.next_reminder_time_map[reminder_type] = now + interval_seconds
                self.idle_suppressed_map[reminder_type] = False

            time.sleep(1)

    def reminder_timer_worker(self, reminder_type: str) -> None:
        """Worker thread for a specific reminder type."""
        if reminder_type not in self.interval_minutes_map:
            logging.warning("Unknown reminder type for timer worker: %s", reminder_type)
            return

        self._timer_loop(
            reminder_type,
            lambda: self.show_reminder_notification(reminder_type),
        )


def setup_logging():
    """Set up logging with rotating file handler."""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    handler = RotatingFileHandler(
        get_log_file_path(),
        maxBytes=5 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def main():
    """Main entry point for the application."""
    setup_logging()
    app = _RuntimeNotifyMeApp()
    app.run()


if __name__ == "__main__":
    main()
