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
  "blink_hidden": false,
  "walking_hidden": false,
  "water_hidden": false,
  "pranayama_hidden": false,
  "last_run": null
}
```

## Logging

The application uses Python's logging module with a rotating file handler:

- Log file: `%APPDATA%/NotifyMe/notifyme.log`
- Maximum size: 5 MB per file
- Backup count: 5 files
- Format: `%(asctime)s - %(levelname)s - %(message)s`
