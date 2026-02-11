"""
NotifyMe - A comprehensive reminder application for Windows.

This package provides a system tray application that helps users maintain
healthy habits through periodic reminders for:
- Eye blinking (to prevent digital eye strain)
- Walking breaks (to combat sedentary behavior)
- Water intake (to maintain proper hydration)
- Pranayama breathing exercises (for stress relief and focus)

The application features:
- Customizable reminder intervals
- Individual sound controls for each reminder type
- Ability to hide/show specific reminder types
- Smart idle detection to avoid interrupting when away
- Automatic startup help and welcome notifications
- Update checking from GitHub releases
- Persistent configuration storage

Main Components:
- app: Main application class coordinating all components
- config: Configuration management and persistence
- constants: Application constants and default values
- menu: System tray menu generation and management
- notifications: Toast notification display and management
- system: System integration (file operations, browser launching)
- timers: Background timer management with idle detection
- updater: Application update checking and notifications
- utils: Utility functions for common operations

Usage:
    from notifyme_app import NotifyMeApp

    app = NotifyMeApp()
    app.run()

Author: Atul Kumar
License: MIT
Version: 2.2.0
"""

from .app import NotifyMeApp
from .constants import APP_VERSION

__version__ = APP_VERSION
__author__ = "Atul Kumar"
__license__ = "MIT"

__all__ = ["NotifyMeApp", "APP_VERSION"]
