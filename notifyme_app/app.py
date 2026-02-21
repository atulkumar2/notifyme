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
from notifyme_app.menu import MenuManager, ReminderStateKeys
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
        self.last_reminder_shown_at: dict[str, float | None] = {
            reminder_type: None for reminder_type in ALL_REMINDER_TYPES
        }

        # Initialize timers
        self._setup_timers()

        logging.info("Application initialized")

    def _setup_timers(self) -> None:
        """Set up reminder timers with callbacks."""
        for reminder_type in ALL_REMINDER_TYPES:
            self.timers.create_timer(
                reminder_type,
                self.config.get_reminder_interval_minutes(reminder_type),
                self._create_reminder_handler(reminder_type),
            )

    def _create_reminder_handler(self, reminder_type: str):
        """Create a reminder handler for a specific reminder type.

        Returns a callable that handles the reminder trigger.
        """

        def handler() -> None:
            if not self.config.get_reminder_hidden(reminder_type):
                sound_enabled = (
                    self.config.sound_enabled
                    and self.config.get_reminder_sound_enabled(reminder_type)
                )
                message = self.notifications.show_reminder_notification(
                    reminder_type,
                    self.last_reminder_shown_at[reminder_type],
                    sound_enabled,
                )
                self.last_reminder_shown_at[reminder_type] = time.time()

                try:
                    if self.config.tts_enabled or self.config.get_reminder_tts_enabled(
                        reminder_type
                    ):
                        # Strip emoji icon from the beginning, keep the rest of the message
                        tts_message = message.lstrip("🌿👁️🥤🙏 ").strip()
                        speak_once(tts_message, lang=self.config.tts_language)
                except Exception as e:
                    logging.error(
                        "Error invoking TTS for %s reminder: %s", reminder_type, e
                    )

        return handler

    def _get_menu_callbacks(self) -> dict:
        """Get callback functions for menu items.

        Builds callbacks dynamically for each reminder type to avoid code duplication.
        """
        callbacks = {
            # Control callbacks
            MenuCallbacks.START_REMINDERS: self.start_reminders,
            MenuCallbacks.PAUSE_REMINDERS: self.pause_reminders,
            MenuCallbacks.RESUME_REMINDERS: self.resume_reminders,
            MenuCallbacks.SNOOZE_REMINDER: self.snooze_reminder,
            MenuCallbacks.QUIT_APP: self.quit_app,
            # Global toggles
            MenuCallbacks.TOGGLE_SOUND: self.toggle_sound,
            MenuCallbacks.TOGGLE_TTS: self.toggle_tts,
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

        # Dynamically add reminder-specific callbacks for all reminder types
        for reminder_type in ALL_REMINDER_TYPES:
            # Sound callbacks - called directly by pystray, wrap to ignore extra args
            callbacks[f"toggle_{reminder_type}_sound"] = (
                lambda *_, rt=reminder_type, **__: self._toggle_reminder_sound(rt)
            )
            # TTS callbacks - called directly by pystray
            callbacks[f"toggle_{reminder_type}_tts"] = (
                lambda *_, rt=reminder_type, **__: self._toggle_reminder_tts(rt)
            )
            # Hidden callbacks - called directly by pystray
            callbacks[f"toggle_{reminder_type}_hidden"] = (
                lambda *_, rt=reminder_type, **__: self._toggle_reminder_hidden(rt)
            )
            # Pause callbacks - called directly by pystray
            callbacks[f"toggle_{reminder_type}_pause"] = (
                lambda *_, rt=reminder_type, **__: self._toggle_reminder_pause(rt)
            )
            # Interval callbacks - called from menu code with explicit arguments
            callbacks[f"set_{reminder_type}_interval"] = (
                lambda minutes, rt=reminder_type: self._set_reminder_interval(
                    rt, minutes
                )
            )
            # Test notification callbacks - called directly by pystray
            callbacks[f"test_{reminder_type}_notification"] = (
                lambda *_, rt=reminder_type, **__: self._test_reminder_notification(rt)
            )

        return callbacks

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

    def _toggle_reminder_sound(self, reminder_type: str) -> None:
        """Toggle sound for a specific reminder type."""
        current = self.config.get_reminder_sound_enabled(reminder_type)
        self.config.set_reminder_sound_enabled(reminder_type, not current)
        new_state = "enabled" if not current else "disabled"
        logging.info("%s sound %s", reminder_type.title(), new_state)
        self.update_menu()

    # TTS control methods
    def toggle_tts(self) -> None:
        """Toggle global Text-to-Speech on/off."""
        self.config.tts_enabled = not self.config.tts_enabled
        logging.info(
            "Global TTS %s", "enabled" if self.config.tts_enabled else "disabled"
        )
        self.update_menu()

    def _toggle_reminder_tts(self, reminder_type: str) -> None:
        """Toggle TTS for a specific reminder type."""
        current = self.config.get_reminder_tts_enabled(reminder_type)
        self.config.set_reminder_tts_enabled(reminder_type, not current)
        new_state = "enabled" if not current else "disabled"
        logging.info("%s TTS %s", reminder_type.title(), new_state)
        self.update_menu()

    # Visibility control methods
    def _toggle_reminder_hidden(self, reminder_type: str) -> None:
        """Toggle visibility for a specific reminder type."""
        current = self.config.get_reminder_hidden(reminder_type)
        self.config.set_reminder_hidden(reminder_type, not current)
        new_state = "hidden" if not current else "visible"
        logging.info("%s reminder %s", reminder_type.title(), new_state)
        self.update_menu()

    # Pause control methods
    def _toggle_reminder_pause(self, reminder_type: str) -> None:
        """Toggle pause state for a specific reminder type."""
        self.timers.toggle_timer_pause(reminder_type)
        self.update_icon_title()
        self.update_menu()

    # Interval setting methods
    def _set_reminder_interval(self, reminder_type: str, minutes: int):
        """Set interval for a specific reminder type.

        Returns a callable for use as a menu callback.
        """

        def _set():
            self.config.set_reminder_interval_minutes(reminder_type, minutes)
            self.timers.update_timer_interval(reminder_type, minutes)
            logging.info(
                "%s interval set to %s minutes", reminder_type.title(), minutes
            )
            self.update_icon_title()

        return _set

    # Test notification methods
    def _test_reminder_notification(self, reminder_type: str) -> None:
        """Trigger a test notification for a specific reminder type."""
        logging.info("User requested test %s notification", reminder_type)
        try:
            # Show notification sound based on global or reminder-specific setting
            sound_enabled = (
                self.config.sound_enabled
                or self.config.get_reminder_sound_enabled(reminder_type)
            )

            # Show the notification
            message = self.notifications.show_reminder_notification(
                reminder_type, None, sound_enabled
            )

            # Optionally speak using TTS
            if self.config.tts_enabled or self.config.get_reminder_tts_enabled(
                reminder_type
            ):
                # Strip emoji icon from the beginning, keep the rest of the message
                tts_message = message.lstrip("🌿👁️🥤🙏 ").strip()
                speak_once(
                    tts_message,
                    lang=self.config.tts_language,
                )
            logging.info("Test %s notification displayed successfully", reminder_type)
        except Exception as e:
            logging.error("Failed to show test %s notification: %s", reminder_type, e)

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
            REMINDER_BLINK: "blink_interval_minutes",
            REMINDER_WALKING: "walking_interval_minutes",
            REMINDER_WATER: "water_interval_minutes",
            REMINDER_PRANAYAMA: "pranayama_interval_minutes",
        }

        reminder_states = {}
        for reminder_type in ALL_REMINDER_TYPES:
            interval_property = interval_property_map.get(
                reminder_type, "blink_interval_minutes"
            )
            reminder_states[reminder_type] = {
                ReminderStateKeys.HIDDEN: getattr(
                    self.config, f"{reminder_type}_hidden", False
                ),
                ReminderStateKeys.PAUSED: self.timers.is_timer_paused(reminder_type),
                ReminderStateKeys.SOUND_ENABLED: getattr(
                    self.config, f"{reminder_type}_sound_enabled", True
                ),
                ReminderStateKeys.TTS_ENABLED: getattr(
                    self.config, f"{reminder_type}_tts_enabled", True
                ),
                ReminderStateKeys.INTERVAL_MINUTES: getattr(
                    self.config, interval_property, 20
                ),
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
        status_parts = []
        for reminder_type in ALL_REMINDER_TYPES:
            status = (
                "⏸"
                if self.timers.is_timer_paused(reminder_type)
                else f"{self.config.get_reminder_interval_minutes(reminder_type)}min"
            )
            status_parts.append(f"{reminder_type.title()}: {status}")

        self.icon.title = ", ".join(status_parts)

    def get_initial_title(self) -> str:
        """Get the initial title for the system tray icon."""
        status_parts = []
        for reminder_type in ALL_REMINDER_TYPES:
            status_parts.append(
                f"{reminder_type.title()}: {self.config.get_reminder_interval_minutes(reminder_type)}min"
            )
        return ", ".join(status_parts)

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
            self.config.get_reminder_interval_minutes(REMINDER_BLINK),
            self.config.get_reminder_interval_minutes(REMINDER_WALKING),
            self.config.get_reminder_interval_minutes(REMINDER_WATER),
            self.config.get_reminder_interval_minutes(REMINDER_PRANAYAMA),
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
