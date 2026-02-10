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
