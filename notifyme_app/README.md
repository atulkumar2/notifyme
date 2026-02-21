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
  "global": {
    "sound_enabled": false,
    "tts_enabled": true,
    "tts_language": "auto",
    "last_run": null
  },
  "reminders": {
    "blink": {
      "interval_minutes": 20,
      "sound_enabled": true,
      "tts_enabled": true,
      "hidden": false
    },
    "walking": {
      "interval_minutes": 60,
      "sound_enabled": true,
      "tts_enabled": true,
      "hidden": false
    },
    "water": {
      "interval_minutes": 30,
      "sound_enabled": true,
      "tts_enabled": true,
      "hidden": false
    },
    "pranayama": {
      "interval_minutes": 120,
      "sound_enabled": true,
      "tts_enabled": true,
      "hidden": false
    }
  }
}
```

**Configuration Keys:**

- `global.sound_enabled`: Global sound toggle
- `global.tts_enabled`: Global TTS toggle
- `global.tts_language`: TTS language ("auto", "en", or "hi")
- `global.last_run`: Tracks last application run time
- `reminders.[type].interval_minutes`: Reminder intervals in minutes
- `reminders.[type].sound_enabled`: Per-reminder sound toggles
- `reminders.[type].tts_enabled`: Per-reminder TTS toggles
- `reminders.[type].hidden`: Hide specific reminders from menu

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

### 3. Add Default Intervals (`constants.py`)

Update the defaults so new reminders get initial values automatically:

```python
DEFAULT_INTERVALS_MIN = {
    # ... existing reminders ...
    REMINDER_STRETCH: 45,
}
```

### 4. Configuration Defaults (Automatic)

No new `ConfigKeys` or properties are required. The config system uses
sectioned reminder settings under `reminders.[type]` and will initialize
defaults based on `ALL_REMINDER_TYPES` and `DEFAULT_INTERVALS_MIN`.
No extra config properties are needed for new reminders.

### 5. Notifications (Automatic)

NotificationManager uses `show_reminder_notification(reminder_type)` and the
entries in `REMINDER_TITLES` and `REMINDER_MESSAGES`, so no new notification
method is required.

### 6. Menu Callbacks (`app.py`)

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
