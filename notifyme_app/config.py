"""
Configuration management for the NotifyMe application.

This module handles loading, saving, and managing application configuration
including reminder intervals, sound settings, and visibility preferences.
"""

import json
import logging
from typing import Any

from notifyme_app.constants import (
    DEFAULT_BLINK_INTERVAL_MIN,
    DEFAULT_PRANAYAMA_INTERVAL_MIN,
    DEFAULT_WALKING_INTERVAL_MIN,
    DEFAULT_WATER_INTERVAL_MIN,
    ConfigKeys,
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
            ConfigKeys.INTERVAL_MINUTES: DEFAULT_BLINK_INTERVAL_MIN,
            ConfigKeys.WALKING_INTERVAL_MINUTES: DEFAULT_WALKING_INTERVAL_MIN,
            ConfigKeys.WATER_INTERVAL_MINUTES: DEFAULT_WATER_INTERVAL_MIN,
            ConfigKeys.PRANAYAMA_INTERVAL_MINUTES: DEFAULT_PRANAYAMA_INTERVAL_MIN,
            ConfigKeys.SOUND_ENABLED: False,
            ConfigKeys.BLINK_SOUND_ENABLED: True,
            ConfigKeys.WALKING_SOUND_ENABLED: True,
            ConfigKeys.WATER_SOUND_ENABLED: True,
            ConfigKeys.PRANAYAMA_SOUND_ENABLED: True,
            # Text-to-Speech configuration (offline via pyttsx3 / SAPI5 on Windows)
            ConfigKeys.TTS_ENABLED: True,
            ConfigKeys.BLINK_TTS_ENABLED: True,
            ConfigKeys.WALKING_TTS_ENABLED: True,
            ConfigKeys.WATER_TTS_ENABLED: True,
            ConfigKeys.PRANAYAMA_TTS_ENABLED: True,
            # 'auto' prefers Hindi if a Hindi voice is available, otherwise English
            ConfigKeys.TTS_LANGUAGE: "auto",
            ConfigKeys.BLINK_HIDDEN: False,
            ConfigKeys.WALKING_HIDDEN: False,
            ConfigKeys.WATER_HIDDEN: False,
            ConfigKeys.PRANAYAMA_HIDDEN: False,
            ConfigKeys.LAST_RUN: None,
        }

    def _load_config(self) -> dict[str, Any]:
        """Load configuration from the JSON config file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, encoding="utf-8") as f:
                    config = json.load(f)
                # One-time migration: enable TTS for existing users if the key is missing
                if ConfigKeys.TTS_ENABLED not in config:
                    config[ConfigKeys.TTS_ENABLED] = True
                    self._config = config
                    self.save_config()
                return config
            except Exception as e:
                logging.error("Error loading config: %s", e)
                return self._get_default_config()
        return self._get_default_config()

    def save_config(self) -> None:
        """Persist current configuration to the JSON config file."""
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self._config, f, indent=4)
        except Exception as e:
            logging.error("Error saving config: %s", e)

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        return self._config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value and save to file."""
        old_value = self._config.get(key)
        self._config[key] = value
        self.save_config()
        logging.info("Configuration updated: %s = %s (was: %s)", key, value, old_value)

    def get_all(self) -> dict[str, Any]:
        """Get all configuration values."""
        return self._config.copy()

    def update(self, updates: dict[str, Any]) -> None:
        """Update multiple configuration values and save to file."""
        for key, value in updates.items():
            old_value = self._config.get(key)
            logging.info(
                "Configuration updated: %s = %s (was: %s)", key, value, old_value
            )
        self._config.update(updates)
        self.save_config()

    # Convenience properties for commonly used settings
    @property
    def interval_minutes(self) -> int:
        """Get blink reminder interval in minutes."""
        return self.get(ConfigKeys.INTERVAL_MINUTES, DEFAULT_BLINK_INTERVAL_MIN)

    @interval_minutes.setter
    def interval_minutes(self, value: int) -> None:
        """Set blink reminder interval in minutes."""
        self.set(ConfigKeys.INTERVAL_MINUTES, value)

    @property
    def walking_interval_minutes(self) -> int:
        """Get walking reminder interval in minutes."""
        return self.get(
            ConfigKeys.WALKING_INTERVAL_MINUTES, DEFAULT_WALKING_INTERVAL_MIN
        )

    @walking_interval_minutes.setter
    def walking_interval_minutes(self, value: int) -> None:
        """Set walking reminder interval in minutes."""
        self.set(ConfigKeys.WALKING_INTERVAL_MINUTES, value)

    @property
    def water_interval_minutes(self) -> int:
        """Get water reminder interval in minutes."""
        return self.get(ConfigKeys.WATER_INTERVAL_MINUTES, DEFAULT_WATER_INTERVAL_MIN)

    @water_interval_minutes.setter
    def water_interval_minutes(self, value: int) -> None:
        """Set water reminder interval in minutes."""
        self.set(ConfigKeys.WATER_INTERVAL_MINUTES, value)

    @property
    def pranayama_interval_minutes(self) -> int:
        """Get pranayama reminder interval in minutes."""
        return self.get(
            ConfigKeys.PRANAYAMA_INTERVAL_MINUTES,
            DEFAULT_PRANAYAMA_INTERVAL_MIN,
        )

    @pranayama_interval_minutes.setter
    def pranayama_interval_minutes(self, value: int) -> None:
        """Set pranayama reminder interval in minutes."""
        self.set(ConfigKeys.PRANAYAMA_INTERVAL_MINUTES, value)

    @property
    def sound_enabled(self) -> bool:
        """Get global sound enabled state."""
        return self.get(ConfigKeys.SOUND_ENABLED, False)

    @sound_enabled.setter
    def sound_enabled(self, value: bool) -> None:
        """Set global sound enabled state."""
        self.set(ConfigKeys.SOUND_ENABLED, value)

    @property
    def blink_sound_enabled(self) -> bool:
        """Get blink sound enabled state."""
        return self.get(ConfigKeys.BLINK_SOUND_ENABLED, True)

    @blink_sound_enabled.setter
    def blink_sound_enabled(self, value: bool) -> None:
        """Set blink sound enabled state."""
        self.set(ConfigKeys.BLINK_SOUND_ENABLED, value)

    @property
    def walking_sound_enabled(self) -> bool:
        """Get walking sound enabled state."""
        return self.get(ConfigKeys.WALKING_SOUND_ENABLED, True)

    @walking_sound_enabled.setter
    def walking_sound_enabled(self, value: bool) -> None:
        """Set walking sound enabled state."""
        self.set(ConfigKeys.WALKING_SOUND_ENABLED, value)

    @property
    def water_sound_enabled(self) -> bool:
        """Get water sound enabled state."""
        return self.get(ConfigKeys.WATER_SOUND_ENABLED, True)

    @water_sound_enabled.setter
    def water_sound_enabled(self, value: bool) -> None:
        """Set water sound enabled state."""
        self.set(ConfigKeys.WATER_SOUND_ENABLED, value)

    @property
    def pranayama_sound_enabled(self) -> bool:
        """Get pranayama sound enabled state."""
        return self.get(ConfigKeys.PRANAYAMA_SOUND_ENABLED, True)

    @pranayama_sound_enabled.setter
    def pranayama_sound_enabled(self, value: bool) -> None:
        """Set pranayama sound enabled state."""
        self.set(ConfigKeys.PRANAYAMA_SOUND_ENABLED, value)

    @property
    def blink_hidden(self) -> bool:
        """Get blink reminder hidden state."""
        return self.get(ConfigKeys.BLINK_HIDDEN, False)

    @blink_hidden.setter
    def blink_hidden(self, value: bool) -> None:
        """Set blink reminder hidden state."""
        self.set(ConfigKeys.BLINK_HIDDEN, value)

    @property
    def walking_hidden(self) -> bool:
        """Get walking reminder hidden state."""
        return self.get(ConfigKeys.WALKING_HIDDEN, False)

    @walking_hidden.setter
    def walking_hidden(self, value: bool) -> None:
        """Set walking reminder hidden state."""
        self.set(ConfigKeys.WALKING_HIDDEN, value)

    @property
    def water_hidden(self) -> bool:
        """Get water reminder hidden state."""
        return self.get(ConfigKeys.WATER_HIDDEN, False)

    @water_hidden.setter
    def water_hidden(self, value: bool) -> None:
        """Set water reminder hidden state."""
        self.set(ConfigKeys.WATER_HIDDEN, value)

    @property
    def pranayama_hidden(self) -> bool:
        """Get pranayama reminder hidden state."""
        return self.get(ConfigKeys.PRANAYAMA_HIDDEN, False)

    @pranayama_hidden.setter
    def pranayama_hidden(self, value: bool) -> None:
        """Set pranayama reminder hidden state."""
        self.set(ConfigKeys.PRANAYAMA_HIDDEN, value)

    # Text-to-Speech properties
    @property
    def tts_enabled(self) -> bool:
        """Get global TTS enabled state."""
        return self.get(ConfigKeys.TTS_ENABLED, False)

    @tts_enabled.setter
    def tts_enabled(self, value: bool) -> None:
        """Set global TTS enabled state."""
        self.set(ConfigKeys.TTS_ENABLED, value)

    @property
    def blink_tts_enabled(self) -> bool:
        """Get blink reminder TTS enabled state."""
        return self.get(ConfigKeys.BLINK_TTS_ENABLED, True)

    @blink_tts_enabled.setter
    def blink_tts_enabled(self, value: bool) -> None:
        """Set blink reminder TTS enabled state."""
        self.set(ConfigKeys.BLINK_TTS_ENABLED, value)

    @property
    def walking_tts_enabled(self) -> bool:
        """Get walking reminder TTS enabled state."""
        return self.get(ConfigKeys.WALKING_TTS_ENABLED, True)

    @walking_tts_enabled.setter
    def walking_tts_enabled(self, value: bool) -> None:
        """Set walking reminder TTS enabled state."""
        self.set(ConfigKeys.WALKING_TTS_ENABLED, value)

    @property
    def water_tts_enabled(self) -> bool:
        """Get water reminder TTS enabled state."""
        return self.get(ConfigKeys.WATER_TTS_ENABLED, True)

    @water_tts_enabled.setter
    def water_tts_enabled(self, value: bool) -> None:
        """Set water reminder TTS enabled state."""
        self.set(ConfigKeys.WATER_TTS_ENABLED, value)

    @property
    def pranayama_tts_enabled(self) -> bool:
        """Get pranayama reminder TTS enabled state."""
        return self.get(ConfigKeys.PRANAYAMA_TTS_ENABLED, True)

    @pranayama_tts_enabled.setter
    def pranayama_tts_enabled(self, value: bool) -> None:
        """Set pranayama reminder TTS enabled state."""
        self.set(ConfigKeys.PRANAYAMA_TTS_ENABLED, value)

    @property
    def tts_language(self) -> str:
        """Get preferred TTS language. 'auto' (default), 'en', or 'hi'."""
        return self.get(ConfigKeys.TTS_LANGUAGE, "auto")

    @tts_language.setter
    def tts_language(self, value: str) -> None:
        """Set preferred TTS language."""
        self.set(ConfigKeys.TTS_LANGUAGE, value)
