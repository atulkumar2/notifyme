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
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Iterable

from winotify import Notification, audio

from notifyme_app import NotifyMeApp as _RuntimeNotifyMeApp
from notifyme_app.constants import APP_VERSION
from notifyme_app.utils import get_idle_seconds as _get_idle_seconds

try:
    from pystray import Menu, MenuItem
except Exception:  # pragma: no cover - fallback for environments without pystray
    class MenuItem:  # type: ignore[override]
        def __init__(self, text, action=None, **_kwargs):
            self.text = text
            self.action = action

    class Menu:  # type: ignore[override]
        def __init__(self, *items):
            self._items = list(items)

        @property
        def items(self):
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
    app_data = Path(os.environ.get("APPDATA", Path.home())) / "NotifyMe"
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

    def __init__(self):
        self.interval_minutes = 20
        self.walking_interval_minutes = 60
        self.water_interval_minutes = 30
        self.pranayama_interval_minutes = 120

        self.is_running = False
        self.is_paused = False
        self.is_blink_paused = False
        self.is_walking_paused = False
        self.is_water_paused = False
        self.is_pranayama_paused = False

        self.blink_offset_seconds = 0
        self.walking_offset_seconds = 0
        self.water_offset_seconds = 0
        self.pranayama_offset_seconds = 0

        self.next_reminder_time = None
        self.next_walking_reminder_time = None
        self.next_water_reminder_time = None
        self.next_pranayama_reminder_time = None

        self._blink_idle_suppressed = False
        self._walking_idle_suppressed = False
        self._water_idle_suppressed = False
        self._pranayama_idle_suppressed = False

        self.config = self.get_default_config()
        self.config_file = APP_DATA_DIR / "config.json"
        self.icon_file = get_resource_path("icon.png")
        self.icon_file_ico = get_resource_path("icon.ico")
        self.icon = None

    def get_default_config(self) -> dict:
        return {
            "interval_minutes": 20,
            "walking_interval_minutes": 60,
            "water_interval_minutes": 30,
            "pranayama_interval_minutes": 120,
            "sound_enabled": False,
        }

    def load_config(self) -> dict:
        if self.config_file.exists():
            return json.loads(self.config_file.read_text(encoding="utf-8"))
        return self.get_default_config()

    def save_config(self) -> None:
        self.config_file.write_text(json.dumps(self.config, indent=2), encoding="utf-8")

    def set_interval(self, minutes: int):
        def _set():
            self.interval_minutes = minutes
            self.config["interval_minutes"] = minutes
        return _set

    def set_walking_interval(self, minutes: int):
        def _set():
            self.walking_interval_minutes = minutes
            self.config["walking_interval_minutes"] = minutes
        return _set

    def set_water_interval(self, minutes: int):
        def _set():
            self.water_interval_minutes = minutes
            self.config["water_interval_minutes"] = minutes
        return _set

    def set_pranayama_interval(self, minutes: int):
        def _set():
            self.pranayama_interval_minutes = minutes
            self.config["pranayama_interval_minutes"] = minutes
        return _set

    def start_reminders(self) -> None:
        self.is_running = True
        self.is_paused = False
        threading.Thread(target=self.timer_worker, daemon=True).start()
        threading.Thread(target=self.walking_timer_worker, daemon=True).start()
        threading.Thread(target=self.water_timer_worker, daemon=True).start()
        threading.Thread(target=self.pranayama_timer_worker, daemon=True).start()

    def pause_reminders(self) -> None:
        self.is_paused = True

    def resume_reminders(self) -> None:
        self.is_paused = False
        self.is_blink_paused = False
        self.is_walking_paused = False
        self.is_water_paused = False
        self.is_pranayama_paused = False

    def toggle_blink_pause(self) -> None:
        self.is_blink_paused = not self.is_blink_paused

    def toggle_walking_pause(self) -> None:
        self.is_walking_paused = not self.is_walking_paused

    def toggle_water_pause(self) -> None:
        self.is_water_paused = not self.is_water_paused

    def toggle_pranayama_pause(self) -> None:
        self.is_pranayama_paused = not self.is_pranayama_paused

    def stop_reminders(self) -> None:
        self.is_running = False
        self.is_paused = False
        if self.icon is not None:
            try:
                self.icon.stop()
            except Exception:
                pass

    def open_log_location(self) -> None:
        subprocess.run(["explorer", "/select,", str(APP_DATA_DIR / "notifyme.log")])

    def open_exe_location(self) -> None:
        subprocess.run(["explorer", "/select,", str(Path(sys.executable))])

    def open_config_location(self) -> None:
        subprocess.run(["explorer", "/select,", str(self.config_file)])

    def open_help(self) -> None:
        help_dir = get_resource_path("help")
        webbrowser.open(str(help_dir / "index.html"))

    def update_icon_title(self) -> None:
        if not self.icon:
            return
        if self.is_paused:
            self.icon.title = "NotifyMe - All Paused"
            return

        blink_status = "⏸" if self.is_blink_paused else f"{self.interval_minutes}min"
        walk_status = "⏸" if self.is_walking_paused else f"{self.walking_interval_minutes}min"
        water_status = "⏸" if self.is_water_paused else f"{self.water_interval_minutes}min"
        pranayama_status = (
            "⏸" if self.is_pranayama_paused else f"{self.pranayama_interval_minutes}min"
        )
        self.icon.title = (
            f"Blink: {blink_status}, Walk: {walk_status}, "
            f"Water: {water_status}, Pranayama: {pranayama_status}"
        )

    def get_initial_title(self) -> str:
        return (
            f"Blink: {self.interval_minutes}min, Walk: {self.walking_interval_minutes}min, "
            f"Water: {self.water_interval_minutes}min, Pranayama: {self.pranayama_interval_minutes}min"
        )

    def show_notification(self, title: str, messages: Iterable[str]) -> None:
        message = next(iter(messages), "")
        toast = Notification(app_id="NotifyMe Reminder", title=title, msg=message)
        toast.set_audio(audio.Default, loop=False)
        toast.show()

    def show_blink_notification(self) -> None:
        self.show_notification("Eye Blink Reminder", ["Blink now"])

    def show_walking_notification(self) -> None:
        self.show_notification("Walking Reminder", ["Time to walk"])

    def show_water_notification(self) -> None:
        self.show_notification("Water Reminder", ["Drink water"])

    def show_pranayama_notification(self) -> None:
        self.show_notification("Pranayama Reminder", ["Breathe"])

    def create_icon_image(self):
        from PIL import Image
        return Image.open(self.icon_file).resize((64, 64))

    def create_menu(self):
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
        self._timer_loop(
            self.interval_minutes,
            self.blink_offset_seconds,
            "is_blink_paused",
            "next_reminder_time",
            "_blink_idle_suppressed",
            self.show_blink_notification,
        )

    def walking_timer_worker(self) -> None:
        self._timer_loop(
            self.walking_interval_minutes,
            self.walking_offset_seconds,
            "is_walking_paused",
            "next_walking_reminder_time",
            "_walking_idle_suppressed",
            self.show_walking_notification,
        )

    def water_timer_worker(self) -> None:
        self._timer_loop(
            self.water_interval_minutes,
            self.water_offset_seconds,
            "is_water_paused",
            "next_water_reminder_time",
            "_water_idle_suppressed",
            self.show_water_notification,
        )

    def pranayama_timer_worker(self) -> None:
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
