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
    REMINDER_WALKING,
    REMINDER_WATER,
    ConfigKeys,
)
from notifyme_app.utils import get_config_path
from notifyme_app.utils import get_idle_seconds as _get_idle_seconds

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

        self.next_reminder_time_map = {
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

    # Properties for backward compatibility with individual interval minute attributes
    @property
    def blink_interval_minutes(self) -> int:
        return self.interval_minutes_map[REMINDER_BLINK]

    @blink_interval_minutes.setter
    def blink_interval_minutes(self, value: int) -> None:
        self.interval_minutes_map[REMINDER_BLINK] = value

    @property
    def walking_interval_minutes(self) -> int:
        return self.interval_minutes_map[REMINDER_WALKING]

    @walking_interval_minutes.setter
    def walking_interval_minutes(self, value: int) -> None:
        self.interval_minutes_map[REMINDER_WALKING] = value

    @property
    def water_interval_minutes(self) -> int:
        return self.interval_minutes_map[REMINDER_WATER]

    @water_interval_minutes.setter
    def water_interval_minutes(self, value: int) -> None:
        self.interval_minutes_map[REMINDER_WATER] = value

    @property
    def pranayama_interval_minutes(self) -> int:
        return self.interval_minutes_map[REMINDER_PRANAYAMA]

    @pranayama_interval_minutes.setter
    def pranayama_interval_minutes(self, value: int) -> None:
        self.interval_minutes_map[REMINDER_PRANAYAMA] = value

    # Properties for backward compatibility with individual pause state attributes
    @property
    def is_blink_paused(self) -> bool:
        return self.is_paused_map[REMINDER_BLINK]

    @is_blink_paused.setter
    def is_blink_paused(self, value: bool) -> None:
        self.is_paused_map[REMINDER_BLINK] = value

    @property
    def is_walking_paused(self) -> bool:
        return self.is_paused_map[REMINDER_WALKING]

    @is_walking_paused.setter
    def is_walking_paused(self, value: bool) -> None:
        self.is_paused_map[REMINDER_WALKING] = value

    @property
    def is_water_paused(self) -> bool:
        return self.is_paused_map[REMINDER_WATER]

    @is_water_paused.setter
    def is_water_paused(self, value: bool) -> None:
        self.is_paused_map[REMINDER_WATER] = value

    @property
    def is_pranayama_paused(self) -> bool:
        return self.is_paused_map[REMINDER_PRANAYAMA]

    @is_pranayama_paused.setter
    def is_pranayama_paused(self, value: bool) -> None:
        self.is_paused_map[REMINDER_PRANAYAMA] = value

    # Properties for backward compatibility with individual offset attributes
    @property
    def blink_offset_seconds(self) -> int:
        return self.offset_seconds_map[REMINDER_BLINK]

    @blink_offset_seconds.setter
    def blink_offset_seconds(self, value: int) -> None:
        self.offset_seconds_map[REMINDER_BLINK] = value

    @property
    def walking_offset_seconds(self) -> int:
        return self.offset_seconds_map[REMINDER_WALKING]

    @walking_offset_seconds.setter
    def walking_offset_seconds(self, value: int) -> None:
        self.offset_seconds_map[REMINDER_WALKING] = value

    @property
    def water_offset_seconds(self) -> int:
        return self.offset_seconds_map[REMINDER_WATER]

    @water_offset_seconds.setter
    def water_offset_seconds(self, value: int) -> None:
        self.offset_seconds_map[REMINDER_WATER] = value

    @property
    def pranayama_offset_seconds(self) -> int:
        return self.offset_seconds_map[REMINDER_PRANAYAMA]

    @pranayama_offset_seconds.setter
    def pranayama_offset_seconds(self, value: int) -> None:
        self.offset_seconds_map[REMINDER_PRANAYAMA] = value

    # Properties for backward compatibility with individual next reminder time attributes
    @property
    def next_reminder_time(self):
        return self.next_reminder_time_map[REMINDER_BLINK]

    @next_reminder_time.setter
    def next_reminder_time(self, value) -> None:
        self.next_reminder_time_map[REMINDER_BLINK] = value

    @property
    def next_walking_reminder_time(self):
        return self.next_reminder_time_map[REMINDER_WALKING]

    @next_walking_reminder_time.setter
    def next_walking_reminder_time(self, value) -> None:
        self.next_reminder_time_map[REMINDER_WALKING] = value

    @property
    def next_water_reminder_time(self):
        return self.next_reminder_time_map[REMINDER_WATER]

    @next_water_reminder_time.setter
    def next_water_reminder_time(self, value) -> None:
        self.next_reminder_time_map[REMINDER_WATER] = value

    @property
    def next_pranayama_reminder_time(self):
        return self.next_reminder_time_map[REMINDER_PRANAYAMA]

    @next_pranayama_reminder_time.setter
    def next_pranayama_reminder_time(self, value) -> None:
        self.next_reminder_time_map[REMINDER_PRANAYAMA] = value

    # Properties for backward compatibility with individual idle suppression attributes
    @property
    def _blink_idle_suppressed(self) -> bool:
        return self.idle_suppressed_map[REMINDER_BLINK]

    @_blink_idle_suppressed.setter
    def _blink_idle_suppressed(self, value: bool) -> None:
        self.idle_suppressed_map[REMINDER_BLINK] = value

    @property
    def _walking_idle_suppressed(self) -> bool:
        return self.idle_suppressed_map[REMINDER_WALKING]

    @_walking_idle_suppressed.setter
    def _walking_idle_suppressed(self, value: bool) -> None:
        self.idle_suppressed_map[REMINDER_WALKING] = value

    @property
    def _water_idle_suppressed(self) -> bool:
        return self.idle_suppressed_map[REMINDER_WATER]

    @_water_idle_suppressed.setter
    def _water_idle_suppressed(self, value: bool) -> None:
        self.idle_suppressed_map[REMINDER_WATER] = value

    @property
    def _pranayama_idle_suppressed(self) -> bool:
        return self.idle_suppressed_map[REMINDER_PRANAYAMA]

    @_pranayama_idle_suppressed.setter
    def _pranayama_idle_suppressed(self, value: bool) -> None:
        self.idle_suppressed_map[REMINDER_PRANAYAMA] = value

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

    def set_blink_interval(self, minutes: int):
        """Set the interval for eye blink reminders."""

        def _set():
            self.blink_interval_minutes = minutes
            self.config[ConfigKeys.BLINK_INTERVAL_MINUTES] = minutes

        return _set

    def set_walking_interval(self, minutes: int):
        """Set the interval for walking reminders."""

        def _set():
            self.walking_interval_minutes = minutes
            self.config[ConfigKeys.WALKING_INTERVAL_MINUTES] = minutes

        return _set

    def set_water_interval(self, minutes: int):
        """Set the interval for water reminders."""

        def _set():
            self.water_interval_minutes = minutes
            self.config[ConfigKeys.WATER_INTERVAL_MINUTES] = minutes

        return _set

    def set_pranayama_interval(self, minutes: int):
        """Set the interval for pranayama reminders."""

        def _set():
            self.pranayama_interval_minutes = minutes
            self.config[ConfigKeys.PRANAYAMA_INTERVAL_MINUTES] = minutes

        return _set

    # Generic interval setting method using dictionary

    def _set_reminder_interval(self, reminder_type: str, minutes: int):
        """Set interval for a specific reminder type.

        Returns a callable for use as a menu callback.
        """
        # Mapping of reminder type to config key
        config_key_map = {
            REMINDER_BLINK: ConfigKeys.BLINK_INTERVAL_MINUTES,
            REMINDER_WALKING: ConfigKeys.WALKING_INTERVAL_MINUTES,
            REMINDER_WATER: ConfigKeys.WATER_INTERVAL_MINUTES,
            REMINDER_PRANAYAMA: ConfigKeys.PRANAYAMA_INTERVAL_MINUTES,
        }

        def _set():
            if reminder_type in self.interval_minutes_map:
                self.interval_minutes_map[reminder_type] = minutes
                self.config[config_key_map[reminder_type]] = minutes

        return _set

    def start_reminders(self) -> None:
        """Start all reminder timers."""
        self.is_running = True
        self.is_paused = False
        threading.Thread(target=self.timer_worker, daemon=True).start()
        threading.Thread(target=self.walking_timer_worker, daemon=True).start()
        threading.Thread(target=self.water_timer_worker, daemon=True).start()
        threading.Thread(target=self.pranayama_timer_worker, daemon=True).start()

    def pause_reminders(self) -> None:
        """Pause all reminder timers."""
        self.is_paused = True

    def resume_reminders(self) -> None:
        """Resume all reminder timers."""
        self.is_paused = False
        for reminder_type in self.is_paused_map:
            self.is_paused_map[reminder_type] = False

    def toggle_blink_pause(self) -> None:
        """Toggle pause state for eye blink reminders."""
        self.is_blink_paused = not self.is_blink_paused

    def toggle_walking_pause(self) -> None:
        """Toggle pause state for walking reminders."""
        self.is_walking_paused = not self.is_walking_paused

    def toggle_water_pause(self) -> None:
        """Toggle pause state for water reminders."""
        self.is_water_paused = not self.is_water_paused

    def toggle_pranayama_pause(self) -> None:
        """Toggle pause state for pranayama reminders."""
        self.is_pranayama_paused = not self.is_pranayama_paused

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
        subprocess.run(
            ["explorer", "/select,", str(APP_DATA_DIR / "notifyme.log")], check=False
        )

    def open_exe_location(self) -> None:
        """Open the folder containing the executable."""
        subprocess.run(["explorer", "/select,", str(Path(sys.executable))], check=False)

    def open_config_location(self) -> None:
        """Open the folder containing the configuration file."""
        subprocess.run(["explorer", "/select,", str(self.config_file)], check=False)

    def open_help(self) -> None:
        """Open the help documentation in the default web browser."""
        help_dir = get_resource_path("help")
        webbrowser.open(str(help_dir / "index.html"))

    def update_icon_title(self) -> None:
        """Update the system tray icon title based on current state."""
        if not self.icon:
            return
        if self.is_paused:
            self.icon.title = f"{APP_NAME} - All Paused"
            return

        status_parts = []
        reminder_labels = {
            REMINDER_BLINK: "Blink",
            REMINDER_WALKING: "Walk",
            REMINDER_WATER: "Water",
            REMINDER_PRANAYAMA: "Pranayama",
        }

        for reminder_type, label in reminder_labels.items():
            is_paused = self.is_paused_map[reminder_type]
            status = (
                "⏸" if is_paused else f"{self.interval_minutes_map[reminder_type]}min"
            )
            status_parts.append(f"{label}: {status}")

        self.icon.title = ", ".join(status_parts)

    def get_initial_title(self) -> str:
        """Get the initial title for the system tray icon."""
        return (
            f"Blink: {self.interval_minutes_map[REMINDER_BLINK]}min, "
            f"Walk: {self.interval_minutes_map[REMINDER_WALKING]}min, "
            f"Water: {self.interval_minutes_map[REMINDER_WATER]}min, "
            f"Pranayama: {self.interval_minutes_map[REMINDER_PRANAYAMA]}min"
        )

    def show_notification(self, title: str, messages: Iterable[str]) -> None:
        """Show a notification with the given title and messages."""
        message = next(iter(messages), "")
        toast = Notification(app_id=APP_REMINDER_APP_ID, title=title, msg=message)
        toast.set_audio(audio.Default, loop=False)
        toast.show()

    def show_reminder_notification(self, reminder_type: str) -> None:
        """Show a notification for a specific reminder type."""
        notifications = {
            REMINDER_BLINK: ("Eye Blink Reminder", ["Blink now"]),
            REMINDER_WALKING: ("Walking Reminder", ["Time to walk"]),
            REMINDER_WATER: ("Water Reminder", ["Drink water"]),
            REMINDER_PRANAYAMA: ("Pranayama Reminder", ["Breathe"]),
        }
        title, messages = notifications.get(reminder_type, ("Reminder", ["Reminder"]))
        self.show_notification(title, messages)

    def show_blink_notification(self) -> None:
        """Show a notification for eye blink reminders."""
        self.show_reminder_notification(REMINDER_BLINK)

    def show_walking_notification(self) -> None:
        """Show a notification for walking reminders."""
        self.show_reminder_notification(REMINDER_WALKING)

    def show_water_notification(self) -> None:
        """Show a notification for water reminders."""
        self.show_reminder_notification(REMINDER_WATER)

    def show_pranayama_notification(self) -> None:
        """Show a notification for pranayama reminders."""
        self.show_reminder_notification(REMINDER_PRANAYAMA)

    def create_icon_image(self):
        """Load and return the icon image for the system tray."""
        return Image.open(self.icon_file).resize((64, 64))

    def create_menu(self):
        """Create and return the menu for the system tray icon."""
        return Menu(MenuItem("❓ Help", self.open_help))

    def _timer_loop(
        self,
        interval_minutes: int,
        offset_seconds: int,
        paused_attr: str,
        next_time_attr: str,
        idle_suppressed_attr: str,
        show_callback,
    ) -> None:
        while self.is_running:
            if self.is_paused or getattr(self, paused_attr):
                time.sleep(1)
                continue

            now = time.time()
            interval_seconds = int(interval_minutes * 60)
            idle_seconds = get_idle_seconds()

            if idle_seconds is not None and idle_seconds >= interval_seconds:
                setattr(self, idle_suppressed_attr, True)
                setattr(self, next_time_attr, now + idle_seconds)
                time.sleep(1)
                continue

            next_time = getattr(self, next_time_attr)
            if next_time is None:
                setattr(self, next_time_attr, now + interval_seconds + offset_seconds)
                time.sleep(1)
                continue

            if now >= next_time:
                show_callback()
                setattr(self, next_time_attr, now + interval_seconds)
                setattr(self, idle_suppressed_attr, False)

            time.sleep(1)

    def timer_worker(self) -> None:
        """Worker thread for eye blink reminders."""
        self._timer_loop(
            self.blink_interval_minutes,
            self.blink_offset_seconds,
            "is_blink_paused",
            "next_reminder_time",
            "_blink_idle_suppressed",
            self.show_blink_notification,
        )

    def walking_timer_worker(self) -> None:
        """Worker thread for walking reminders."""
        self._timer_loop(
            self.walking_interval_minutes,
            self.walking_offset_seconds,
            "is_walking_paused",
            "next_walking_reminder_time",
            "_walking_idle_suppressed",
            self.show_walking_notification,
        )

    def water_timer_worker(self) -> None:
        """Worker thread for water reminders."""
        self._timer_loop(
            self.water_interval_minutes,
            self.water_offset_seconds,
            "is_water_paused",
            "next_water_reminder_time",
            "_water_idle_suppressed",
            self.show_water_notification,
        )

    def pranayama_timer_worker(self) -> None:
        """Worker thread for pranayama reminders."""
        self._timer_loop(
            self.pranayama_interval_minutes,
            self.pranayama_offset_seconds,
            "is_pranayama_paused",
            "next_pranayama_reminder_time",
            "_pranayama_idle_suppressed",
            self.show_pranayama_notification,
        )


def setup_logging():
    """Set up logging with rotating file handler."""
    app_data_dir = get_app_data_dir()
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    handler = RotatingFileHandler(
        app_data_dir / "notifyme.log",
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
