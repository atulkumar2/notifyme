"""
Configuration management for the NotifyMe application.

This module handles loading, saving, and managing application configuration
including reminder intervals, sound settings, and visibility preferences.
"""

import json
import logging
from typing import Dict, Any

from notifyme_app.constants import (
    DEFAULT_BLINK_INTERVAL_MIN,
    DEFAULT_WALKING_INTERVAL_MIN,
    DEFAULT_WATER_INTERVAL_MIN,
    DEFAULT_PRANAYAMA_INTERVAL_MIN,
)
from notifyme_app.utils import get_app_data_dir


class ConfigManager:
    """Manages application configuration settings."""

    def __init__(self):
        """Initialize the configuration manager."""
        self.config_file = get_app_data_dir() / "config.json"
        self._config = self._load_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """Return default configuration values."""
        return {
            "interval_minutes": DEFAULT_BLINK_INTERVAL_MIN,
            "walking_interval_minutes": DEFAULT_WALKING_INTERVAL_MIN,
            "water_interval_minutes": DEFAULT_WATER_INTERVAL_MIN,
            "pranayama_interval_minutes": DEFAULT_PRANAYAMA_INTERVAL_MIN,
            "sound_enabled": False,
            "blink_sound_enabled": True,
            "walking_sound_enabled": True,
            "water_sound_enabled": True,
            "pranayama_sound_enabled": True,
            "blink_hidden": False,
            "walking_hidden": False,
            "water_hidden": False,
            "pranayama_hidden": False,
            "last_run": None,
        }

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from the JSON config file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, encoding="utf-8") as f:
                    return json.load(f)
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

    def get_all(self) -> Dict[str, Any]:
        """Get all configuration values."""
        return self._config.copy()

    def update(self, updates: Dict[str, Any]) -> None:
        """Update multiple configuration values and save to file."""
        for key, value in updates.items():
            old_value = self._config.get(key)
            logging.info("Configuration updated: %s = %s (was: %s)", key, value, old_value)
        self._config.update(updates)
        self.save_config()

    # Convenience properties for commonly used settings
    @property
    def interval_minutes(self) -> int:
        """Get blink reminder interval in minutes."""
        return self.get("interval_minutes", DEFAULT_BLINK_INTERVAL_MIN)

    @interval_minutes.setter
    def interval_minutes(self, value: int) -> None:
        """Set blink reminder interval in minutes."""
        self.set("interval_minutes", value)

    @property
    def walking_interval_minutes(self) -> int:
        """Get walking reminder interval in minutes."""
        return self.get("walking_interval_minutes", DEFAULT_WALKING_INTERVAL_MIN)

    @walking_interval_minutes.setter
    def walking_interval_minutes(self, value: int) -> None:
        """Set walking reminder interval in minutes."""
        self.set("walking_interval_minutes", value)

    @property
    def water_interval_minutes(self) -> int:
        """Get water reminder interval in minutes."""
        return self.get("water_interval_minutes", DEFAULT_WATER_INTERVAL_MIN)

    @water_interval_minutes.setter
    def water_interval_minutes(self, value: int) -> None:
        """Set water reminder interval in minutes."""
        self.set("water_interval_minutes", value)

    @property
    def pranayama_interval_minutes(self) -> int:
        """Get pranayama reminder interval in minutes."""
        return self.get("pranayama_interval_minutes", DEFAULT_PRANAYAMA_INTERVAL_MIN)

    @pranayama_interval_minutes.setter
    def pranayama_interval_minutes(self, value: int) -> None:
        """Set pranayama reminder interval in minutes."""
        self.set("pranayama_interval_minutes", value)

    @property
    def sound_enabled(self) -> bool:
        """Get global sound enabled state."""
        return self.get("sound_enabled", False)

    @sound_enabled.setter
    def sound_enabled(self, value: bool) -> None:
        """Set global sound enabled state."""
        self.set("sound_enabled", value)

    @property
    def blink_sound_enabled(self) -> bool:
        """Get blink sound enabled state."""
        return self.get("blink_sound_enabled", True)

    @blink_sound_enabled.setter
    def blink_sound_enabled(self, value: bool) -> None:
        """Set blink sound enabled state."""
        self.set("blink_sound_enabled", value)

    @property
    def walking_sound_enabled(self) -> bool:
        """Get walking sound enabled state."""
        return self.get("walking_sound_enabled", True)

    @walking_sound_enabled.setter
    def walking_sound_enabled(self, value: bool) -> None:
        """Set walking sound enabled state."""
        self.set("walking_sound_enabled", value)

    @property
    def water_sound_enabled(self) -> bool:
        """Get water sound enabled state."""
        return self.get("water_sound_enabled", True)

    @water_sound_enabled.setter
    def water_sound_enabled(self, value: bool) -> None:
        """Set water sound enabled state."""
        self.set("water_sound_enabled", value)

    @property
    def pranayama_sound_enabled(self) -> bool:
        """Get pranayama sound enabled state."""
        return self.get("pranayama_sound_enabled", True)

    @pranayama_sound_enabled.setter
    def pranayama_sound_enabled(self, value: bool) -> None:
        """Set pranayama sound enabled state."""
        self.set("pranayama_sound_enabled", value)

    @property
    def blink_hidden(self) -> bool:
        """Get blink reminder hidden state."""
        return self.get("blink_hidden", False)

    @blink_hidden.setter
    def blink_hidden(self, value: bool) -> None:
        """Set blink reminder hidden state."""
        self.set("blink_hidden", value)

    @property
    def walking_hidden(self) -> bool:
        """Get walking reminder hidden state."""
        return self.get("walking_hidden", False)

    @walking_hidden.setter
    def walking_hidden(self, value: bool) -> None:
        """Set walking reminder hidden state."""
        self.set("walking_hidden", value)

    @property
    def water_hidden(self) -> bool:
        """Get water reminder hidden state."""
        return self.get("water_hidden", False)

    @water_hidden.setter
    def water_hidden(self, value: bool) -> None:
        """Set water reminder hidden state."""
        self.set("water_hidden", value)

    @property
    def pranayama_hidden(self) -> bool:
        """Get pranayama reminder hidden state."""
        return self.get("pranayama_hidden", False)

    @pranayama_hidden.setter
    def pranayama_hidden(self, value: bool) -> None:
        """Set pranayama reminder hidden state."""
        self.set("pranayama_hidden", value)
