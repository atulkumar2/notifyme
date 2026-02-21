"""Tests for menu creation."""

import sys
import unittest
from collections.abc import Iterable
from pathlib import Path
from typing import cast

sys.path.insert(0, str(Path(__file__).parent.parent))

from notifyme_app.constants import ALL_REMINDER_TYPES, MenuCallbacks
from notifyme_app.menu import MenuManager, ReminderStateKeys


class TestMenuManager(unittest.TestCase):
    """Tests for MenuManager."""

    def test_global_controls_include_tts(self) -> None:
        """Ensure global controls include the Global TTS toggle."""
        menu_manager = MenuManager(self._build_callbacks())
        reminder_states = self._build_reminder_states()

        menu = menu_manager.create_menu(
            reminder_states=reminder_states,
            is_paused=False,
            sound_enabled=False,
            tts_enabled=True,
            update_available=False,
        )

        labels = self._collect_menu_labels(menu)
        self.assertTrue(any("Global TTS" in label for label in labels))

    def _build_callbacks(self) -> dict:
        callbacks = {
            MenuCallbacks.OPEN_GITHUB_RELEASES: lambda *_: None,
            MenuCallbacks.START_REMINDERS: lambda *_: None,
            MenuCallbacks.PAUSE_REMINDERS: lambda *_: None,
            MenuCallbacks.RESUME_REMINDERS: lambda *_: None,
            MenuCallbacks.TOGGLE_SOUND: lambda *_: None,
            MenuCallbacks.TOGGLE_TTS: lambda *_: None,
            MenuCallbacks.SNOOZE_REMINDER: lambda *_: None,
            MenuCallbacks.OPEN_HELP: lambda *_: None,
            MenuCallbacks.OPEN_GITHUB_PAGES: lambda *_: None,
            MenuCallbacks.CHECK_FOR_UPDATES_ASYNC: lambda *_: None,
            MenuCallbacks.SHOW_ABOUT: lambda *_: None,
            MenuCallbacks.OPEN_GITHUB: lambda *_: None,
            MenuCallbacks.OPEN_LOG_LOCATION: lambda *_: None,
            MenuCallbacks.OPEN_CONFIG_LOCATION: lambda *_: None,
            MenuCallbacks.OPEN_EXE_LOCATION: lambda *_: None,
            MenuCallbacks.QUIT_APP: lambda *_: None,
        }

        def _interval_factory(*_args, **_kwargs):
            return lambda *_: None

        for reminder_type in ALL_REMINDER_TYPES:
            callbacks[f"toggle_{reminder_type}_hidden"] = lambda *_: None
            callbacks[f"toggle_{reminder_type}_pause"] = lambda *_: None
            callbacks[f"toggle_{reminder_type}_sound"] = lambda *_: None
            callbacks[f"toggle_{reminder_type}_tts"] = lambda *_: None
            callbacks[f"set_{reminder_type}_interval"] = _interval_factory
            callbacks[f"test_{reminder_type}_notification"] = lambda *_: None

        return callbacks

    def _build_reminder_states(self) -> dict:
        reminder_states = {}
        for reminder_type in ALL_REMINDER_TYPES:
            reminder_states[reminder_type] = {
                ReminderStateKeys.HIDDEN: False,
                ReminderStateKeys.PAUSED: False,
                ReminderStateKeys.SOUND_ENABLED: True,
                ReminderStateKeys.TTS_ENABLED: True,
                ReminderStateKeys.INTERVAL_MINUTES: 20,
            }
        return reminder_states

    def _collect_menu_labels(self, menu) -> list[str]:
        labels: list[str] = []
        items = self._get_menu_items(menu)
        for item in items:
            label = getattr(item, "text", None)
            if label:
                labels.append(label)

            submenu = self._get_submenu(item)
            if submenu is not None:
                labels.extend(self._collect_menu_labels(submenu))
        return labels

    def _get_menu_items(self, menu) -> list:
        return list(
            cast(
                Iterable,
                getattr(menu, "items", getattr(menu, "_items", ())),
            )
        )

    def _get_submenu(self, item):
        submenu = getattr(item, "submenu", None)
        if submenu is not None:
            return submenu

        action = getattr(item, "action", None)
        if action is not None and (
            hasattr(action, "items") or hasattr(action, "_items")
        ):
            return action

        return None


if __name__ == "__main__":
    unittest.main()
