"""
Configuration management for the NotifyMe application.

This module handles loading, saving, and managing application configuration
including reminder intervals, sound settings, and visibility preferences.
"""

import json
import logging
from typing import Any

from notifyme_app.constants import (
    ALL_REMINDER_TYPES,
    DEFAULT_INTERVALS_MIN,
    REMINDER_BLINK,
    REMINDER_PRANAYAMA,
    REMINDER_WALKING,
    REMINDER_WATER,
    ConfigKeys,
    ConfigSections,
    ReminderConfigFields,
)
from notifyme_app.utils import get_config_path


class ConfigManager:
    """Manages application configuration settings."""

    def __init__(self):
        """Initialize the configuration manager."""
        self.config_file = get_config_path()
        self._config = self._load_config()

    def _get_default_config(self) -> dict[str, Any]:
        """Return default configuration values."""
        return {
            ConfigSections.GLOBAL: self._get_default_global_config(),
            ConfigSections.REMINDERS: self._get_default_reminders_config(),
        }

    def _get_default_global_config(self) -> dict[str, int | bool | str | None]:
        """Return default global configuration values."""
        return {
            ConfigKeys.SOUND_ENABLED: False,
            # Text-to-Speech configuration (offline via pyttsx3 / SAPI5 on Windows)
            ConfigKeys.TTS_ENABLED: True,
            # 'auto' prefers Hindi if a Hindi voice is available, otherwise English
            ConfigKeys.TTS_LANGUAGE: "auto",
            ConfigKeys.LAST_RUN: None,
        }

    def _get_default_reminder_config(self, reminder_type: str) -> dict[str, Any]:
        """Return default configuration for a reminder type."""
        return {
            ReminderConfigFields.INTERVAL_MINUTES: DEFAULT_INTERVALS_MIN[reminder_type],
            ReminderConfigFields.SOUND_ENABLED: True,
            ReminderConfigFields.TTS_ENABLED: True,
            ReminderConfigFields.HIDDEN: False,
        }

    def _get_default_reminders_config(self) -> dict[str, Any]:
        """Return default reminder configuration values."""
        reminders: dict[str, Any] = {}
        for reminder_type in ALL_REMINDER_TYPES:
            reminders[reminder_type] = self._get_default_reminder_config(reminder_type)
        return reminders

    def _load_config(self) -> dict[str, Any]:
        """Load configuration from the JSON config file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, encoding="utf-8") as f:
                    raw_config = json.load(f)
                config = self._normalize_config(raw_config)
                if config != raw_config:
                    self._config = config
                    self.save_config()
                return config
            except Exception as e:
                logging.error("Error loading config: %s", e)
                return self._get_default_config()
        return self._get_default_config()

    def _normalize_config(self, config: dict[str, Any]) -> dict[str, Any]:
        """Normalize config into the sectioned structure."""
        if ConfigSections.GLOBAL in config or ConfigSections.REMINDERS in config:
            global_config = config.get(ConfigSections.GLOBAL, {})
            reminders_config = config.get(ConfigSections.REMINDERS, {})
        else:
            global_config = {}
            reminders_config = {}

            for key in (
                ConfigKeys.SOUND_ENABLED,
                ConfigKeys.TTS_ENABLED,
                ConfigKeys.TTS_LANGUAGE,
                ConfigKeys.LAST_RUN,
            ):
                if key in config:
                    global_config[key] = config[key]

            for reminder_type in ALL_REMINDER_TYPES:
                reminders_config[reminder_type] = {
                    ReminderConfigFields.INTERVAL_MINUTES: config.get(
                        self._legacy_reminder_key(reminder_type, "interval_minutes"),
                        DEFAULT_INTERVALS_MIN[reminder_type],
                    ),
                    ReminderConfigFields.SOUND_ENABLED: config.get(
                        self._legacy_reminder_key(reminder_type, "sound_enabled"),
                        True,
                    ),
                    ReminderConfigFields.TTS_ENABLED: config.get(
                        self._legacy_reminder_key(reminder_type, "tts_enabled"),
                        True,
                    ),
                    ReminderConfigFields.HIDDEN: config.get(
                        self._legacy_reminder_key(reminder_type, "hidden"),
                        False,
                    ),
                }

        defaults = self._get_default_config()
        normalized_global = defaults[ConfigSections.GLOBAL] | global_config

        normalized_reminders: dict[str, Any] = {}
        for reminder_type in ALL_REMINDER_TYPES:
            reminder_defaults = defaults[ConfigSections.REMINDERS][reminder_type]
            reminder_current = reminders_config.get(reminder_type, {})
            normalized_reminders[reminder_type] = reminder_defaults | reminder_current

        return {
            ConfigSections.GLOBAL: normalized_global,
            ConfigSections.REMINDERS: normalized_reminders,
        }

    def save_config(self) -> None:
        """Persist current configuration to the JSON config file."""
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self._config, f, indent=4)
        except Exception as e:
            logging.error("Error saving config: %s", e)

    def get(self, key: str, default: Any = None) -> Any:
        """Get a global configuration value."""
        return self._get_global(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set a global configuration value and save to file."""
        old_value = self._get_global(key)
        self._set_global(key, value)
        self.save_config()
        logging.info("Configuration updated: %s = %s (was: %s)", key, value, old_value)

    def get_all(self) -> dict[str, Any]:
        """Get all configuration values."""
        return {
            ConfigSections.GLOBAL: self._config[ConfigSections.GLOBAL].copy(),
            ConfigSections.REMINDERS: {
                reminder_type: reminder.copy()
                for reminder_type, reminder in self._config[
                    ConfigSections.REMINDERS
                ].items()
            },
        }

    def update(self, updates: dict[str, Any]) -> None:
        """Update multiple configuration values and save to file."""
        if ConfigSections.GLOBAL in updates or ConfigSections.REMINDERS in updates:
            global_updates = updates.get(ConfigSections.GLOBAL, {})
            reminders_updates = updates.get(ConfigSections.REMINDERS, {})
        else:
            global_updates = updates
            reminders_updates = {}

        for key, value in global_updates.items():
            old_value = self._get_global(key)
            logging.info(
                "Configuration updated: %s = %s (was: %s)", key, value, old_value
            )
        self._config[ConfigSections.GLOBAL].update(global_updates)

        for reminder_type, reminder_updates in reminders_updates.items():
            reminder_config = self._config[ConfigSections.REMINDERS].setdefault(
                reminder_type, {}
            )
            reminder_config.update(reminder_updates)

        self.save_config()

    def _legacy_reminder_key(self, reminder_type: str, suffix: str) -> str:
        """Build legacy reminder-specific configuration keys."""
        return f"{reminder_type}_{suffix}"

    def _get_global(self, key: str, default: Any = None) -> Any:
        """Get a value from the global configuration section."""
        return self._config[ConfigSections.GLOBAL].get(key, default)

    def _set_global(self, key: str, value: Any) -> None:
        """Set a value in the global configuration section."""
        self._config[ConfigSections.GLOBAL][key] = value

    def _get_reminder_value(
        self, reminder_type: str, key: str, default: Any = None
    ) -> Any:
        """Get a value from a reminder configuration section."""
        reminder_config = self._config[ConfigSections.REMINDERS].setdefault(
            reminder_type, {}
        )
        return reminder_config.get(key, default)

    def _set_reminder_value(self, reminder_type: str, key: str, value: Any) -> None:
        """Set a value in a reminder configuration section."""
        reminder_config = self._config[ConfigSections.REMINDERS].setdefault(
            reminder_type, {}
        )
        reminder_config[key] = value

    def get_interval_minutes(self, reminder_type: str) -> int:
        """Get reminder interval in minutes for a reminder type."""
        return self._get_reminder_value(
            reminder_type,
            ReminderConfigFields.INTERVAL_MINUTES,
            DEFAULT_INTERVALS_MIN.get(reminder_type, 20),
        )

    def set_interval_minutes(self, reminder_type: str, value: int) -> None:
        """Set reminder interval in minutes for a reminder type."""
        self._set_reminder_value(
            reminder_type, ReminderConfigFields.INTERVAL_MINUTES, value
        )
        self.save_config()

    def get_sound_enabled(self, reminder_type: str) -> bool:
        """Get reminder-specific sound enabled state."""
        return self._get_reminder_value(
            reminder_type, ReminderConfigFields.SOUND_ENABLED, True
        )

    def set_sound_enabled(self, reminder_type: str, value: bool) -> None:
        """Set reminder-specific sound enabled state."""
        self._set_reminder_value(
            reminder_type, ReminderConfigFields.SOUND_ENABLED, value
        )
        self.save_config()

    def get_tts_enabled(self, reminder_type: str) -> bool:
        """Get reminder-specific TTS enabled state."""
        return self._get_reminder_value(
            reminder_type, ReminderConfigFields.TTS_ENABLED, True
        )

    def set_tts_enabled(self, reminder_type: str, value: bool) -> None:
        """Set reminder-specific TTS enabled state."""
        self._set_reminder_value(reminder_type, ReminderConfigFields.TTS_ENABLED, value)
        self.save_config()

    def get_hidden(self, reminder_type: str) -> bool:
        """Get reminder hidden state for a reminder type."""
        return self._get_reminder_value(
            reminder_type, ReminderConfigFields.HIDDEN, False
        )

    def set_hidden(self, reminder_type: str, value: bool) -> None:
        """Set reminder hidden state for a reminder type."""
        self._set_reminder_value(reminder_type, ReminderConfigFields.HIDDEN, value)
        self.save_config()

    # Convenience properties for commonly used settings
    @property
    def blink_interval_minutes(self) -> int:
        """Get blink reminder interval in minutes."""
        return self.get_interval_minutes(REMINDER_BLINK)

    @blink_interval_minutes.setter
    def blink_interval_minutes(self, value: int) -> None:
        """Set blink reminder interval in minutes."""
        self.set_interval_minutes(REMINDER_BLINK, value)

    @property
    def walking_interval_minutes(self) -> int:
        """Get walking reminder interval in minutes."""
        return self.get_interval_minutes(REMINDER_WALKING)

    @walking_interval_minutes.setter
    def walking_interval_minutes(self, value: int) -> None:
        """Set walking reminder interval in minutes."""
        self.set_interval_minutes(REMINDER_WALKING, value)

    @property
    def water_interval_minutes(self) -> int:
        """Get water reminder interval in minutes."""
        return self.get_interval_minutes(REMINDER_WATER)

    @water_interval_minutes.setter
    def water_interval_minutes(self, value: int) -> None:
        """Set water reminder interval in minutes."""
        self.set_interval_minutes(REMINDER_WATER, value)

    @property
    def pranayama_interval_minutes(self) -> int:
        """Get pranayama reminder interval in minutes."""
        return self.get_interval_minutes(REMINDER_PRANAYAMA)

    @pranayama_interval_minutes.setter
    def pranayama_interval_minutes(self, value: int) -> None:
        """Set pranayama reminder interval in minutes."""
        self.set_interval_minutes(REMINDER_PRANAYAMA, value)

    @property
    def sound_enabled(self) -> bool:
        """Get global sound enabled state."""
        return self._get_global(ConfigKeys.SOUND_ENABLED, False)

    @sound_enabled.setter
    def sound_enabled(self, value: bool) -> None:
        """Set global sound enabled state."""
        self._set_global(ConfigKeys.SOUND_ENABLED, value)
        self.save_config()

    @property
    def blink_sound_enabled(self) -> bool:
        """Get blink sound enabled state."""
        return self.get_sound_enabled(REMINDER_BLINK)

    @blink_sound_enabled.setter
    def blink_sound_enabled(self, value: bool) -> None:
        """Set blink sound enabled state."""
        self.set_sound_enabled(REMINDER_BLINK, value)

    @property
    def walking_sound_enabled(self) -> bool:
        """Get walking sound enabled state."""
        return self.get_sound_enabled(REMINDER_WALKING)

    @walking_sound_enabled.setter
    def walking_sound_enabled(self, value: bool) -> None:
        """Set walking sound enabled state."""
        self.set_sound_enabled(REMINDER_WALKING, value)

    @property
    def water_sound_enabled(self) -> bool:
        """Get water sound enabled state."""
        return self.get_sound_enabled(REMINDER_WATER)

    @water_sound_enabled.setter
    def water_sound_enabled(self, value: bool) -> None:
        """Set water sound enabled state."""
        self.set_sound_enabled(REMINDER_WATER, value)

    @property
    def pranayama_sound_enabled(self) -> bool:
        """Get pranayama sound enabled state."""
        return self.get_sound_enabled(REMINDER_PRANAYAMA)

    @pranayama_sound_enabled.setter
    def pranayama_sound_enabled(self, value: bool) -> None:
        """Set pranayama sound enabled state."""
        self.set_sound_enabled(REMINDER_PRANAYAMA, value)

    @property
    def blink_hidden(self) -> bool:
        """Get blink reminder hidden state."""
        return self.get_hidden(REMINDER_BLINK)

    @blink_hidden.setter
    def blink_hidden(self, value: bool) -> None:
        """Set blink reminder hidden state."""
        self.set_hidden(REMINDER_BLINK, value)

    @property
    def walking_hidden(self) -> bool:
        """Get walking reminder hidden state."""
        return self.get_hidden(REMINDER_WALKING)

    @walking_hidden.setter
    def walking_hidden(self, value: bool) -> None:
        """Set walking reminder hidden state."""
        self.set_hidden(REMINDER_WALKING, value)

    @property
    def water_hidden(self) -> bool:
        """Get water reminder hidden state."""
        return self.get_hidden(REMINDER_WATER)

    @water_hidden.setter
    def water_hidden(self, value: bool) -> None:
        """Set water reminder hidden state."""
        self.set_hidden(REMINDER_WATER, value)

    @property
    def pranayama_hidden(self) -> bool:
        """Get pranayama reminder hidden state."""
        return self.get_hidden(REMINDER_PRANAYAMA)

    @pranayama_hidden.setter
    def pranayama_hidden(self, value: bool) -> None:
        """Set pranayama reminder hidden state."""
        self.set_hidden(REMINDER_PRANAYAMA, value)

    # Text-to-Speech properties
    @property
    def tts_enabled(self) -> bool:
        """Get global TTS enabled state."""
        return self._get_global(ConfigKeys.TTS_ENABLED, False)

    @tts_enabled.setter
    def tts_enabled(self, value: bool) -> None:
        """Set global TTS enabled state."""
        self._set_global(ConfigKeys.TTS_ENABLED, value)
        self.save_config()

    @property
    def blink_tts_enabled(self) -> bool:
        """Get blink reminder TTS enabled state."""
        return self.get_tts_enabled(REMINDER_BLINK)

    @blink_tts_enabled.setter
    def blink_tts_enabled(self, value: bool) -> None:
        """Set blink reminder TTS enabled state."""
        self.set_tts_enabled(REMINDER_BLINK, value)

    @property
    def walking_tts_enabled(self) -> bool:
        """Get walking reminder TTS enabled state."""
        return self.get_tts_enabled(REMINDER_WALKING)

    @walking_tts_enabled.setter
    def walking_tts_enabled(self, value: bool) -> None:
        """Set walking reminder TTS enabled state."""
        self.set_tts_enabled(REMINDER_WALKING, value)

    @property
    def water_tts_enabled(self) -> bool:
        """Get water reminder TTS enabled state."""
        return self.get_tts_enabled(REMINDER_WATER)

    @water_tts_enabled.setter
    def water_tts_enabled(self, value: bool) -> None:
        """Set water reminder TTS enabled state."""
        self.set_tts_enabled(REMINDER_WATER, value)

    @property
    def pranayama_tts_enabled(self) -> bool:
        """Get pranayama reminder TTS enabled state."""
        return self.get_tts_enabled(REMINDER_PRANAYAMA)

    @pranayama_tts_enabled.setter
    def pranayama_tts_enabled(self, value: bool) -> None:
        """Set pranayama reminder TTS enabled state."""
        self.set_tts_enabled(REMINDER_PRANAYAMA, value)

    @property
    def tts_language(self) -> str:
        """Get preferred TTS language. 'auto' (default), 'en', or 'hi'."""
        return self._get_global(ConfigKeys.TTS_LANGUAGE, "auto")

    @tts_language.setter
    def tts_language(self, value: str) -> None:
        """Set preferred TTS language."""
        self._set_global(ConfigKeys.TTS_LANGUAGE, value)
        self.save_config()
