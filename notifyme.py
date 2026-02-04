"""
NotifyMe reminder app for Windows.

Provides system-tray controls and toast notifications for periodic reminders
to blink, walk, hydrate, and practice pranayama. Intervals and preferences are
stored in a JSON config file, and activity is logged to rotating log files.
"""

import ctypes
import json
import logging
import os
import random
import subprocess
import sys
import tempfile
import threading
import time
import webbrowser
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler
from pathlib import Path
from urllib.request import Request, urlopen

from PIL import Image, ImageDraw
from pystray import Icon, Menu, MenuItem
from ctypes import wintypes

from winotify import Notification, audio

# Reminder types
REMINDER_BLINK = "blink"
REMINDER_WALKING = "walking"
REMINDER_WATER = "water"
REMINDER_PRANAYAMA = "pranayama"

# Default intervals (minutes)
DEFAULT_BLINK_INTERVAL_MIN = 20
DEFAULT_WALKING_INTERVAL_MIN = 60
DEFAULT_WATER_INTERVAL_MIN = 30
DEFAULT_PRANAYAMA_INTERVAL_MIN = 120

# Reminder titles
TITLE_BLINK = "Eye Blink Reminder"
TITLE_WALKING = "Walking Reminder"
TITLE_WATER = "Water Reminder"
TITLE_PRANAYAMA = "Pranayama Reminder"

# Initial stagger offsets (seconds) to avoid simultaneous notifications
DEFAULT_OFFSETS_SECONDS = {
    REMINDER_BLINK: 30,
    REMINDER_WATER: 10,
    REMINDER_WALKING: 50,
    REMINDER_PRANAYAMA: 20,
}

# Versioning and update checks
APP_VERSION = "2.1.0"
GITHUB_REPO_URL = "https://github.com/atulkumar2/notifyme"
GITHUB_RELEASES_URL = f"{GITHUB_REPO_URL}/releases/latest"
GITHUB_RELEASES_API_URL = (
    "https://api.github.com/repos/atulkumar2/notifyme/releases/latest"
)
GITHUB_PAGES_URL = "https://atulkumar2.github.io/notifyme/"
UPDATE_CHECK_TIMEOUT_SECONDS = 5

HELP_ERROR_HTML = """
<html>
<head><title>Help Not Available</title></head>
<body style="font-family: Arial, sans-serif; margin: 40px; color: #666;">
    <h1>❌ Help Not Available</h1>
    <p>Could not open offline help or GitHub Pages.</p>
    <p>Please visit: <a href="{url}">{url}</a></p>
    <p>Or check the offline help at: help/index.html</p>
</body>
</html>
"""


def get_app_data_dir() -> Path:
    """Return the per-user app data directory for config and logs."""
    app_data = Path(os.environ.get("APPDATA", Path.home())) / "NotifyMe"
    app_data.mkdir(parents=True, exist_ok=True)
    return app_data


def get_resource_path(filename: str) -> Path:
    """Return path to a bundled or local resource (PyInstaller compatible)."""
    if getattr(sys, "frozen", False):
        # Running as compiled executable
        base_path = Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
    else:
        # Running as script
        base_path = Path(__file__).parent
    return base_path / filename


# App data directory for config and logs
APP_DATA_DIR = get_app_data_dir()

# Configure logging with rolling file handler
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Create rotating file handler (5 MB per file, keep up to 5 backups)
handler = RotatingFileHandler(
    APP_DATA_DIR / "notifyme.log",
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

class LASTINPUTINFO(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.UINT),
        ("dwTime", wintypes.DWORD),
    ]


def get_idle_seconds() -> float | None:
    """Return system idle time in seconds, or None if unavailable."""
    try:
        info = LASTINPUTINFO()
        info.cbSize = ctypes.sizeof(LASTINPUTINFO)
        if not ctypes.windll.user32.GetLastInputInfo(ctypes.byref(info)):
            return None
        tick_ms = ctypes.windll.kernel32.GetTickCount64()
        idle_ms = int(tick_ms) - int(info.dwTime)
        if idle_ms < 0:
            return None
        return idle_ms / 1000.0
    except Exception:
        return None


class NotifyMeApp:
    """Main application class for the NotifyMe reminder system."""

    # Blink reminder messages (randomized for variety)
    BLINK_MESSAGES = [
        "👁️ Time to blink! Give your eyes a break.",
        "💧 Blink reminder: Keep your eyes hydrated!",
        "✨ Don't forget to blink and look away from the screen.",
        "🌟 Eye care reminder: Blink 10 times slowly.",
        "💙 Your eyes need a break - blink and relax!",
        "🌈 Blink break! Look at something 20 feet away for 20 seconds.",
    ]

    # Walking reminder messages (randomized for variety)
    WALKING_MESSAGES = [
        "🚶 Time for a walk! Stretch your legs.",
        "🏃 Walking break: Get up and move around!",
        "🌿 Take a short walk - your body will thank you.",
        "💪 Stand up and walk for a few minutes!",
        "🚶‍♂️ Sitting too long? Time for a walking break!",
        "🌞 Walk around for 5 minutes - refresh your mind and body!",
    ]

    # Water drinking reminder messages (randomized for variety)
    WATER_MESSAGES = [
        "💧 Time to hydrate! Drink a glass of water.",
        "🚰 Water break: Stay hydrated for better health!",
        "💦 Don't forget to drink water - your body needs it!",
        "🌊 Hydration reminder: Drink some water now.",
        "💙 Keep yourself hydrated - drink water regularly!",
        "🥤 Water time! Drink at least 250ml now.",
    ]

    # Pranayama (breathing) reminder messages (randomized for variety)
    PRANAYAMA_MESSAGES = [
        "🧘 Pranayama break: Slow, deep breathing for 2-3 minutes.",
        "🌬️ Breathing reminder: Inhale 4, hold 4, exhale 6.",
        "🫁 Reset with pranayama: Calm breath, clear mind.",
        "🧘‍♀️ Pause and breathe: Gentle pranayama now.",
        "🌿 Take a breathing break: Relax your shoulders and breathe.",
        "🧘‍♂️ Pranayama time: Smooth, steady breaths.",
    ]

    def __init__(self):
        """Initialize the NotifyMe reminder application."""
        self.config_file = APP_DATA_DIR / "config.json"
        self.icon_file = get_resource_path("icon.png")
        self.icon_file_ico = get_resource_path("icon.ico")

        # Ensure .ico exists for win10toast
        self.ensure_ico_exists()

        # Load configuration
        self.config = self.load_config()
        self.interval_minutes: int = (
            self.config.get("interval_minutes") or DEFAULT_BLINK_INTERVAL_MIN
        )
        self.walking_interval_minutes: int = (
            self.config.get("walking_interval_minutes")
            or DEFAULT_WALKING_INTERVAL_MIN
        )
        self.water_interval_minutes: int = (
            self.config.get("water_interval_minutes") or DEFAULT_WATER_INTERVAL_MIN
        )
        self.pranayama_interval_minutes: int = (
            self.config.get("pranayama_interval_minutes")
            or DEFAULT_PRANAYAMA_INTERVAL_MIN
        )

        # Application state
        self.is_running = False
        self.is_paused = False
        self.is_blink_paused = False
        self.is_walking_paused = False
        self.is_water_paused = False
        self.is_pranayama_paused = False
        self.timer_thread = None
        self.walking_timer_thread = None
        self.water_timer_thread = None
        self.pranayama_timer_thread = None
        self.icon = None

        # Timer tracking
        self.next_reminder_time = None
        self.next_walking_reminder_time = None
        self.next_water_reminder_time = None
        self.next_pranayama_reminder_time = None
        self.blink_offset_seconds = DEFAULT_OFFSETS_SECONDS[REMINDER_BLINK]
        self.water_offset_seconds = DEFAULT_OFFSETS_SECONDS[REMINDER_WATER]
        self.walking_offset_seconds = DEFAULT_OFFSETS_SECONDS[REMINDER_WALKING]
        self.pranayama_offset_seconds = DEFAULT_OFFSETS_SECONDS[REMINDER_PRANAYAMA]
        self.last_blink_shown_at = None
        self.last_walking_shown_at = None
        self.last_water_shown_at = None
        self.last_pranayama_shown_at = None
        self._blink_idle_suppressed = False
        self._walking_idle_suppressed = False
        self._water_idle_suppressed = False
        self._pranayama_idle_suppressed = False
        self.update_available = False
        self.latest_version = None
        self.last_update_check_at = None

        logging.info("Application initialized")

    def ensure_ico_exists(self):
        """Ensure an .ico icon exists for toast notifications."""
        if not self.icon_file_ico.exists() and self.icon_file.exists():
            try:
                img = Image.open(self.icon_file)
                img.save(self.icon_file_ico, format="ICO")
                logging.info("Created icon.ico from %s", self.icon_file.name)
            except Exception as e:
                logging.error("Failed to create .ico file: %s", e)

    def load_config(self):
        """Load configuration from the JSON config file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logging.error("Error loading config: %s", e)
                return self.get_default_config()
        return self.get_default_config()

    def get_default_config(self):
        """Return default configuration."""
        return {
            "interval_minutes": DEFAULT_BLINK_INTERVAL_MIN,
            "walking_interval_minutes": DEFAULT_WALKING_INTERVAL_MIN,
            "water_interval_minutes": DEFAULT_WATER_INTERVAL_MIN,
            "pranayama_interval_minutes": DEFAULT_PRANAYAMA_INTERVAL_MIN,
            "sound_enabled": False,
            "last_run": None,
        }

    def save_config(self):
        """Persist current configuration to the JSON config file."""
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            logging.error("Error saving config: %s", e)

    def create_icon_image(self):
        """Create or load the system tray icon image."""
        if self.icon_file.exists():
            try:
                return Image.open(self.icon_file)
            except Exception as e:
                logging.error("Error loading icon: %s", e)

        # Fallback: Create a simple icon programmatically
        width = 64
        height = 64
        image = Image.new("RGB", (width, height), color="white")
        draw = ImageDraw.Draw(image)

        # Draw a simple eye shape
        draw.ellipse([10, 20, 54, 44], fill="lightblue", outline="blue", width=2)
        draw.ellipse([26, 26, 38, 38], fill="darkblue")
        draw.ellipse([29, 29, 35, 35], fill="black")

        return image

    def show_notification(
        self, title=TITLE_BLINK, messages=None, last_shown_at=None
    ):
        """Display a Windows toast notification for a reminder."""
        if messages is None:
            messages = self.BLINK_MESSAGES
        message = random.choice(messages)  # noqa: S311
        if last_shown_at:
            elapsed = max(0, time.time() - last_shown_at)
            message = f"{message}\nLast reminder: {self.format_elapsed(elapsed)} ago."
        try:
            # Get icon path for notification
            icon_path = (
                str(self.icon_file_ico)
                if self.icon_file_ico.exists()
                else (str(self.icon_file) if self.icon_file.exists() else None)
            )

            logging.info("Showing notification: %s", message)

            # Create notification using winotify
            toast_args = {
                "app_id": "NotifyMe Reminder",
                "title": title,
                "msg": message,
            }
            if icon_path:
                toast_args["icon"] = icon_path
            toast = Notification(**toast_args)
            toast.set_audio(audio.Default, loop=False)
            toast.show()
        except Exception as e:
            logging.error("Error showing notification: %s", e)

    def show_update_notification(self, latest_version: str):
        """Show a toast notification for an available app update."""
        try:
            message = (
                f"NotifyMe {latest_version} is available. "
                "Open the tray menu to update."
            )
            toast = Notification(
                app_id="NotifyMe Reminder",
                title="Update Available",
                msg=message,
            )
            toast.set_audio(audio.Default, loop=False)
            toast.show()
        except Exception as e:
            logging.error("Error showing update notification: %s", e)
    def show_blink_notification(self):
        """Display a blink reminder notification."""
        self.show_notification(
            TITLE_BLINK, self.BLINK_MESSAGES, self.last_blink_shown_at
        )
        self.last_blink_shown_at = time.time()

    def show_walking_notification(self):
        """Display a walking reminder notification."""
        self.show_notification(
            TITLE_WALKING, self.WALKING_MESSAGES, self.last_walking_shown_at
        )
        self.last_walking_shown_at = time.time()

    def show_water_notification(self):
        """Display a water drinking reminder notification."""
        self.show_notification(
            TITLE_WATER, self.WATER_MESSAGES, self.last_water_shown_at
        )
        self.last_water_shown_at = time.time()

    def show_pranayama_notification(self):
        """Display a pranayama reminder notification."""
        self.show_notification(
            TITLE_PRANAYAMA,
            self.PRANAYAMA_MESSAGES,
            self.last_pranayama_shown_at,
        )
        self.last_pranayama_shown_at = time.time()

    @staticmethod
    def format_elapsed(seconds: float) -> str:
        """Format elapsed time in a short, human-readable form."""
        minutes = int(round(seconds / 60))
        if minutes <= 1:
            return "1 min"
        if minutes < 60:
            return f"{minutes} mins"
        hours = minutes // 60
        rem_minutes = minutes % 60
        if rem_minutes == 0:
            return f"{hours}h"
        return f"{hours}h {rem_minutes}m"

    def should_reset_due_to_idle(self, interval_seconds: int, reminder_type: str) -> bool:
        """Return True if idle time exceeds interval and the timer should reset."""
        idle_seconds = get_idle_seconds()
        if idle_seconds is None:
            return False
        if idle_seconds >= interval_seconds:
            if reminder_type == REMINDER_BLINK and not self._blink_idle_suppressed:
                logging.info("Blink reminder reset due to user idle/lock")
            if (
                reminder_type == REMINDER_WALKING
                and not self._walking_idle_suppressed
            ):
                logging.info("Walking reminder reset due to user idle/lock")
            if reminder_type == REMINDER_WATER and not self._water_idle_suppressed:
                logging.info("Water reminder reset due to user idle/lock")
            if (
                reminder_type == REMINDER_PRANAYAMA
                and not self._pranayama_idle_suppressed
            ):
                logging.info("Pranayama reminder reset due to user idle/lock")
            return True
        return False

    def timer_worker(self):
        """Background worker that triggers blink reminders at intervals."""
        while self.is_running:
            if not self.is_paused and not self.is_blink_paused:
                interval_seconds = self.interval_minutes * 60
                now = time.time()

                if self.should_reset_due_to_idle(interval_seconds, REMINDER_BLINK):
                    self._blink_idle_suppressed = True
                    self.next_reminder_time = now + interval_seconds
                    time.sleep(1)
                    continue

                if self._blink_idle_suppressed:
                    self._blink_idle_suppressed = False

                if self.next_reminder_time is None:
                    self.next_reminder_time = now + interval_seconds + self.blink_offset_seconds

                if now >= self.next_reminder_time:
                    self.show_blink_notification()
                    self.next_reminder_time = now + interval_seconds
                time.sleep(1)
            else:
                # If paused, check every second
                time.sleep(1)

    def walking_timer_worker(self):
        """Background worker that triggers walking reminders at intervals."""
        while self.is_running:
            if not self.is_paused and not self.is_walking_paused:
                interval_seconds = self.walking_interval_minutes * 60
                now = time.time()

                if self.should_reset_due_to_idle(interval_seconds, REMINDER_WALKING):
                    self._walking_idle_suppressed = True
                    self.next_walking_reminder_time = now + interval_seconds
                    time.sleep(1)
                    continue

                if self._walking_idle_suppressed:
                    self._walking_idle_suppressed = False

                if self.next_walking_reminder_time is None:
                    self.next_walking_reminder_time = (
                        now + interval_seconds + self.walking_offset_seconds
                    )

                if now >= self.next_walking_reminder_time:
                    self.show_walking_notification()
                    self.next_walking_reminder_time = now + interval_seconds
                time.sleep(1)
            else:
                # If paused, check every second
                time.sleep(1)

    def water_timer_worker(self):
        """Background worker that triggers water reminders at intervals."""
        while self.is_running:
            if not self.is_paused and not self.is_water_paused:
                interval_seconds = self.water_interval_minutes * 60
                now = time.time()

                if self.should_reset_due_to_idle(interval_seconds, REMINDER_WATER):
                    self._water_idle_suppressed = True
                    self.next_water_reminder_time = now + interval_seconds
                    time.sleep(1)
                    continue

                if self._water_idle_suppressed:
                    self._water_idle_suppressed = False

                if self.next_water_reminder_time is None:
                    self.next_water_reminder_time = (
                        now + interval_seconds + self.water_offset_seconds
                    )

                if now >= self.next_water_reminder_time:
                    self.show_water_notification()
                    self.next_water_reminder_time = now + interval_seconds
                time.sleep(1)
            else:
                # If paused, check every second
                time.sleep(1)

    def pranayama_timer_worker(self):
        """Background worker that triggers pranayama reminders at intervals."""
        while self.is_running:
            if not self.is_paused and not self.is_pranayama_paused:
                interval_seconds = self.pranayama_interval_minutes * 60
                now = time.time()

                if self.should_reset_due_to_idle(
                    interval_seconds, REMINDER_PRANAYAMA
                ):
                    self._pranayama_idle_suppressed = True
                    self.next_pranayama_reminder_time = now + interval_seconds
                    time.sleep(1)
                    continue

                if self._pranayama_idle_suppressed:
                    self._pranayama_idle_suppressed = False

                if self.next_pranayama_reminder_time is None:
                    self.next_pranayama_reminder_time = (
                        now + interval_seconds + self.pranayama_offset_seconds
                    )

                if now >= self.next_pranayama_reminder_time:
                    self.show_pranayama_notification()
                    self.next_pranayama_reminder_time = now + interval_seconds
                time.sleep(1)
            else:
                # If paused, check every second
                time.sleep(1)

    def start_reminders(self):
        """Start all reminder timers."""
        if not self.is_running:
            self.is_running = True
            self.is_paused = False
            self.is_blink_paused = False
            self.is_walking_paused = False
            self.is_water_paused = False
            self.is_pranayama_paused = False
            self.timer_thread = threading.Thread(target=self.timer_worker, daemon=True)
            self.timer_thread.start()
            self.walking_timer_thread = threading.Thread(
                target=self.walking_timer_worker, daemon=True
            )
            self.walking_timer_thread.start()
            self.water_timer_thread = threading.Thread(
                target=self.water_timer_worker, daemon=True
            )
            self.water_timer_thread.start()
            self.pranayama_timer_thread = threading.Thread(
                target=self.pranayama_timer_worker, daemon=True
            )
            self.pranayama_timer_thread.start()
            logging.info("Reminders started")
            self.update_icon_title()

    def pause_reminders(self):
        """Pause all reminders."""
        self.is_paused = True
        logging.info("All reminders paused")
        self.update_icon_title()
        self.update_menu()

    def resume_reminders(self):
        """Resume all reminders and clear pause states."""
        self.is_paused = False
        self.is_blink_paused = False
        self.is_walking_paused = False
        self.is_water_paused = False
        self.is_pranayama_paused = False
        logging.info("All reminders resumed")
        self.update_icon_title()
        self.update_menu()

    def toggle_blink_pause(self):
        """Toggle pause state for blink reminders."""
        self.is_blink_paused = not self.is_blink_paused
        logging.info(
            "Blink reminders %s", "paused" if self.is_blink_paused else "resumed"
        )
        self.update_icon_title()
        self.update_menu()

    def toggle_walking_pause(self):
        """Toggle pause state for walking reminders."""
        self.is_walking_paused = not self.is_walking_paused
        logging.info(
            "Walking reminders %s", "paused" if self.is_walking_paused else "resumed"
        )
        self.update_icon_title()
        self.update_menu()

    def toggle_water_pause(self):
        """Toggle pause state for water reminders."""
        self.is_water_paused = not self.is_water_paused
        logging.info(
            "Water reminders %s", "paused" if self.is_water_paused else "resumed"
        )
        self.update_icon_title()
        self.update_menu()

    def toggle_pranayama_pause(self):
        """Toggle pause state for pranayama reminders."""
        self.is_pranayama_paused = not self.is_pranayama_paused
        logging.info(
            "Pranayama reminders %s",
            "paused" if self.is_pranayama_paused else "resumed",
        )
        self.update_icon_title()
        self.update_menu()

    def update_menu(self):
        """Update the system tray menu to reflect pause states."""
        if self.icon:
            self.icon.menu = self.create_menu()

    def update_icon_title(self):
        """Update the system tray icon title based on current state."""
        if not self.icon:
            return

        if self.is_paused:
            self.icon.title = "NotifyMe - All Paused"
            return

        # Build status for each reminder type
        blink_status = "⏸" if self.is_blink_paused else f"{self.interval_minutes}min"
        walk_status = (
            "⏸" if self.is_walking_paused else f"{self.walking_interval_minutes}min"
        )
        water_status = (
            "⏸" if self.is_water_paused else f"{self.water_interval_minutes}min"
        )
        pranayama_status = (
            "⏸"
            if self.is_pranayama_paused
            else f"{self.pranayama_interval_minutes}min"
        )

        self.icon.title = (
            "Blink: {blink}, Walk: {walk}, Water: {water}, Pranayama: {pranayama}"
        ).format(
            blink=blink_status,
            walk=walk_status,
            water=water_status,
            pranayama=pranayama_status,
        )

    def stop_reminders(self):
        """Stop the reminder timer."""
        self.is_running = False
        self.is_paused = False
        logging.info("Reminders stopped")
        if self.icon:
            self.icon.title = "NotifyMe - Stopped"

    def snooze_reminder(self):
        """Snooze the reminder for 5 minutes."""
        if self.is_running and not self.is_paused:
            # Reset the timer by updating next reminder time
            self.next_reminder_time = time.time() + (5 * 60)
            logging.info("Reminder snoozed for 5 minutes")

    def set_interval(self, minutes):
        """Set a new blink reminder interval."""

        def _set():
            self.interval_minutes = minutes
            self.config["interval_minutes"] = minutes
            self.save_config()
            logging.info("Blink interval set to %s minutes", minutes)
            self.update_icon_title()

        return _set

    def set_walking_interval(self, minutes):
        """Set a new walking reminder interval."""

        def _set():
            self.walking_interval_minutes = minutes
            self.config["walking_interval_minutes"] = minutes
            self.save_config()
            logging.info("Walking interval set to %s minutes", minutes)
            self.update_icon_title()

        return _set

    def set_water_interval(self, minutes):
        """Set a new water reminder interval."""

        def _set():
            self.water_interval_minutes = minutes
            self.config["water_interval_minutes"] = minutes
            self.save_config()
            logging.info("Water interval set to %s minutes", minutes)
            self.update_icon_title()

        return _set

    def set_pranayama_interval(self, minutes):
        """Set a new pranayama reminder interval."""

        def _set():
            self.pranayama_interval_minutes = minutes
            self.config["pranayama_interval_minutes"] = minutes
            self.save_config()
            logging.info("Pranayama interval set to %s minutes", minutes)
            self.update_icon_title()

        return _set

    def quit_app(self):
        """Quit the application."""
        self.stop_reminders()
        if self.icon:
            self.icon.stop()
        logging.info("Application closed")

    def test_blink_notification(self):
        """Trigger a test blink notification immediately."""
        logging.info("User requested test blink notification")
        self.show_blink_notification()

    def test_walking_notification(self):
        """Trigger a test walking notification immediately."""
        logging.info("User requested test walking notification")
        self.show_walking_notification()

    def test_water_notification(self):
        """Trigger a test water notification immediately."""
        logging.info("User requested test water notification")
        self.show_water_notification()

    def test_pranayama_notification(self):
        """Trigger a test pranayama notification immediately."""
        logging.info("User requested test pranayama notification")
        self.show_pranayama_notification()

    def open_log_location(self):
        """Open the log file location in Explorer."""
        log_path = APP_DATA_DIR / "notifyme.log"
        try:
            # Open Explorer and select the log file
            subprocess.run(["explorer", "/select,", str(log_path)], check=False)
            logging.info("Opened log location: %s", APP_DATA_DIR)
        except Exception as e:
            logging.error("Failed to open log location: %s", e)

    def open_exe_location(self):
        """Open the EXE/script location in Explorer."""
        if getattr(sys, "frozen", False):
            # Running as compiled executable
            exe_path = Path(sys.executable)
        else:
            # Running as script
            exe_path = Path(__file__)
        try:
            # Open Explorer and select the executable/script
            subprocess.run(["explorer", "/select,", str(exe_path)], check=False)
            logging.info("Opened EXE location: %s", exe_path.parent)
        except Exception as e:
            logging.error("Failed to open EXE location: %s", e)

    def open_config_location(self):
        """Open the config file location in Explorer."""
        config_path = self.config_file
        try:
            # Open Explorer and select the config file
            subprocess.run(["explorer", "/select,", str(config_path)], check=False)
            logging.info("Opened config location: %s", config_path.parent)
        except Exception as e:
            logging.error("Failed to open config location: %s", e)

    def open_help(self):
        """
        Open help with smart fallback:
        1. Try offline help/index.html (local or bundled)
        2. Fall back to GitHub Pages URL if offline help unavailable
        """
        # Offline help paths to try (in order of priority)
        help_search_paths = []

        # 1. Check bundled help directory (PyInstaller: help/index.html)
        help_search_paths.append(get_resource_path("help") / "index.html")

        # 2. Check project root help directory (dev mode)
        try:
            help_search_paths.append(Path(__file__).parent / "help" / "index.html")
        except NameError:
            # __file__ not available in frozen mode
            logging.debug("__file__ not available in frozen mode")

        # Try to open offline help first
        for help_path in help_search_paths:
            if help_path.exists():
                try:
                    webbrowser.open(help_path.as_uri())
                    logging.info("Opened offline help: %s", help_path)
                    return
                except Exception as e:
                    logging.error("Failed to open offline help: %s", e)

        try:
            webbrowser.open(GITHUB_PAGES_URL)
            logging.info("Opened GitHub Pages help: %s", GITHUB_PAGES_URL)
        except Exception as e:
            logging.error("Failed to open GitHub Pages help: %s", e)
            # Final fallback: show error
            try:
                error_html = HELP_ERROR_HTML.format(url=GITHUB_PAGES_URL)
                with tempfile.NamedTemporaryFile(
                    mode="w", suffix=".html", delete=False, encoding="utf-8"
                ) as f:
                    f.write(error_html)
                    temp_path = Path(f.name)
                webbrowser.open(temp_path.as_uri())
                logging.info("Displayed help error message")
            except Exception as final_error:
                logging.error("Failed to display help error: %s", final_error)

    def open_github(self):
        """Open the GitHub repository in the default browser."""
        try:
            webbrowser.open(GITHUB_REPO_URL)
            logging.info("Opened GitHub repository")
        except Exception as e:
            logging.error("Failed to open GitHub repository: %s", e)

    def open_github_releases(self):
        """Open the GitHub releases page in the default browser."""
        try:
            webbrowser.open(GITHUB_RELEASES_URL)
            logging.info("Opened GitHub releases")
        except Exception as e:
            logging.error("Failed to open GitHub releases: %s", e)

    def open_github_pages(self):
        """Open the GitHub Pages documentation in the default browser."""
        try:
            webbrowser.open(GITHUB_PAGES_URL)
            logging.info("Opened GitHub Pages documentation")
        except Exception as e:
            logging.error("Failed to open GitHub Pages documentation: %s", e)

    def get_current_version(self) -> str:
        """Return the current application version string."""
        return APP_VERSION

    @staticmethod
    def parse_version(version: str) -> tuple[int, int, int]:
        """Parse a version string into a numeric tuple (major, minor, patch)."""
        cleaned = version.strip().lower().lstrip("v")
        parts = cleaned.split(".")
        nums = []
        for part in parts[:3]:
            num = ""
            for ch in part:
                if ch.isdigit():
                    num += ch
                else:
                    break
            nums.append(int(num or 0))
        while len(nums) < 3:
            nums.append(0)
        return tuple(nums[:3])

    def check_for_updates(self):
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
            if self.parse_version(latest) > self.parse_version(current):
                self.update_available = True
                self.latest_version = latest
                logging.info("Update available: %s (current: %s)", latest, current)
                self.show_update_notification(latest)
            else:
                self.update_available = False
                self.latest_version = latest
                logging.info("No update available (current: %s)", current)
        except Exception as e:
            logging.error("Failed to check for updates: %s", e)
        finally:
            self.last_update_check_at = datetime.now(timezone.utc)
            self.update_menu()

    def check_for_updates_async(self):
        """Run update check in a background thread."""
        thread = threading.Thread(target=self.check_for_updates, daemon=True)
        thread.start()

    def create_menu(self):
        """Create the system tray menu."""
        if self.update_available and self.latest_version:
            update_label = f"⬆ Update available: v{self.latest_version}"
            update_item = MenuItem(update_label, self.open_github_releases)
        else:
            update_item = MenuItem("✅ Up to date", None, enabled=False)

        return Menu(
            update_item,
            MenuItem("🔄 Check for Updates", self.check_for_updates_async),
            Menu.SEPARATOR,
            MenuItem(
                "⚙ Controls",
                Menu(
                    MenuItem("▶ Start", self.start_reminders, default=True),
                    MenuItem("⏸ Pause All", self.pause_reminders),
                    MenuItem("▶ Resume All", self.resume_reminders),
                ),
            ),
            MenuItem("💤 Snooze (5 min)", self.snooze_reminder),
            Menu.SEPARATOR,
            MenuItem(
                "🔔 Test Notifications",
                Menu(
                    MenuItem("👁 Test Blink", self.test_blink_notification),
                    MenuItem("🚶 Test Walking", self.test_walking_notification),
                    MenuItem("💧 Test Water", self.test_water_notification),
                    MenuItem("🧘 Test Pranayama", self.test_pranayama_notification),
                ),
            ),
            Menu.SEPARATOR,
            MenuItem(
                "👁 Blink Reminder",
                Menu(
                    MenuItem(
                        "⏸ Pause/Resume",
                        self.toggle_blink_pause,
                        checked=lambda _: self.is_blink_paused,
                    ),
                    Menu.SEPARATOR,
                    MenuItem(
                        "10 minutes",
                        self.set_interval(10),
                        checked=lambda _: self.interval_minutes == 10,
                        enabled=not self.is_blink_paused and not self.is_paused,
                    ),
                    MenuItem(
                        "15 minutes",
                        self.set_interval(15),
                        checked=lambda _: self.interval_minutes == 15,
                        enabled=not self.is_blink_paused and not self.is_paused,
                    ),
                    MenuItem(
                        "20 minutes",
                        self.set_interval(20),
                        checked=lambda _: self.interval_minutes == 20,
                        enabled=not self.is_blink_paused and not self.is_paused,
                    ),
                    MenuItem(
                        "30 minutes",
                        self.set_interval(30),
                        checked=lambda _: self.interval_minutes == 30,
                        enabled=not self.is_blink_paused and not self.is_paused,
                    ),
                    MenuItem(
                        "45 minutes",
                        self.set_interval(45),
                        checked=lambda _: self.interval_minutes == 45,
                        enabled=not self.is_blink_paused and not self.is_paused,
                    ),
                    MenuItem(
                        "60 minutes",
                        self.set_interval(60),
                        checked=lambda _: self.interval_minutes == 60,
                        enabled=not self.is_blink_paused and not self.is_paused,
                    ),
                ),
            ),
            MenuItem(
                "🚶 Walking Reminder",
                Menu(
                    MenuItem(
                        "⏸ Pause/Resume",
                        self.toggle_walking_pause,
                        checked=lambda _: self.is_walking_paused,
                    ),
                    Menu.SEPARATOR,
                    MenuItem(
                        "30 minutes",
                        self.set_walking_interval(30),
                        checked=lambda _: self.walking_interval_minutes == 30,
                        enabled=not self.is_walking_paused and not self.is_paused,
                    ),
                    MenuItem(
                        "45 minutes",
                        self.set_walking_interval(45),
                        checked=lambda _: self.walking_interval_minutes == 45,
                        enabled=not self.is_walking_paused and not self.is_paused,
                    ),
                    MenuItem(
                        "60 minutes",
                        self.set_walking_interval(60),
                        checked=lambda _: self.walking_interval_minutes == 60,
                        enabled=not self.is_walking_paused and not self.is_paused,
                    ),
                    MenuItem(
                        "90 minutes",
                        self.set_walking_interval(90),
                        checked=lambda _: self.walking_interval_minutes == 90,
                        enabled=not self.is_walking_paused and not self.is_paused,
                    ),
                    MenuItem(
                        "120 minutes",
                        self.set_walking_interval(120),
                        checked=lambda _: self.walking_interval_minutes == 120,
                        enabled=not self.is_walking_paused and not self.is_paused,
                    ),
                ),
            ),
            MenuItem(
                "💧 Water Reminder",
                Menu(
                    MenuItem(
                        "⏸ Pause/Resume",
                        self.toggle_water_pause,
                        checked=lambda _: self.is_water_paused,
                    ),
                    Menu.SEPARATOR,
                    MenuItem(
                        "20 minutes",
                        self.set_water_interval(20),
                        checked=lambda _: self.water_interval_minutes == 20,
                        enabled=not self.is_water_paused and not self.is_paused,
                    ),
                    MenuItem(
                        "30 minutes",
                        self.set_water_interval(30),
                        checked=lambda _: self.water_interval_minutes == 30,
                        enabled=not self.is_water_paused and not self.is_paused,
                    ),
                    MenuItem(
                        "45 minutes",
                        self.set_water_interval(45),
                        checked=lambda _: self.water_interval_minutes == 45,
                        enabled=not self.is_water_paused and not self.is_paused,
                    ),
                    MenuItem(
                        "60 minutes",
                        self.set_water_interval(60),
                        checked=lambda _: self.water_interval_minutes == 60,
                        enabled=not self.is_water_paused and not self.is_paused,
                    ),
                    MenuItem(
                        "90 minutes",
                        self.set_water_interval(90),
                        checked=lambda _: self.water_interval_minutes == 90,
                        enabled=not self.is_water_paused and not self.is_paused,
                    ),
                ),
            ),
            MenuItem(
                "🧘 Pranayama Reminder",
                Menu(
                    MenuItem(
                        "⏸ Pause/Resume",
                        self.toggle_pranayama_pause,
                        checked=lambda _: self.is_pranayama_paused,
                    ),
                    Menu.SEPARATOR,
                    MenuItem(
                        "60 minutes",
                        self.set_pranayama_interval(60),
                        checked=lambda _: self.pranayama_interval_minutes == 60,
                        enabled=not self.is_pranayama_paused and not self.is_paused,
                    ),
                    MenuItem(
                        "90 minutes",
                        self.set_pranayama_interval(90),
                        checked=lambda _: self.pranayama_interval_minutes == 90,
                        enabled=not self.is_pranayama_paused and not self.is_paused,
                    ),
                    MenuItem(
                        "120 minutes",
                        self.set_pranayama_interval(120),
                        checked=lambda _: self.pranayama_interval_minutes == 120,
                        enabled=not self.is_pranayama_paused and not self.is_paused,
                    ),
                    MenuItem(
                        "180 minutes",
                        self.set_pranayama_interval(180),
                        checked=lambda _: self.pranayama_interval_minutes == 180,
                        enabled=not self.is_pranayama_paused and not self.is_paused,
                    ),
                    MenuItem(
                        "240 minutes",
                        self.set_pranayama_interval(240),
                        checked=lambda _: self.pranayama_interval_minutes == 240,
                        enabled=not self.is_pranayama_paused and not self.is_paused,
                    ),
                ),
            ),
            Menu.SEPARATOR,
            MenuItem(
                "❓ Help",
                Menu(
                    MenuItem("🌐 User Guide", self.open_help),
                    MenuItem("� Online Documentation", self.open_github_pages),
                    MenuItem("�🐙 GitHub Repository", self.open_github),
                    MenuItem("⬆ Releases", self.open_github_releases),
                ),
            ),
            Menu.SEPARATOR,
            MenuItem(
                "📂 Open Locations",
                Menu(
                    MenuItem("📄 Log Location", self.open_log_location),
                    MenuItem("⚙ Config Location", self.open_config_location),
                    MenuItem("📦 App Location", self.open_exe_location),
                ),
            ),
            Menu.SEPARATOR,
            MenuItem("❌ Quit", self.quit_app),
        )

    def get_initial_title(self):
        """Get the initial title for the system tray icon."""
        blink_status = f"{self.interval_minutes}min"
        walk_status = f"{self.walking_interval_minutes}min"
        water_status = f"{self.water_interval_minutes}min"
        pranayama_status = f"{self.pranayama_interval_minutes}min"
        return (
            "Blink: {blink}, Walk: {walk}, Water: {water}, Pranayama: {pranayama}"
        ).format(
            blink=blink_status,
            walk=walk_status,
            water=water_status,
            pranayama=pranayama_status,
        )

    def run(self):
        """Run the application with system tray icon and timers."""
        # Create the icon
        icon_image = self.create_icon_image()
        self.icon = Icon(
            "NotifyMe",
            icon_image,
            self.get_initial_title(),
            menu=self.create_menu(),
        )

        self.check_for_updates_async()

        # Always start reminders on launch
        self.start_reminders()

        # Run the icon in a separate thread so main thread can handle signals
        logging.info("NotifyMe is running in the system tray")
        logging.info(
            "Blink interval: %s minutes, Walking interval: %s minutes, Water interval: %s minutes, Pranayama interval: %s minutes",
            self.interval_minutes,
            self.walking_interval_minutes,
            self.water_interval_minutes,
            self.pranayama_interval_minutes,
        )
        logging.info("NotifyMe version: %s", self.get_current_version())
        print("NotifyMe is running. Press Ctrl+C to quit.")

        self.icon.run_detached()

        # Main thread waits for Ctrl+C or explicit quit
        try:
            while True:
                if not self.is_running and (not self.icon or not self.icon.visible):
                    break
                time.sleep(0.5)
        except KeyboardInterrupt:
            print("\nShutting down...")
            logging.info("Received Ctrl+C, shutting down...")
        finally:
            self.quit_app()


def main():
    """Main entry point for the application."""
    app = NotifyMeApp()
    app.run()


if __name__ == "__main__":
    main()
