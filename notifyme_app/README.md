# NotifyMe Application Module

This directory contains the refactored NotifyMe application organized into logical modules for better maintainability and code organization.

## Module Structure

### Core Modules

- **`__init__.py`** - Package initialization and main exports
- **`app.py`** - Main application class that coordinates all components
- **`constants.py`** - Application constants, default values, and message templates

### Component Modules

- **`config.py`** - Configuration management and persistence
- **`notifications.py`** - Toast notification display and management
- **`timers.py`** - Background timer management with idle detection
- **`menu.py`** - System tray menu generation and management
- **`updater.py`** - Application update checking from GitHub releases
- **`system.py`** - System integration (file operations, browser launching)
- **`tts.py`** - Text-to-Speech management (NEW)
- **`utils.py`** - Utility functions and helper classes

## Key Features

### Configuration Management (`config.py`)

- **ConfigManager**: Handles loading, saving, and managing all application settings
- Properties for easy access to common settings
- Automatic persistence to JSON configuration file
- Default value handling

### Notification System (`notifications.py`)

- **NotificationManager**: Manages Windows toast notifications
- Support for different reminder types with custom messages
- Sound control integration
- Icon management for notifications

### Timer System (`timers.py`)

- **ReminderTimer**: Individual timer with idle detection and pause support
- **TimerManager**: Coordinates multiple timers
- Smart idle detection to avoid interrupting when user is away
- Individual pause/resume controls for each reminder type

### Menu System (`menu.py`)

- **MenuManager**: Dynamic system tray menu generation
- Context-aware menu items based on current state
- Support for hidden reminders and sound controls
- Callback-based architecture for clean separation

### Update System (`updater.py`)

- **UpdateChecker**: GitHub releases integration
- Automatic version comparison
- Background update checking
- Update notification support

### System Integration (`system.py`)

- **SystemManager**: System-level operations
- File Explorer integration
- Web browser launching
- Icon creation and management

### Text-to-Speech System (`tts.py`)

- **TTSManager**: Manages offline text-to-speech using Windows SAPI (pyttsx3)
- Non-blocking speech via background worker thread
- Voice selection with language preference (auto-detect Hindi/English)
- Fresh engine instance per request for stability
- Graceful fallback if pyttsx3 unavailable

## Usage

```python
from notifyme_app import NotifyMeApp

# Create and run the application
app = NotifyMeApp()
app.run()
```

## Architecture Benefits

1. **Separation of Concerns**: Each module has a single, well-defined responsibility
2. **Testability**: Individual components can be tested in isolation
3. **Maintainability**: Changes to one component don't affect others
4. **Extensibility**: New features can be added without modifying existing code
5. **Reusability**: Components can be reused in different contexts

## Dependencies

- **pystray**: System tray icon management
- **winotify**: Windows toast notifications
- **pyttsx3**: Offline Text-to-Speech using Windows SAPI
- **PIL (Pillow)**: Image processing for icons
- **Standard library**: logging, threading, json, pathlib, etc.

## Configuration

The application stores its configuration in `%APPDATA%/NotifyMe/config.json` with the following structure:

```json
{
  "interval_minutes": 20,
  "walking_interval_minutes": 60,
  "water_interval_minutes": 30,
  "pranayama_interval_minutes": 120,
  "sound_enabled": false,
  "blink_sound_enabled": true,
  "walking_sound_enabled": true,
  "water_sound_enabled": true,
  "pranayama_sound_enabled": true,
  "tts_enabled": true,
  "tts_language": "auto",
  "blink_tts_enabled": true,
  "walking_tts_enabled": true,
  "water_tts_enabled": true,
  "pranayama_tts_enabled": true,
  "blink_hidden": false,
  "walking_hidden": false,
  "water_hidden": false,
  "pranayama_hidden": false,
  "last_run": null
}
```

**Configuration Keys:**

- `interval_minutes`, `*_interval_minutes`: Reminder intervals in minutes
- `sound_enabled`: Global sound toggle
- `*_sound_enabled`: Per-reminder sound toggles
- `tts_enabled`: Global TTS toggle
- `tts_language`: TTS language ("auto", "en", or "hi")
- `*_tts_enabled`: Per-reminder TTS toggles
- `*_hidden`: Hide specific reminders from menu
- `last_run`: Tracks last application run time

## Logging

The application uses Python's logging module with a rotating file handler:

- Log file: `%APPDATA%/NotifyMe/notifyme.log`
- Maximum size: 5 MB per file
- Backup count: 5 files
- Format: `%(asctime)s - %(levelname)s - %(message)s`

## Adding Custom Reminders

The application is designed with extensibility in mind. To add a new custom reminder:

### 1. Define the Reminder Constant (`constants.py`)

Add a new reminder type constant:

```python
# Reminder types
REMINDER_BLINK = "blink"
REMINDER_WALKING = "walking"
REMINDER_WATER = "water"
REMINDER_PRANAYAMA = "pranayama"
REMINDER_STRETCH = "stretch"  # New custom reminder

# Update the reminder types list
ALL_REMINDER_TYPES = [
    REMINDER_BLINK,
    REMINDER_WALKING,
    REMINDER_WATER,
    REMINDER_PRANAYAMA,
    REMINDER_STRETCH,  # Add to list
]
```

### 2. Add Reminder Configuration (`constants.py`)

Define the reminder's properties in `REMINDER_CONFIGS`:

```python
REMINDER_CONFIGS = {
    # ... existing reminders ...
    REMINDER_STRETCH: {
        "id": REMINDER_STRETCH,
        "icon": "🤸",
        "display_title": "🤸 Stretch Reminder",
        "notification_title": "Stretch Reminder",
        "default_interval": 45,  # minutes
        "default_offset": 40,  # seconds
        "interval_options": [30, 45, 60, 90],  # menu options
        "messages": [
            "🤸 Time to stretch! Stand up and move.",
            "🦴 Stretch break: Loosen up those muscles!",
            "💪 Quick stretch time - your body needs it!",
        ],
    },
}
```

### 3. Add Configuration Keys (`constants.py`)

Update the `ConfigKeys` class with new keys for your reminder:

```python
class ConfigKeys:
    # ... existing keys ...
    STRETCH_INTERVAL_MINUTES = "stretch_interval_minutes"
    STRETCH_SOUND_ENABLED = "stretch_sound_enabled"
    STRETCH_TTS_ENABLED = "stretch_tts_enabled"
    STRETCH_HIDDEN = "stretch_hidden"
```

### 4. Add Configuration Properties (`config.py`)

Add properties to `ConfigManager` for the new reminder:

```python
@property
def stretch_interval_minutes(self) -> int:
    return int(
        self.get(
            ConfigKeys.STRETCH_INTERVAL_MINUTES,
            DEFAULT_INTERVALS_MIN[REMINDER_STRETCH],
        )
    )

@stretch_interval_minutes.setter
def stretch_interval_minutes(self, value: int) -> None:
    self.set(ConfigKeys.STRETCH_INTERVAL_MINUTES, value)

# Add similar properties for stretch_sound_enabled, stretch_tts_enabled, stretch_hidden
```

### 5. Add Notification Method (`notifications.py`)

Add a notification method for the custom reminder:

```python
def show_stretch_notification(self, last_shown_at=None, sound_enabled: bool = False):
    """Display a stretch reminder notification and return the selected message."""
    return self.show_notification(
        REMINDER_TITLES[REMINDER_STRETCH],
        REMINDER_MESSAGES[REMINDER_STRETCH],
        last_shown_at,
        sound_enabled,
    )
```

### 6. Add Menu Callbacks (`app.py`)

The menu system automatically generates entries for all reminders in `ALL_REMINDER_TYPES`. Ensure your callback functions follow the naming convention:

- `toggle_{reminder_type}_hidden`
- `toggle_{reminder_type}_pause`
- `toggle_{reminder_type}_sound`
- `toggle_{reminder_type}_tts`
- `set_{reminder_type}_interval`
- `test_{reminder_type}_notification`

The dynamic menu system will automatically create menu items for your custom reminder!

### Notes

- The menu system is **fully dynamic** and will automatically generate menu items for all reminders in `ALL_REMINDER_TYPES`
- Configuration management automatically handles new reminder properties through `_build_reminder_states()` in `app.py`
- No changes needed to `menu.py` - it dynamically iterates through all configured reminders
- The system supports unlimited custom reminders without modifying core menu logic
