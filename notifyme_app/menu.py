"""
Menu management for the NotifyMe application.

This module handles the creation and management of the system tray menu,
including dynamic menu generation based on visibility settings.
"""

import logging
from typing import cast

from pystray import Menu, MenuItem

from notifyme_app.constants import (
    ALL_MEDICINE_TIMES,
    ALL_REMINDER_TYPES,
    APP_NAME,
    REMINDER_CONFIGS,
    MedicineTimeLabels,
    MenuCallbacks,
    ReminderConfigKeys,
)


class ReminderStateKeys:
    """Keys used in reminder state dictionaries."""

    HIDDEN = "hidden"
    PAUSED = "paused"
    SOUND_ENABLED = "sound_enabled"
    TTS_ENABLED = "tts_enabled"
    INTERVAL_MINUTES = "interval_minutes"


class MenuManager:
    """Manages the system tray menu for the application."""

    def __init__(self, app_callbacks: dict):
        """Initialize the menu manager with application callbacks.

        Args:
            app_callbacks: Dictionary of callback functions from the main app
        """
        self.callbacks = app_callbacks

    def create_menu(
        self,
        reminder_states: dict,
        is_paused: bool = False,
        sound_enabled: bool = False,
        tts_enabled: bool = False,
        update_available: bool = False,
        latest_version: str | None = None,
        medicine_enabled: bool = True,
        medicine_completions: dict | None = None,
    ) -> Menu:
        """Create the system tray menu with current state.

        Args:
            reminder_states: Dict of reminder states keyed by reminder type.
                Each state dict should contain: hidden, paused, sound_enabled,
                tts_enabled, interval_minutes
            is_paused: Global pause state
            sound_enabled: Global sound enabled state
            tts_enabled: Global TTS enabled state
            update_available: Whether an update is available
            latest_version: Latest version string if update available
            medicine_enabled: Whether medicine reminders are enabled
            medicine_completions: Dict of completed meal times for today

        Returns:
            Menu object for the system tray
        """
        logging.debug("Creating system tray menu with current application state")

        # Update status
        if update_available and latest_version:
            update_label = f"⬆ Update available: v{latest_version}"
            update_item = MenuItem(
                update_label, self.callbacks[MenuCallbacks.OPEN_GITHUB_RELEASES]
            )
            logging.info("Update available: %s", latest_version)
        else:
            update_item = MenuItem("✅ Up to date", None, enabled=False)

        # Build reminder menu items dynamically based on visibility
        reminder_menus = []
        hidden_items = []

        for reminder_type in ALL_REMINDER_TYPES:
            config = REMINDER_CONFIGS[reminder_type]
            state = reminder_states.get(
                reminder_type,
                {
                    ReminderStateKeys.HIDDEN: False,
                    ReminderStateKeys.PAUSED: False,
                    ReminderStateKeys.SOUND_ENABLED: True,
                    ReminderStateKeys.TTS_ENABLED: True,
                    ReminderStateKeys.INTERVAL_MINUTES: config[
                        ReminderConfigKeys.DEFAULT_INTERVAL
                    ],
                },
            )

            if not state.get(ReminderStateKeys.HIDDEN, False):
                # Create menu for visible reminder
                display_title = cast(str, config[ReminderConfigKeys.DISPLAY_TITLE])
                interval_options = cast(
                    list[int], config[ReminderConfigKeys.INTERVAL_OPTIONS]
                )
                default_interval = cast(
                    int, config[ReminderConfigKeys.DEFAULT_INTERVAL]
                )

                reminder_menu = self._create_reminder_menu(
                    display_title,
                    reminder_type,
                    state.get(ReminderStateKeys.PAUSED, False),
                    state.get(ReminderStateKeys.SOUND_ENABLED, True),
                    sound_enabled,
                    tts_enabled,
                    state.get(ReminderStateKeys.TTS_ENABLED, True),
                    state.get(ReminderStateKeys.INTERVAL_MINUTES, default_interval),
                    interval_options,
                    is_paused,
                )
                reminder_menus.append(reminder_menu)
            else:
                # Add to hidden items list
                hidden_items.append(
                    MenuItem(
                        f"{config['icon']} Show {config['notification_title']}",
                        self.callbacks[f"toggle_{reminder_type}_hidden"],
                    )
                )

        # Build the main menu
        menu_items = [
            update_item,
            Menu.SEPARATOR,
            self._create_global_controls_menu(sound_enabled, tts_enabled),
            MenuItem(
                "💤 Snooze (5 min)",
                self.callbacks[MenuCallbacks.SNOOZE_REMINDER],
            ),
            Menu.SEPARATOR,
        ]

        # Build test notifications menu dynamically
        test_notification_items = []
        for reminder_type in ALL_REMINDER_TYPES:
            config = REMINDER_CONFIGS[reminder_type]
            test_notification_items.append(
                MenuItem(
                    f"{config['icon']} Test {config['notification_title']}",
                    self.callbacks[f"test_{reminder_type}_notification"],
                )
            )

        menu_items.append(
            MenuItem("🔔 Test Notifications", Menu(*test_notification_items))
        )
        menu_items.append(Menu.SEPARATOR)

        # Add medicine menu
        medicine_completions = medicine_completions or {}
        menu_items.append(
            self._create_medicine_menu(medicine_enabled, medicine_completions)
        )
        menu_items.append(Menu.SEPARATOR)

        # Add visible reminder menus
        menu_items.extend(reminder_menus)

        # Add hidden reminders menu if there are any hidden
        if hidden_items:
            menu_items.append(Menu.SEPARATOR)
            menu_items.append(MenuItem("👁 Hidden Reminders", Menu(*hidden_items)))

        # Add remaining menu items
        menu_items.extend(
            [
                Menu.SEPARATOR,
                self._create_help_menu_item(),
                Menu.SEPARATOR,
                self._create_open_locations_menu_item(),
                Menu.SEPARATOR,
                MenuItem("❌ Quit", self.callbacks[MenuCallbacks.QUIT_APP]),
            ]
        )

        return Menu(*menu_items)

    def _create_global_controls_menu(
        self, sound_enabled: bool, tts_enabled: bool
    ) -> MenuItem:
        """Create the global controls submenu entry."""
        return MenuItem(
            "⚙ Controls",
            Menu(
                MenuItem(
                    "▶ Start",
                    self.callbacks[MenuCallbacks.START_REMINDERS],
                    default=True,
                ),
                MenuItem(
                    "⏸ Pause All",
                    self.callbacks[MenuCallbacks.PAUSE_REMINDERS],
                ),
                MenuItem(
                    "▶ Resume All",
                    self.callbacks[MenuCallbacks.RESUME_REMINDERS],
                ),
                Menu.SEPARATOR,
                MenuItem(
                    "🔊 Global Sound",
                    self.callbacks[MenuCallbacks.TOGGLE_SOUND],
                    checked=lambda _: sound_enabled,
                ),
                MenuItem(
                    "🗣️ Global TTS",
                    self.callbacks.get(MenuCallbacks.TOGGLE_TTS, lambda: None),
                    checked=lambda _: tts_enabled,
                ),
            ),
        )

    def _create_help_menu_item(self) -> MenuItem:
        """Create the help submenu entry."""
        return MenuItem(
            "❓ Help",
            Menu(
                MenuItem(
                    "🌐 User Guide",
                    self.callbacks[MenuCallbacks.OPEN_HELP],
                ),
                MenuItem(
                    "📖 Online Documentation",
                    self.callbacks[MenuCallbacks.OPEN_GITHUB_PAGES],
                ),
                Menu.SEPARATOR,
                MenuItem(
                    "🔄 Check for Updates",
                    self.callbacks[MenuCallbacks.CHECK_FOR_UPDATES_ASYNC],
                ),
                MenuItem(
                    f"ℹ️ About {APP_NAME}",
                    self.callbacks[MenuCallbacks.SHOW_ABOUT],
                ),
                Menu.SEPARATOR,
                MenuItem(
                    "🐙 GitHub Repository",
                    self.callbacks[MenuCallbacks.OPEN_GITHUB],
                ),
                MenuItem(
                    "⬆ Releases",
                    self.callbacks[MenuCallbacks.OPEN_GITHUB_RELEASES],
                ),
            ),
        )

    def _create_open_locations_menu_item(self) -> MenuItem:
        """Create the open locations submenu entry."""
        return MenuItem(
            "📂 Open Locations",
            Menu(
                MenuItem(
                    "📄 Log Location",
                    self.callbacks[MenuCallbacks.OPEN_LOG_LOCATION],
                ),
                MenuItem(
                    "⚙ Config Location",
                    self.callbacks[MenuCallbacks.OPEN_CONFIG_LOCATION],
                ),
                MenuItem(
                    "📦 App Location",
                    self.callbacks[MenuCallbacks.OPEN_EXE_LOCATION],
                ),
            ),
        )

    def _create_reminder_menu(
        self,
        title: str,
        reminder_type: str,
        is_paused: bool,
        sound_enabled: bool,
        global_sound_enabled: bool,
        # global tts enabled flag
        global_tts_enabled: bool,
        # per-reminder tts enabled flag
        tts_enabled: bool,
        current_interval: int,
        interval_options: list[int],
        global_paused: bool,
    ) -> MenuItem:
        """Create a menu for a specific reminder type."""
        # Create interval menu items
        interval_items = []
        for interval in interval_options:
            interval_items.append(
                MenuItem(
                    f"{interval} minutes",
                    self.callbacks[f"set_{reminder_type}_interval"](interval),
                    checked=lambda _, i=interval: current_interval == i,
                    enabled=not is_paused and not global_paused,
                )
            )

        # Create the reminder submenu
        submenu_items = [
            MenuItem(
                "⏸ Pause/Resume",
                self.callbacks[f"toggle_{reminder_type}_pause"],
                checked=lambda _, paused=is_paused: (
                    not paused
                ),  # Checked when NOT paused (running)
            ),
            MenuItem(
                "🔊 Sound",
                self.callbacks[f"toggle_{reminder_type}_sound"],
                checked=lambda _: global_sound_enabled and sound_enabled,
            ),
            MenuItem(
                "🗣️ TTS",
                self.callbacks.get(f"toggle_{reminder_type}_tts", lambda: None),
                checked=lambda _: tts_enabled and global_tts_enabled,
            ),
            MenuItem(
                "🙈 Hide Reminder", self.callbacks[f"toggle_{reminder_type}_hidden"]
            ),
            Menu.SEPARATOR,
        ]
        submenu_items.extend(interval_items)

        return MenuItem(title, Menu(*submenu_items))

    def _create_medicine_menu(
        self, medicine_enabled: bool, medicine_completions: dict
    ) -> MenuItem:
        """Create the medicine reminders menu."""
        # Build mark completed items
        completion_items = []
        for meal_time in ALL_MEDICINE_TIMES:
            meal_label = MedicineTimeLabels.get(meal_time, meal_time.title())
            is_completed = meal_time in medicine_completions

            if is_completed:
                completion_items.append(
                    MenuItem(
                        f"✅ {meal_label} (Completed)",
                        None,
                        enabled=False,
                    )
                )
            else:
                callback_key = getattr(
                    MenuCallbacks,
                    f"MARK_{meal_time.upper()}_COMPLETED",
                    None,
                )
                if callback_key:
                    completion_items.append(
                        MenuItem(
                            f"☑️ Mark {meal_label} Complete",
                            self.callbacks.get(callback_key, lambda: None),
                        )
                    )

        # Build submenu
        submenu_items = [
            MenuItem(
                "⚙️ Manage Medicines",
                self.callbacks.get(MenuCallbacks.MANAGE_MEDICINES, lambda: None),
            ),
            Menu.SEPARATOR,
            MenuItem(
                "✓ Enable Medicine Reminders",
                self.callbacks.get(MenuCallbacks.TOGGLE_MEDICINE_ENABLED, lambda: None),
                checked=lambda _: medicine_enabled,
            ),
            Menu.SEPARATOR,
        ]
        submenu_items.extend(completion_items)

        return MenuItem("💊 Medicine Reminders", Menu(*submenu_items))
