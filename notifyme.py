"""
Reminder app - Windows Desktop Application
    Reminds users to blink their eyes at regular intervals to reduce eye strain.
    Uses system tray icon and Windows toast notifications.
    Remind intervals and settings are configurable via a JSON file.
    Remind user to walk at longer intervals.
    Logs events to a rolling log file.
"""

import json
import logging
import random
import sys
import threading
import time
from logging.handlers import RotatingFileHandler
from pathlib import Path

from PIL import Image, ImageDraw
from pystray import Icon, Menu, MenuItem
from winotify import Notification, audio

# Configure logging with rolling file handler
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Create rotating file handler (5 MB per file, keep up to 5 backups)
handler = RotatingFileHandler(
    "notifyme.log",
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


class NotifyMeApp:
    """Main application class for the NotifyMe Reminder."""

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

    def __init__(self):
        """Initialize the NotifyMe Reminder application."""
        self.config_file = Path(__file__).parent / "config.json"
        self.icon_file = Path(__file__).parent / "icon.png"
        self.icon_file_ico = Path(__file__).parent / "icon.ico"

        # Ensure .ico exists for win10toast
        self.ensure_ico_exists()

        # Load configuration
        self.config = self.load_config()
        self.interval_minutes: int = self.config.get("interval_minutes") or 20
        self.walking_interval_minutes: int = self.config.get("walking_interval_minutes") or 60

        # Application state
        self.is_running = False
        self.is_paused = False
        self.timer_thread = None
        self.walking_timer_thread = None
        self.icon = None

        # Timer tracking
        self.next_reminder_time = None
        self.next_walking_reminder_time = None

        logging.info("Application initialized")

    def ensure_ico_exists(self):
        """Ensure an .ico version of the icon exists for notifications."""
        if not self.icon_file_ico.exists() and self.icon_file.exists():
            try:
                img = Image.open(self.icon_file)
                img.save(self.icon_file_ico, format="ICO")
                logging.info("Created icon.ico from %s", self.icon_file.name)
            except Exception as e:
                logging.error("Failed to create .ico file: %s", e)

    def load_config(self):
        """Load configuration from JSON file."""
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
            "interval_minutes": 20,
            "walking_interval_minutes": 60,
            "sound_enabled": False,
            "auto_start": False,
            "last_run": None,
        }

    def save_config(self):
        """Save current configuration to JSON file."""
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            logging.error("Error saving config: %s", e)

    def create_icon_image(self):
        """Create or load the system tray icon."""
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

    def show_notification(self, title="Eye Blink Reminder", messages=None):
        """Display a Windows toast notification."""
        if messages is None:
            messages = self.BLINK_MESSAGES
        message = random.choice(messages)  # noqa: S311
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

    def show_blink_notification(self):
        """Display a blink reminder notification."""
        self.show_notification("Eye Blink Reminder", self.BLINK_MESSAGES)

    def show_walking_notification(self):
        """Display a walking reminder notification."""
        self.show_notification("Walking Reminder", self.WALKING_MESSAGES)

    def timer_worker(self):
        """Background worker that triggers blink reminders at intervals."""
        while self.is_running:
            if not self.is_paused:
                # Calculate next reminder time
                self.next_reminder_time = time.time() + (self.interval_minutes * 60)

                # Wait for the interval
                time.sleep(self.interval_minutes * 60)

                # Show notification if still running and not paused
                if self.is_running and not self.is_paused:
                    self.show_blink_notification()
            else:
                # If paused, check every second
                time.sleep(1)

    def walking_timer_worker(self):
        """Background worker that triggers walking reminders at intervals."""
        while self.is_running:
            if not self.is_paused:
                # Calculate next walking reminder time
                self.next_walking_reminder_time = time.time() + (self.walking_interval_minutes * 60)

                # Wait for the interval
                time.sleep(self.walking_interval_minutes * 60)

                # Show notification if still running and not paused
                if self.is_running and not self.is_paused:
                    self.show_walking_notification()
            else:
                # If paused, check every second
                time.sleep(1)

    def start_reminders(self):
        """Start the reminder timers."""
        if not self.is_running:
            self.is_running = True
            self.is_paused = False
            self.timer_thread = threading.Thread(target=self.timer_worker, daemon=True)
            self.timer_thread.start()
            self.walking_timer_thread = threading.Thread(target=self.walking_timer_worker, daemon=True)
            self.walking_timer_thread.start()
            logging.info("Reminders started")
            if self.icon:
                self.icon.title = (
                    f"Reminders Active - Blink: {self.interval_minutes}min, Walk: {self.walking_interval_minutes}min"
                )

    def pause_reminders(self):
        """Pause the reminder timer."""
        self.is_paused = True
        logging.info("Reminders paused")
        if self.icon:
            self.icon.title = "NotifyMe - Paused"

    def resume_reminders(self):
        """Resume the reminder timer."""
        if self.is_running:
            self.is_paused = False
            logging.info("Reminders resumed")
            if self.icon:
                self.icon.title = (
                    f"Reminders Active - Blink: {self.interval_minutes}min, Walk: {self.walking_interval_minutes}min"
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
            if self.icon:
                self.icon.title = (
                    f"Reminders Active - Blink: {self.interval_minutes}min, Walk: {self.walking_interval_minutes}min"
                )

        return _set

    def set_walking_interval(self, minutes):
        """Set a new walking reminder interval."""

        def _set():
            self.walking_interval_minutes = minutes
            self.config["walking_interval_minutes"] = minutes
            self.save_config()
            logging.info("Walking interval set to %s minutes", minutes)
            if self.icon:
                self.icon.title = (
                    f"Reminders Active - Blink: {self.interval_minutes}min, Walk: {self.walking_interval_minutes}min"
                )

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

    def create_menu(self):
        """Create the system tray menu."""
        return Menu(
            MenuItem("Start", self.start_reminders, default=True),
            MenuItem("Pause", self.pause_reminders),
            MenuItem("Resume", self.resume_reminders),
            MenuItem("Snooze (5 min)", self.snooze_reminder),
            Menu.SEPARATOR,
            MenuItem(
                "Test Notifications",
                Menu(
                    MenuItem("Test Blink", self.test_blink_notification),
                    MenuItem("Test Walking", self.test_walking_notification),
                ),
            ),
            Menu.SEPARATOR,
            MenuItem(
                "Blink Interval",
                Menu(
                    MenuItem("10 minutes", self.set_interval(10)),
                    MenuItem("15 minutes", self.set_interval(15)),
                    MenuItem("20 minutes", self.set_interval(20)),
                    MenuItem("30 minutes", self.set_interval(30)),
                    MenuItem("45 minutes", self.set_interval(45)),
                    MenuItem("60 minutes", self.set_interval(60)),
                ),
            ),
            MenuItem(
                "Walking Interval",
                Menu(
                    MenuItem("30 minutes", self.set_walking_interval(30)),
                    MenuItem("45 minutes", self.set_walking_interval(45)),
                    MenuItem("60 minutes", self.set_walking_interval(60)),
                    MenuItem("90 minutes", self.set_walking_interval(90)),
                    MenuItem("120 minutes", self.set_walking_interval(120)),
                ),
            ),
            Menu.SEPARATOR,
            MenuItem("Quit", self.quit_app),
        )

    def run(self):
        """Run the application with system tray icon."""
        # Create the icon
        icon_image = self.create_icon_image()
        self.icon = Icon(
            "NotifyMe",
            icon_image,
            "NotifyMe",
            menu=self.create_menu(),
        )

        # Auto-start if configured
        if self.config.get("auto_start", False):
            self.start_reminders()

        # Run the icon in a separate thread so main thread can handle signals
        logging.info("NotifyMe is running in the system tray")
        logging.info("Blink interval: %s minutes, Walking interval: %s minutes",
                     self.interval_minutes, self.walking_interval_minutes)
        print("NotifyMe is running. Press Ctrl+C to quit.")

        self.icon.run_detached()

        # Main thread waits for Ctrl+C
        try:
            while self.icon.visible:
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
