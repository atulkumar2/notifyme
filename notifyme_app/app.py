"""
Main application class for the NotifyMe reminder system.

This module contains the main NotifyMeApp class that coordinates all the
different components of the application including timers, notifications,
configuration, and system tray integration.
"""

import logging
import os
import subprocess
import sys
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

from pystray import Icon
from winotify import Notification

from notifyme_app.config import ConfigManager
from notifyme_app.constants import (
    ALL_MEDICINE_TIMES,
    ALL_REMINDER_TYPES,
    APP_NAME,
    APP_REMINDER_APP_ID,
    APP_VERSION,
    MEDICINE_BREAKFAST,
    MEDICINE_DINNER,
    MEDICINE_LUNCH,
    REMINDER_BLINK,
    REMINDER_PRANAYAMA,
    REMINDER_WALKING,
    REMINDER_WATER,
    MedicineTimeLabels,
    MenuCallbacks,
)
from notifyme_app.medicine import MedicineManager
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
        self.medicine_manager = MedicineManager()

        # Create menu manager with callbacks
        self.menu_manager = MenuManager(self._get_menu_callbacks())

        # Application state
        self.icon = None
        self.last_reminder_shown_at: dict[str, float | None] = {
            reminder_type: None for reminder_type in ALL_REMINDER_TYPES
        }
        self.last_medicine_reminder_at: dict[str, float | None] = {
            meal_time: None for meal_time in ALL_MEDICINE_TIMES
        }

        # Initialize timers
        self._setup_timers()
        self._setup_medicine_timers()

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

    def _setup_medicine_timers(self) -> None:
        """Set up medicine reminder timers for each meal time."""
        if not self.config.medicine_enabled:
            logging.info("Medicine reminders disabled")
            return

        interval = self.config.medicine_reminder_interval
        for meal_time in ALL_MEDICINE_TIMES:
            self.timers.create_timer(
                f"medicine_{meal_time}",
                interval,
                self._create_medicine_handler(meal_time),
            )
        logging.info("Medicine timers set up")

    def _create_medicine_handler(self, meal_time: str):
        """Create a medicine reminder handler for a specific meal time."""

        def handler() -> None:
            if not self.config.medicine_enabled:
                return

            if self.medicine_manager.should_remind(meal_time):
                medicines = self.medicine_manager.get_medicines_for_meal_time(meal_time)
                if medicines:
                    self._show_medicine_notification(meal_time, medicines)
                    self.last_medicine_reminder_at[meal_time] = time.time()

        return handler

    def _show_medicine_notification(self, meal_time: str, medicines: list) -> None:
        """Show notification for medicine reminder."""
        try:
            meal_label = MedicineTimeLabels.get(meal_time, meal_time.title())

            # Build medicine list
            medicine_names = [f"• {m.name} ({m.dosage})" for m in medicines]
            medicine_list = "\n".join(medicine_names)

            title = f"💊 {meal_label} Medicine Reminder"
            message = f"Time to take your medicine:\n{medicine_list}\n\nClick to mark as completed."

            # Create notification with action buttons
            notification = Notification(
                app_id=APP_REMINDER_APP_ID,
                title=title,
                msg=message,
            )

            # Add action button to mark as completed
            notification.add_actions(
                label="Mark Completed", launch=f"medicine_completed:{meal_time}"
            )

            notification.show()

            # TTS
            if self.config.tts_enabled:
                tts_message = (
                    f"{meal_label} medicine reminder. Time to take your medicine."
                )
                speak_once(tts_message, lang=self.config.tts_language)

            logging.info("Showed %s medicine notification", meal_time)
        except Exception as e:
            logging.error("Failed to show medicine notification: %s", e)

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
            # Medicine callbacks
            MenuCallbacks.ADD_MEDICINE: self.add_medicine_quick,
            MenuCallbacks.MANAGE_MEDICINES: self.manage_medicines,
            MenuCallbacks.MARK_BREAKFAST_COMPLETED: lambda *_, **__: (
                self.mark_medicine_completed(MEDICINE_BREAKFAST)
            ),
            MenuCallbacks.MARK_LUNCH_COMPLETED: lambda *_, **__: (
                self.mark_medicine_completed(MEDICINE_LUNCH)
            ),
            MenuCallbacks.MARK_DINNER_COMPLETED: lambda *_, **__: (
                self.mark_medicine_completed(MEDICINE_DINNER)
            ),
            MenuCallbacks.TOGGLE_MEDICINE_ENABLED: self.toggle_medicine_enabled,
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
                lambda *_, minutes=None, rt=reminder_type, **__: (
                    self._set_reminder_interval(rt, minutes)
                    if minutes is not None
                    else None
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
    def _set_reminder_interval(self, reminder_type: str, minutes: int) -> None:
        """Set interval for a specific reminder type."""
        self.config.set_reminder_interval_minutes(reminder_type, minutes)
        self.timers.update_timer_interval(reminder_type, minutes)
        logging.info("%s interval set to %s minutes", reminder_type.title(), minutes)
        self.update_icon_title()

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

    # Medicine reminder methods
    def add_medicine_quick(self) -> None:
        """Open a simplified add-medicine dialog."""
        try:
            standalone_module = Path(__file__).parent / "medicine_ui_standalone.py"
            env = os.environ.copy()

            # Determine the Python executable to use
            if getattr(sys, "frozen", False):
                # In frozen mode, try to find python in the environment
                # or use the embedded python
                import shutil

                executable = shutil.which("python") or shutil.which("python3")
                if not executable:
                    # If no python found, fall back to main exe with --add-medicine flag
                    exe_path = Path(sys.executable)
                    logging.info(
                        "Launching frozen exe with --add-medicine flag: %s", exe_path
                    )
                    # Don't hide the window for the add-medicine dialog
                    subprocess.Popen([str(exe_path), "--add-medicine"])
                    logging.info("Opened add medicine dialog (frozen)")
                    return
            else:
                executable = sys.executable
                if sys.platform == "win32" and executable.endswith("python.exe"):
                    executable = executable.replace("python.exe", "pythonw.exe")

            logging.info("Launching medicine dialog with: %s", executable)
            kwargs = {
                "cwd": str(Path(__file__).parent.parent),
                "env": env,
                "stdin": subprocess.DEVNULL,
                "stdout": subprocess.DEVNULL,
                "stderr": subprocess.PIPE,  # Capture stderr to log errors
            }

            if sys.platform == "win32":
                kwargs["creationflags"] = 0x08000000  # CREATE_NO_WINDOW

            subprocess.Popen(
                [executable, "-u", str(standalone_module), "--add"], **kwargs
            )
            logging.info("Opened add medicine dialog")
        except Exception as e:
            logging.error("Failed to open add medicine dialog: %s", e, exc_info=True)

    def manage_medicines(self) -> None:
        """Open the medicine management window in a separate subprocess."""
        try:
            # If running as a frozen/compiled app (PyInstaller), run in a thread instead
            # of subprocess to avoid spawning a new instance of the entire app
            if getattr(sys, "frozen", False):

                def open_medicine_ui() -> None:
                    try:
                        import tkinter as tk

                        from notifyme_app.medicine import MedicineManager
                        from notifyme_app.medicine_ui import MedicineManagementWindow

                        # Create a new root window
                        root = tk.Tk()
                        root.title("Medicine Management")
                        root.geometry("800x600")

                        # Create and display the medicine management window
                        medicine_manager = MedicineManager()
                        window = MedicineManagementWindow(root, medicine_manager)

                        # Run the window's event loop
                        root.mainloop()
                    except Exception as e:
                        logging.error("Error in medicine UI: %s", e, exc_info=True)

                # Run in a daemon thread so it doesn't block the main app
                thread = threading.Thread(target=open_medicine_ui, daemon=True)
                thread.start()
                logging.info("Opened medicine management UI")
            else:
                # If running as a regular Python script, use subprocess
                standalone_module = Path(__file__).parent / "medicine_ui_standalone.py"
                env = os.environ.copy()

                # Use pythonw.exe on Windows
                executable = sys.executable
                if sys.platform == "win32" and executable.endswith("python.exe"):
                    executable = executable.replace("python.exe", "pythonw.exe")

                kwargs = {
                    "cwd": str(Path(__file__).parent.parent),
                    "env": env,
                    "stdin": subprocess.DEVNULL,
                    "stdout": subprocess.DEVNULL,
                    "stderr": subprocess.DEVNULL,
                }

                if sys.platform == "win32":
                    kwargs["creationflags"] = 0x08000000  # CREATE_NO_WINDOW

                subprocess.Popen([executable, "-u", str(standalone_module)], **kwargs)
                logging.info("Opened medicine management UI")
        except Exception as e:
            logging.error("Failed to open medicine management: %s", e)

    def mark_medicine_completed(self, meal_time: str) -> None:
        """Mark medicine as completed for a specific meal time."""
        try:
            self.medicine_manager.mark_completed(meal_time)
            meal_label = MedicineTimeLabels.get(meal_time, meal_time.title())

            # Show confirmation notification
            notification = Notification(
                app_id=APP_REMINDER_APP_ID,
                title=f"✅ {meal_label} Medicine Completed",
                msg=f"Marked {meal_label} medicine as taken for today.",
            )
            notification.show()

            logging.info("Marked %s medicine as completed", meal_time)
            self.update_menu()
        except Exception as e:
            logging.error("Failed to mark medicine completed: %s", e)

    def toggle_medicine_enabled(self) -> None:
        """Toggle medicine reminders on/off."""
        self.config.medicine_enabled = not self.config.medicine_enabled
        logging.info(
            "Medicine reminders %s",
            "enabled" if self.config.medicine_enabled else "disabled",
        )

        # Show notification
        status = "enabled" if self.config.medicine_enabled else "disabled"
        notification = Notification(
            app_id=APP_REMINDER_APP_ID,
            title="💊 Medicine Reminders",
            msg=f"Medicine reminders have been {status}.",
        )
        notification.show()

        self.update_menu()

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
            # Get today's medicine completions

            today = datetime.now().strftime("%Y-%m-%d")
            medicine_completions = self.medicine_manager.completions.get(today, {})

            self.icon.menu = self.menu_manager.create_menu(
                reminder_states=self._build_reminder_states(),
                is_paused=self.timers.is_global_paused,
                sound_enabled=self.config.sound_enabled,
                tts_enabled=self.config.tts_enabled,
                update_available=self.updater.is_update_available(),
                latest_version=self.updater.get_latest_version(),
                medicine_enabled=self.config.medicine_enabled,
                medicine_completions=medicine_completions,
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
                f"{reminder_type.title()}: "
                f"{self.config.get_reminder_interval_minutes(reminder_type)}min"
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

        # Get today's medicine completions
        today = datetime.now().strftime("%Y-%m-%d")
        medicine_completions = self.medicine_manager.completions.get(today, {})

        self.icon = Icon(
            APP_NAME,
            icon_image,
            self.get_initial_title(),
            menu=self.menu_manager.create_menu(
                reminder_states=self._build_reminder_states(),
                is_paused=False,
                sound_enabled=self.config.sound_enabled,
                tts_enabled=self.config.tts_enabled,
                medicine_enabled=self.config.medicine_enabled,
                medicine_completions=medicine_completions,
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
