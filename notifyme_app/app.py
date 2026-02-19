"""
Main application class for the NotifyMe reminder system.

This module contains the main NotifyMeApp class that coordinates all the
different components of the application including timers, notifications,
configuration, and system tray integration.
"""

import logging
import time
from typing import TYPE_CHECKING

from pystray import Icon
from winotify import Notification

from notifyme_app.config import ConfigManager
from notifyme_app.constants import (
    ALL_REMINDER_TYPES,
    APP_NAME,
    APP_REMINDER_APP_ID,
    APP_VERSION,
    REMINDER_BLINK,
    REMINDER_PRANAYAMA,
    REMINDER_WALKING,
    REMINDER_WATER,
    MenuCallbacks,
)
from notifyme_app.menu import MenuManager
from notifyme_app.notifications import NotificationManager
from notifyme_app.system import SystemManager
from notifyme_app.timers import TimerManager
from notifyme_app.tts import speak_once
from notifyme_app.updater import UpdateChecker

if TYPE_CHECKING:
    pass


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
        self.icon = None
        self.last_blink_shown_at = None
        self.last_walking_shown_at = None
        self.last_water_shown_at = None
        self.last_pranayama_shown_at = None

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
                    speak_text = f"Blink reminder: {message}"
                    speak_once(speak_text, lang=self.config.tts_language)
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
                    speak_once(
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
                    speak_once(
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
                    speak_once(
                        f"Pranayama reminder: {message}", lang=self.config.tts_language
                    )
            except Exception as e:
                logging.error("Error invoking TTS for pranayama reminder: %s", e)

    def _get_menu_callbacks(self) -> dict:
        """Get callback functions for menu items."""
        return {
            # Control callbacks
            MenuCallbacks.START_REMINDERS: self.start_reminders,
            MenuCallbacks.PAUSE_REMINDERS: self.pause_reminders,
            MenuCallbacks.RESUME_REMINDERS: self.resume_reminders,
            MenuCallbacks.SNOOZE_REMINDER: self.snooze_reminder,
            MenuCallbacks.QUIT_APP: self.quit_app,
            # Sound callbacks
            MenuCallbacks.TOGGLE_SOUND: self.toggle_sound,
            MenuCallbacks.TOGGLE_BLINK_SOUND: self.toggle_blink_sound,
            MenuCallbacks.TOGGLE_WALKING_SOUND: self.toggle_walking_sound,
            MenuCallbacks.TOGGLE_WATER_SOUND: self.toggle_water_sound,
            MenuCallbacks.TOGGLE_PRANAYAMA_SOUND: self.toggle_pranayama_sound,
            # TTS callbacks
            MenuCallbacks.TOGGLE_TTS: self.toggle_tts,
            MenuCallbacks.TOGGLE_BLINK_TTS: self.toggle_blink_tts,
            MenuCallbacks.TOGGLE_WALKING_TTS: self.toggle_walking_tts,
            MenuCallbacks.TOGGLE_WATER_TTS: self.toggle_water_tts,
            MenuCallbacks.TOGGLE_PRANAYAMA_TTS: self.toggle_pranayama_tts,
            # Visibility callbacks
            MenuCallbacks.TOGGLE_BLINK_HIDDEN: self.toggle_blink_hidden,
            MenuCallbacks.TOGGLE_WALKING_HIDDEN: self.toggle_walking_hidden,
            MenuCallbacks.TOGGLE_WATER_HIDDEN: self.toggle_water_hidden,
            MenuCallbacks.TOGGLE_PRANAYAMA_HIDDEN: self.toggle_pranayama_hidden,
            # Pause callbacks
            MenuCallbacks.TOGGLE_BLINK_PAUSE: self.toggle_blink_pause,
            MenuCallbacks.TOGGLE_WALKING_PAUSE: self.toggle_walking_pause,
            MenuCallbacks.TOGGLE_WATER_PAUSE: self.toggle_water_pause,
            MenuCallbacks.TOGGLE_PRANAYAMA_PAUSE: self.toggle_pranayama_pause,
            # Interval callbacks
            MenuCallbacks.SET_BLINK_INTERVAL: self.set_interval,
            MenuCallbacks.SET_WALKING_INTERVAL: self.set_walking_interval,
            MenuCallbacks.SET_WATER_INTERVAL: self.set_water_interval,
            MenuCallbacks.SET_PRANAYAMA_INTERVAL: self.set_pranayama_interval,
            # Test callbacks
            MenuCallbacks.TEST_BLINK_NOTIFICATION: self.test_blink_notification,
            MenuCallbacks.TEST_WALKING_NOTIFICATION: self.test_walking_notification,
            MenuCallbacks.TEST_WATER_NOTIFICATION: self.test_water_notification,
            MenuCallbacks.TEST_PRANAYAMA_NOTIFICATION: self.test_pranayama_notification,
            # System callbacks
            MenuCallbacks.OPEN_HELP: self.system.open_help,
            MenuCallbacks.OPEN_GITHUB: self.system.open_github,
            MenuCallbacks.OPEN_GITHUB_PAGES: self.system.open_github_pages,
            MenuCallbacks.OPEN_GITHUB_RELEASES: self.system.open_github_releases,
            MenuCallbacks.OPEN_LOG_LOCATION: self.system.open_log_location,
            MenuCallbacks.OPEN_CONFIG_LOCATION: self.system.open_config_location,
            MenuCallbacks.OPEN_EXE_LOCATION: self.system.open_exe_location,
            # Update callbacks
            MenuCallbacks.CHECK_FOR_UPDATES_ASYNC: self.updater.check_for_updates_async,
            MenuCallbacks.SHOW_ABOUT: self.show_about,
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
                speak_once(
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
                speak_once(
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
                speak_once(
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
                speak_once(
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
                f"{APP_NAME} v{APP_VERSION}\n\n"
                "A health reminder application that helps you:\n"
                "• Blink regularly to prevent eye strain\n"
                "• Take walking breaks for better circulation\n"
                "• Stay hydrated throughout the day\n"
                "• Practice pranayama for stress relief\n\n"
                "Built with Python and love ❤️\n"
                "© 2024 Atul Kumar"
            )

            toast_args = {
                "app_id": APP_REMINDER_APP_ID,
                "title": f"About {APP_NAME}",
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

    def _build_reminder_states(self) -> dict:
        """Build reminder states dictionary from current config and timer states.

        Returns:
            Dictionary keyed by reminder type containing state for each reminder
        """
        # Map reminder types to their interval property names in config
        interval_property_map = {
            REMINDER_BLINK: "interval_minutes",
            REMINDER_WALKING: "walking_interval_minutes",
            REMINDER_WATER: "water_interval_minutes",
            REMINDER_PRANAYAMA: "pranayama_interval_minutes",
        }

        reminder_states = {}
        for reminder_type in ALL_REMINDER_TYPES:
            interval_property = interval_property_map.get(
                reminder_type, "interval_minutes"
            )
            reminder_states[reminder_type] = {
                "hidden": getattr(self.config, f"{reminder_type}_hidden", False),
                "paused": self.timers.is_timer_paused(reminder_type),
                "sound_enabled": getattr(
                    self.config, f"{reminder_type}_sound_enabled", True
                ),
                "tts_enabled": getattr(
                    self.config, f"{reminder_type}_tts_enabled", True
                ),
                "interval_minutes": getattr(self.config, interval_property, 20),
            }
        return reminder_states

    def update_menu(self) -> None:
        """Update the system tray menu to reflect current state."""
        if self.icon:
            self.icon.menu = self.menu_manager.create_menu(
                reminder_states=self._build_reminder_states(),
                is_paused=self.timers.is_global_paused,
                sound_enabled=self.config.sound_enabled,
                tts_enabled=self.config.tts_enabled,
                update_available=self.updater.is_update_available(),
                latest_version=self.updater.get_latest_version(),
            )

    def update_icon_title(self) -> None:
        """Update the system tray icon title based on current state."""
        if not self.icon:
            return

        if self.timers.is_global_paused:
            self.icon.title = f"{APP_NAME} - All Paused"
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
        # No need to stop TTS manager - it's created on-demand and cleans itself up
        logging.info("Application closed")

    def run(self) -> None:
        """Run the application with system tray icon and timers."""
        # Create the icon
        icon_image = self.system.create_icon_image()
        self.icon = Icon(
            APP_NAME,
            icon_image,
            self.get_initial_title(),
            menu=self.menu_manager.create_menu(
                reminder_states=self._build_reminder_states(),
                is_paused=False,
                sound_enabled=self.config.sound_enabled,
                tts_enabled=self.config.tts_enabled,
            ),
        )

        self.updater.check_for_updates_async()

        # Always start reminders on launch
        self.start_reminders()

        # Show startup help and welcome notification
        self.system.show_startup_help()
        self.notifications.show_welcome_notification()

        # Run the icon in a separate thread so main thread can handle signals
        logging.info("%s is running in the system tray", APP_NAME)
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
        logging.info("%s version: %s", APP_NAME, self.updater.get_current_version())
        print(f"{APP_NAME} is running. Press Ctrl+C to quit.")

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
