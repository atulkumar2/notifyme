"""
Main application class for the NotifyMe reminder system.

This module contains the main NotifyMeApp class that coordinates all the
different components of the application including timers, notifications,
configuration, and system tray integration.
"""

import logging
import time
from typing import TYPE_CHECKING, Optional

from pystray import Icon
from winotify import Notification

from notifyme_app.config import ConfigManager
from notifyme_app.constants import (
    APP_VERSION,
    REMINDER_BLINK,
    REMINDER_PRANAYAMA,
    REMINDER_WALKING,
    REMINDER_WATER,
)
from notifyme_app.menu import MenuManager
from notifyme_app.notifications import NotificationManager
from notifyme_app.system import SystemManager
from notifyme_app.timers import TimerManager
from notifyme_app.tts import get_tts_manager
from notifyme_app.updater import UpdateChecker

if TYPE_CHECKING:
    from pystray._base import Icon as PystrayIcon


class NotifyMeApp:
    """Main application class for the NotifyMe reminder system."""

    def __init__(self):
        """Initialize the NotifyMe reminder application."""
        # Initialize managers
        self.config = ConfigManager()
        self.notifications = NotificationManager()
        self.system = SystemManager()
        self.timers = TimerManager()
        self.updater = UpdateChecker(self.notifications.show_update_notification)

        # Create menu manager with callbacks
        self.menu_manager = MenuManager(self._get_menu_callbacks())

        # Application state
        self.icon: Optional["PystrayIcon"] = None
        self.last_blink_shown_at: Optional[float] = None
        self.last_walking_shown_at: Optional[float] = None
        self.last_water_shown_at: Optional[float] = None
        self.last_pranayama_shown_at: Optional[float] = None

        # Initialize timers
        self._setup_timers()

        logging.info("Application initialized")

    def _setup_timers(self) -> None:
        """Set up reminder timers with callbacks."""
        self.timers.create_timer(
            REMINDER_BLINK,
            self.config.interval_minutes,
            self._on_blink_reminder,
        )
        self.timers.create_timer(
            REMINDER_WALKING,
            self.config.walking_interval_minutes,
            self._on_walking_reminder,
        )
        self.timers.create_timer(
            REMINDER_WATER,
            self.config.water_interval_minutes,
            self._on_water_reminder,
        )
        self.timers.create_timer(
            REMINDER_PRANAYAMA,
            self.config.pranayama_interval_minutes,
            self._on_pranayama_reminder,
        )

    def _on_blink_reminder(self) -> None:
        """Handle blink reminder trigger."""
        if not self.config.blink_hidden:
            sound_enabled = (
                self.config.sound_enabled and self.config.blink_sound_enabled
            )
            message = self.notifications.show_blink_notification(
                self.last_blink_shown_at, sound_enabled
            )
            self.last_blink_shown_at = time.time()

            # Optionally speak the reminder using offline TTS
            try:
                if self.config.tts_enabled and self.config.blink_tts_enabled:
                    tts = get_tts_manager()
                    speak_text = f"Blink reminder: {message}"
                    tts.speak_async(speak_text, lang=self.config.tts_language)
            except Exception as e:
                logging.error("Error invoking TTS for blink reminder: %s", e)

    def _on_walking_reminder(self) -> None:
        """Handle walking reminder trigger."""
        if not self.config.walking_hidden:
            sound_enabled = (
                self.config.sound_enabled and self.config.walking_sound_enabled
            )
            message = self.notifications.show_walking_notification(
                self.last_walking_shown_at, sound_enabled
            )
            self.last_walking_shown_at = time.time()

            try:
                if self.config.tts_enabled and self.config.walking_tts_enabled:
                    tts = get_tts_manager()
                    tts.speak_async(
                        f"Walking reminder: {message}", lang=self.config.tts_language
                    )
            except Exception as e:
                logging.error("Error invoking TTS for walking reminder: %s", e)

    def _on_water_reminder(self) -> None:
        """Handle water reminder trigger."""
        if not self.config.water_hidden:
            sound_enabled = (
                self.config.sound_enabled and self.config.water_sound_enabled
            )
            message = self.notifications.show_water_notification(
                self.last_water_shown_at, sound_enabled
            )
            self.last_water_shown_at = time.time()

            try:
                if self.config.tts_enabled and self.config.water_tts_enabled:
                    tts = get_tts_manager()
                    tts.speak_async(
                        f"Water reminder: {message}", lang=self.config.tts_language
                    )
            except Exception as e:
                logging.error("Error invoking TTS for water reminder: %s", e)

    def _on_pranayama_reminder(self) -> None:
        """Handle pranayama reminder trigger."""
        if not self.config.pranayama_hidden:
            sound_enabled = (
                self.config.sound_enabled and self.config.pranayama_sound_enabled
            )
            message = self.notifications.show_pranayama_notification(
                self.last_pranayama_shown_at, sound_enabled
            )
            self.last_pranayama_shown_at = time.time()

            try:
                if self.config.tts_enabled and self.config.pranayama_tts_enabled:
                    tts = get_tts_manager()
                    tts.speak_async(
                        f"Pranayama reminder: {message}", lang=self.config.tts_language
                    )
            except Exception as e:
                logging.error("Error invoking TTS for pranayama reminder: %s", e)

    def _get_menu_callbacks(self) -> dict:
        """Get callback functions for menu items."""
        return {
            # Control callbacks
            "start_reminders": self.start_reminders,
            "pause_reminders": self.pause_reminders,
            "resume_reminders": self.resume_reminders,
            "snooze_reminder": self.snooze_reminder,
            "quit_app": self.quit_app,
            # Sound callbacks
            "toggle_sound": self.toggle_sound,
            "toggle_blink_sound": self.toggle_blink_sound,
            "toggle_walking_sound": self.toggle_walking_sound,
            "toggle_water_sound": self.toggle_water_sound,
            "toggle_pranayama_sound": self.toggle_pranayama_sound,
            # TTS callbacks
            "toggle_tts": self.toggle_tts,
            "toggle_blink_tts": self.toggle_blink_tts,
            "toggle_walking_tts": self.toggle_walking_tts,
            "toggle_water_tts": self.toggle_water_tts,
            "toggle_pranayama_tts": self.toggle_pranayama_tts,
            # Visibility callbacks
            "toggle_blink_hidden": self.toggle_blink_hidden,
            "toggle_walking_hidden": self.toggle_walking_hidden,
            "toggle_water_hidden": self.toggle_water_hidden,
            "toggle_pranayama_hidden": self.toggle_pranayama_hidden,
            # Pause callbacks
            "toggle_blink_pause": self.toggle_blink_pause,
            "toggle_walking_pause": self.toggle_walking_pause,
            "toggle_water_pause": self.toggle_water_pause,
            "toggle_pranayama_pause": self.toggle_pranayama_pause,
            # Interval callbacks
            "set_blink_interval": self.set_interval,
            "set_walking_interval": self.set_walking_interval,
            "set_water_interval": self.set_water_interval,
            "set_pranayama_interval": self.set_pranayama_interval,
            # Test callbacks
            "test_blink_notification": self.test_blink_notification,
            "test_walking_notification": self.test_walking_notification,
            "test_water_notification": self.test_water_notification,
            "test_pranayama_notification": self.test_pranayama_notification,
            # System callbacks
            "open_help": self.system.open_help,
            "open_github": self.system.open_github,
            "open_github_pages": self.system.open_github_pages,
            "open_github_releases": self.system.open_github_releases,
            "open_log_location": self.system.open_log_location,
            "open_config_location": self.system.open_config_location,
            "open_exe_location": self.system.open_exe_location,
            # Update callbacks
            "check_for_updates_async": self.updater.check_for_updates_async,
            "show_about": self.show_about,
        }

    def start_reminders(self) -> None:
        """Start all reminder timers."""
        self.timers.start_all()
        self.update_icon_title()

    def pause_reminders(self) -> None:
        """Pause all reminders."""
        self.timers.pause_all()
        self.update_icon_title()
        self.update_menu()

    def resume_reminders(self) -> None:
        """Resume all reminders and clear pause states."""
        self.timers.resume_all()
        self.update_icon_title()
        self.update_menu()

    def snooze_reminder(self) -> None:
        """Snooze all reminders for 5 minutes."""
        self.timers.snooze_all(5)
        logging.info("All reminders snoozed for 5 minutes")

    def stop_reminders(self) -> None:
        """Stop all reminder timers."""
        self.timers.stop_all()
        if self.icon:
            self.icon.title = "NotifyMe - Stopped"

    # Sound control methods
    def toggle_sound(self) -> None:
        """Toggle global sound on/off."""
        self.config.sound_enabled = not self.config.sound_enabled
        logging.info(
            "Global sound %s", "enabled" if self.config.sound_enabled else "disabled"
        )
        self.update_menu()

    def toggle_blink_sound(self) -> None:
        """Toggle blink reminder sound on/off."""
        self.config.blink_sound_enabled = not self.config.blink_sound_enabled
        logging.info(
            "Blink sound %s",
            "enabled" if self.config.blink_sound_enabled else "disabled",
        )
        self.update_menu()

    def toggle_walking_sound(self) -> None:
        """Toggle walking reminder sound on/off."""
        self.config.walking_sound_enabled = not self.config.walking_sound_enabled
        logging.info(
            "Walking sound %s",
            "enabled" if self.config.walking_sound_enabled else "disabled",
        )
        self.update_menu()

    def toggle_water_sound(self) -> None:
        """Toggle water reminder sound on/off."""
        self.config.water_sound_enabled = not self.config.water_sound_enabled
        logging.info(
            "Water sound %s",
            "enabled" if self.config.water_sound_enabled else "disabled",
        )
        self.update_menu()

    def toggle_pranayama_sound(self) -> None:
        """Toggle pranayama reminder sound on/off."""
        self.config.pranayama_sound_enabled = not self.config.pranayama_sound_enabled
        logging.info(
            "Pranayama sound %s",
            "enabled" if self.config.pranayama_sound_enabled else "disabled",
        )
        self.update_menu()

    # TTS control methods
    def toggle_tts(self) -> None:
        """Toggle global Text-to-Speech on/off."""
        self.config.tts_enabled = not self.config.tts_enabled
        logging.info(
            "Global TTS %s", "enabled" if self.config.tts_enabled else "disabled"
        )
        self.update_menu()

    def toggle_blink_tts(self) -> None:
        """Toggle blink reminder TTS on/off."""
        self.config.blink_tts_enabled = not self.config.blink_tts_enabled
        logging.info(
            "Blink TTS %s", "enabled" if self.config.blink_tts_enabled else "disabled"
        )
        self.update_menu()

    def toggle_walking_tts(self) -> None:
        """Toggle walking reminder TTS on/off."""
        self.config.walking_tts_enabled = not self.config.walking_tts_enabled
        logging.info(
            "Walking TTS %s",
            "enabled" if self.config.walking_tts_enabled else "disabled",
        )
        self.update_menu()

    def toggle_water_tts(self) -> None:
        """Toggle water reminder TTS on/off."""
        self.config.water_tts_enabled = not self.config.water_tts_enabled
        logging.info(
            "Water TTS %s", "enabled" if self.config.water_tts_enabled else "disabled"
        )
        self.update_menu()

    def toggle_pranayama_tts(self) -> None:
        """Toggle pranayama reminder TTS on/off."""
        self.config.pranayama_tts_enabled = not self.config.pranayama_tts_enabled
        logging.info(
            "Pranayama TTS %s",
            "enabled" if self.config.pranayama_tts_enabled else "disabled",
        )
        self.update_menu()

    # Visibility control methods
    def toggle_blink_hidden(self) -> None:
        """Toggle blink reminder visibility."""
        self.config.blink_hidden = not self.config.blink_hidden
        logging.info(
            "Blink reminder %s", "hidden" if self.config.blink_hidden else "visible"
        )
        self.update_menu()

    def toggle_walking_hidden(self) -> None:
        """Toggle walking reminder visibility."""
        self.config.walking_hidden = not self.config.walking_hidden
        logging.info(
            "Walking reminder %s", "hidden" if self.config.walking_hidden else "visible"
        )
        self.update_menu()

    def toggle_water_hidden(self) -> None:
        """Toggle water reminder visibility."""
        self.config.water_hidden = not self.config.water_hidden
        logging.info(
            "Water reminder %s", "hidden" if self.config.water_hidden else "visible"
        )
        self.update_menu()

    def toggle_pranayama_hidden(self) -> None:
        """Toggle pranayama reminder visibility."""
        self.config.pranayama_hidden = not self.config.pranayama_hidden
        logging.info(
            "Pranayama reminder %s",
            "hidden" if self.config.pranayama_hidden else "visible",
        )
        self.update_menu()

    # Pause control methods
    def toggle_blink_pause(self) -> None:
        """Toggle pause state for blink reminders."""
        self.timers.toggle_timer_pause(REMINDER_BLINK)
        self.update_icon_title()
        self.update_menu()

    def toggle_walking_pause(self) -> None:
        """Toggle pause state for walking reminders."""
        self.timers.toggle_timer_pause(REMINDER_WALKING)
        self.update_icon_title()
        self.update_menu()

    def toggle_water_pause(self) -> None:
        """Toggle pause state for water reminders."""
        self.timers.toggle_timer_pause(REMINDER_WATER)
        self.update_icon_title()
        self.update_menu()

    def toggle_pranayama_pause(self) -> None:
        """Toggle pause state for pranayama reminders."""
        self.timers.toggle_timer_pause(REMINDER_PRANAYAMA)
        self.update_icon_title()
        self.update_menu()

    # Interval setting methods
    def set_interval(self, minutes: int):
        """Set a new blink reminder interval."""

        def _set():
            self.config.interval_minutes = minutes
            self.timers.update_timer_interval(REMINDER_BLINK, minutes)
            logging.info("Blink interval set to %s minutes", minutes)
            self.update_icon_title()

        return _set

    def set_walking_interval(self, minutes: int):
        """Set a new walking reminder interval."""

        def _set():
            self.config.walking_interval_minutes = minutes
            self.timers.update_timer_interval(REMINDER_WALKING, minutes)
            logging.info("Walking interval set to %s minutes", minutes)
            self.update_icon_title()

        return _set

    def set_water_interval(self, minutes: int):
        """Set a new water reminder interval."""

        def _set():
            self.config.water_interval_minutes = minutes
            self.timers.update_timer_interval(REMINDER_WATER, minutes)
            logging.info("Water interval set to %s minutes", minutes)
            self.update_icon_title()

        return _set

    def set_pranayama_interval(self, minutes: int):
        """Set a new pranayama reminder interval."""

        def _set():
            self.config.pranayama_interval_minutes = minutes
            self.timers.update_timer_interval(REMINDER_PRANAYAMA, minutes)
            logging.info("Pranayama interval set to %s minutes", minutes)
            self.update_icon_title()

        return _set

    # Test notification methods
    def test_blink_notification(self) -> None:
        """Trigger a test blink notification immediately."""
        logging.info("User requested test blink notification")
        try:
            # For test notifications, play sound when either global sound OR
            # the per-reminder sound setting is enabled (so tests can preview sound)
            sound_enabled = self.config.sound_enabled or self.config.blink_sound_enabled
            message = self.notifications.show_blink_notification(
                None, sound_enabled
            )  # Pass None for last_shown_at
            tts_preview = self.config.tts_enabled or self.config.blink_tts_enabled
            if message and tts_preview:
                tts = get_tts_manager()
                tts.speak_async(
                    f"Blink reminder: {message}",
                    lang=self.config.tts_language,
                )
            logging.info("Test blink notification displayed successfully")
        except Exception as e:
            logging.error("Failed to show test blink notification: %s", e)

    def test_walking_notification(self) -> None:
        """Trigger a test walking notification immediately."""
        logging.info("User requested test walking notification")
        try:
            sound_enabled = (
                self.config.sound_enabled or self.config.walking_sound_enabled
            )
            message = self.notifications.show_walking_notification(
                None, sound_enabled
            )  # Pass None for last_shown_at
            tts_preview = self.config.tts_enabled or self.config.walking_tts_enabled
            if message and tts_preview:
                tts = get_tts_manager()
                tts.speak_async(
                    f"Walking reminder: {message}",
                    lang=self.config.tts_language,
                )
            logging.info("Test walking notification displayed successfully")
        except Exception as e:
            logging.error("Failed to show test walking notification: %s", e)

    def test_water_notification(self) -> None:
        """Trigger a test water notification immediately."""
        logging.info("User requested test water notification")
        try:
            sound_enabled = self.config.sound_enabled or self.config.water_sound_enabled
            message = self.notifications.show_water_notification(
                None, sound_enabled
            )  # Pass None for last_shown_at
            tts_preview = self.config.tts_enabled or self.config.water_tts_enabled
            if message and tts_preview:
                tts = get_tts_manager()
                tts.speak_async(
                    f"Water reminder: {message}",
                    lang=self.config.tts_language,
                )
            logging.info("Test water notification displayed successfully")
        except Exception as e:
            logging.error("Failed to show test water notification: %s", e)

    def test_pranayama_notification(self) -> None:
        """Trigger a test pranayama notification immediately."""
        logging.info("User requested test pranayama notification")
        try:
            sound_enabled = (
                self.config.sound_enabled or self.config.pranayama_sound_enabled
            )
            message = self.notifications.show_pranayama_notification(
                None, sound_enabled
            )  # Pass None for last_shown_at
            tts_preview = self.config.tts_enabled or self.config.pranayama_tts_enabled
            if message and tts_preview:
                tts = get_tts_manager()
                tts.speak_async(
                    f"Pranayama reminder: {message}",
                    lang=self.config.tts_language,
                )
            logging.info("Test pranayama notification displayed successfully")
        except Exception as e:
            logging.error("Failed to show test pranayama notification: %s", e)

    def show_about(self) -> None:
        """Show about dialog with application information."""
        try:
            message = (
                f"NotifyMe v{APP_VERSION}\n\n"
                "A health reminder application that helps you:\n"
                "• Blink regularly to prevent eye strain\n"
                "• Take walking breaks for better circulation\n"
                "• Stay hydrated throughout the day\n"
                "• Practice pranayama for stress relief\n\n"
                "Built with Python and love ❤️\n"
                "© 2024 Atul Kumar"
            )

            toast_args = {
                "app_id": "NotifyMe Reminder",
                "title": "About NotifyMe",
                "msg": message,
            }

            icon_path = self.notifications._get_icon_path()
            if icon_path:
                toast_args["icon"] = icon_path

            toast = Notification(**toast_args)
            toast.show()

            logging.info("Showed about dialog")
        except Exception as e:
            logging.error("Failed to show about dialog: %s", e)

    def update_menu(self) -> None:
        """Update the system tray menu to reflect current state."""
        if self.icon:
            self.icon.menu = self.menu_manager.create_menu(
                update_available=self.updater.is_update_available(),
                latest_version=self.updater.get_latest_version() or "",
                sound_enabled=self.config.sound_enabled,
                tts_enabled=self.config.tts_enabled,
                blink_hidden=self.config.blink_hidden,
                walking_hidden=self.config.walking_hidden,
                water_hidden=self.config.water_hidden,
                pranayama_hidden=self.config.pranayama_hidden,
                blink_sound_enabled=self.config.blink_sound_enabled,
                walking_sound_enabled=self.config.walking_sound_enabled,
                water_sound_enabled=self.config.water_sound_enabled,
                pranayama_sound_enabled=self.config.pranayama_sound_enabled,
                blink_tts_enabled=self.config.blink_tts_enabled,
                walking_tts_enabled=self.config.walking_tts_enabled,
                water_tts_enabled=self.config.water_tts_enabled,
                pranayama_tts_enabled=self.config.pranayama_tts_enabled,
                is_blink_paused=self.timers.is_timer_paused(REMINDER_BLINK),
                is_walking_paused=self.timers.is_timer_paused(REMINDER_WALKING),
                is_water_paused=self.timers.is_timer_paused(REMINDER_WATER),
                is_pranayama_paused=self.timers.is_timer_paused(REMINDER_PRANAYAMA),
                is_paused=self.timers.is_global_paused,
                interval_minutes=self.config.interval_minutes,
                walking_interval_minutes=self.config.walking_interval_minutes,
                water_interval_minutes=self.config.water_interval_minutes,
                pranayama_interval_minutes=self.config.pranayama_interval_minutes,
            )

    def update_icon_title(self) -> None:
        """Update the system tray icon title based on current state."""
        if not self.icon:
            return

        if self.timers.is_global_paused:
            self.icon.title = "NotifyMe - All Paused"
            return

        # Build status for each reminder type
        blink_status = (
            "⏸"
            if self.timers.is_timer_paused(REMINDER_BLINK)
            else f"{self.config.interval_minutes}min"
        )
        walk_status = (
            "⏸"
            if self.timers.is_timer_paused(REMINDER_WALKING)
            else f"{self.config.walking_interval_minutes}min"
        )
        water_status = (
            "⏸"
            if self.timers.is_timer_paused(REMINDER_WATER)
            else f"{self.config.water_interval_minutes}min"
        )
        pranayama_status = (
            "⏸"
            if self.timers.is_timer_paused(REMINDER_PRANAYAMA)
            else f"{self.config.pranayama_interval_minutes}min"
        )

        self.icon.title = (
            f"Blink: {blink_status}, Walk: {walk_status},"
            f" Water: {water_status}, Pranayama: {pranayama_status}"
        )

    def get_initial_title(self) -> str:
        """Get the initial title for the system tray icon."""
        blink_status = f"{self.config.interval_minutes}min"
        walk_status = f"{self.config.walking_interval_minutes}min"
        water_status = f"{self.config.water_interval_minutes}min"
        pranayama_status = f"{self.config.pranayama_interval_minutes}min"
        return (
            f"Blink: {blink_status}, Walk: {walk_status},"
            f" Water: {water_status}, Pranayama: {pranayama_status}"
        )

    def quit_app(self) -> None:
        """Quit the application."""
        self.stop_reminders()
        if self.icon:
            self.icon.stop()
        try:
            get_tts_manager().stop()
        except Exception:
            pass
        logging.info("Application closed")

    def run(self) -> None:
        """Run the application with system tray icon and timers."""
        # Create the icon
        icon_image = self.system.create_icon_image()
        self.icon = Icon(
            "NotifyMe",
            icon_image,
            self.get_initial_title(),
            menu=self.menu_manager.create_menu(
                sound_enabled=self.config.sound_enabled,
                tts_enabled=self.config.tts_enabled,
                blink_hidden=self.config.blink_hidden,
                walking_hidden=self.config.walking_hidden,
                water_hidden=self.config.water_hidden,
                pranayama_hidden=self.config.pranayama_hidden,
                blink_sound_enabled=self.config.blink_sound_enabled,
                walking_sound_enabled=self.config.walking_sound_enabled,
                water_sound_enabled=self.config.water_sound_enabled,
                pranayama_sound_enabled=self.config.pranayama_sound_enabled,
                blink_tts_enabled=self.config.blink_tts_enabled,
                walking_tts_enabled=self.config.walking_tts_enabled,
                water_tts_enabled=self.config.water_tts_enabled,
                pranayama_tts_enabled=self.config.pranayama_tts_enabled,
                interval_minutes=self.config.interval_minutes,
                walking_interval_minutes=self.config.walking_interval_minutes,
                water_interval_minutes=self.config.water_interval_minutes,
                pranayama_interval_minutes=self.config.pranayama_interval_minutes,
            ),
        )

        self.updater.check_for_updates_async()

        # Always start reminders on launch
        self.start_reminders()

        # Show startup help and welcome notification
        self.system.show_startup_help()
        self.notifications.show_welcome_notification()

        # Run the icon in a separate thread so main thread can handle signals
        logging.info("NotifyMe is running in the system tray")
        logging.info(
            (
                "Blink interval: %s minutes, Walking interval: %s minutes,"
                " Water interval: %s minutes, Pranayama interval: %s minutes"
            ),
            self.config.interval_minutes,
            self.config.walking_interval_minutes,
            self.config.water_interval_minutes,
            self.config.pranayama_interval_minutes,
        )
        logging.info("NotifyMe version: %s", self.updater.get_current_version())
        print("NotifyMe is running. Press Ctrl+C to quit.")

        self.icon.run_detached()

        # Main thread waits for Ctrl+C or explicit quit
        try:
            while True:
                if not any(
                    timer.is_running for timer in self.timers.timers.values()
                ) and (not self.icon or not self.icon.visible):
                    break
                time.sleep(0.5)
        except KeyboardInterrupt:
            print("\nShutting down...")
            logging.info("Received Ctrl+C, shutting down...")
        finally:
            self.quit_app()
