"""
Menu management for the NotifyMe application.

This module handles the creation and management of the system tray menu,
including dynamic menu generation based on visibility settings.
"""

import logging

from pystray import Menu, MenuItem

from notifyme_app.constants import (
    APP_NAME,
    REMINDER_BLINK,
    REMINDER_PRANAYAMA,
    REMINDER_WALKING,
    REMINDER_WATER,
    MenuCallbacks,
)


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
        update_available: bool = False,
        latest_version: str = None,
        sound_enabled: bool = False,
        blink_hidden: bool = False,
        walking_hidden: bool = False,
        water_hidden: bool = False,
        pranayama_hidden: bool = False,
        blink_sound_enabled: bool = True,
        walking_sound_enabled: bool = True,
        water_sound_enabled: bool = True,
        pranayama_sound_enabled: bool = True,
        is_blink_paused: bool = False,
        is_walking_paused: bool = False,
        is_water_paused: bool = False,
        is_pranayama_paused: bool = False,
        is_paused: bool = False,
        interval_minutes: int = 20,
        walking_interval_minutes: int = 60,
        water_interval_minutes: int = 30,
        pranayama_interval_minutes: int = 120,
        tts_enabled: bool = False,
        blink_tts_enabled: bool = True,
        walking_tts_enabled: bool = True,
        water_tts_enabled: bool = True,
        pranayama_tts_enabled: bool = True,
    ) -> Menu:
        """Create the system tray menu with current state."""
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

        # Blink reminder menu
        if not blink_hidden:
            blink_menu = self._create_reminder_menu(
                "👁 Blink Reminder",
                REMINDER_BLINK,
                is_blink_paused,
                blink_sound_enabled,
                sound_enabled,
                tts_enabled,
                # TTS flag for blink
                blink_tts_enabled,
                interval_minutes,
                [10, 15, 20, 30, 45, 60],
                is_paused,
            )
            reminder_menus.append(blink_menu)

        # Walking reminder menu
        if not walking_hidden:
            walking_menu = self._create_reminder_menu(
                "🚶 Walking Reminder",
                REMINDER_WALKING,
                is_walking_paused,
                walking_sound_enabled,
                sound_enabled,
                tts_enabled,
                # TTS flag for walking
                walking_tts_enabled,
                walking_interval_minutes,
                [30, 45, 60, 90, 120],
                is_paused,
            )
            reminder_menus.append(walking_menu)

        # Water reminder menu
        if not water_hidden:
            water_menu = self._create_reminder_menu(
                "💧 Water Reminder",
                REMINDER_WATER,
                is_water_paused,
                water_sound_enabled,
                sound_enabled,
                tts_enabled,
                # TTS flag for water
                water_tts_enabled,
                water_interval_minutes,
                [20, 30, 45, 60, 90],
                is_paused,
            )
            reminder_menus.append(water_menu)

        # Pranayama reminder menu
        if not pranayama_hidden:
            pranayama_menu = self._create_reminder_menu(
                "🧘 Pranayama Reminder",
                REMINDER_PRANAYAMA,
                is_pranayama_paused,
                pranayama_sound_enabled,
                sound_enabled,
                tts_enabled,
                # TTS flag for pranayama
                pranayama_tts_enabled,
                pranayama_interval_minutes,
                [60, 90, 120, 180, 240],
                is_paused,
            )
            reminder_menus.append(pranayama_menu)

        # Build hidden reminders menu
        hidden_items = []
        if blink_hidden:
            hidden_items.append(
                MenuItem(
                    "👁 Show Blink Reminder",
                    self.callbacks[MenuCallbacks.TOGGLE_BLINK_HIDDEN],
                )
            )
        if walking_hidden:
            hidden_items.append(
                MenuItem(
                    "🚶 Show Walking Reminder",
                    self.callbacks[MenuCallbacks.TOGGLE_WALKING_HIDDEN],
                )
            )
        if water_hidden:
            hidden_items.append(
                MenuItem(
                    "💧 Show Water Reminder",
                    self.callbacks[MenuCallbacks.TOGGLE_WATER_HIDDEN],
                )
            )
        if pranayama_hidden:
            hidden_items.append(
                MenuItem(
                    "🧘 Show Pranayama Reminder",
                    self.callbacks[MenuCallbacks.TOGGLE_PRANAYAMA_HIDDEN],
                )
            )

        # Build the main menu
        menu_items = [
            update_item,
            Menu.SEPARATOR,
            MenuItem(
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
            ),
            MenuItem(
                "💤 Snooze (5 min)",
                self.callbacks[MenuCallbacks.SNOOZE_REMINDER],
            ),
            Menu.SEPARATOR,
            MenuItem(
                "🔔 Test Notifications",
                Menu(
                    MenuItem(
                        "👁 Test Blink",
                        self.callbacks[MenuCallbacks.TEST_BLINK_NOTIFICATION],
                    ),
                    MenuItem(
                        "🚶 Test Walking",
                        self.callbacks[MenuCallbacks.TEST_WALKING_NOTIFICATION],
                    ),
                    MenuItem(
                        "💧 Test Water",
                        self.callbacks[MenuCallbacks.TEST_WATER_NOTIFICATION],
                    ),
                    MenuItem(
                        "🧘 Test Pranayama",
                        self.callbacks[MenuCallbacks.TEST_PRANAYAMA_NOTIFICATION],
                    ),
                ),
            ),
            Menu.SEPARATOR,
        ]

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
                MenuItem(
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
                ),
                Menu.SEPARATOR,
                MenuItem(
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
                ),
                Menu.SEPARATOR,
                MenuItem("❌ Quit", self.callbacks[MenuCallbacks.QUIT_APP]),
            ]
        )

        return Menu(*menu_items)

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
