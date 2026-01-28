"""
Eye Blink Reminder - Windows Desktop Application
Reminds users to blink their eyes at regular intervals to reduce eye strain.
"""

import json
import os
import random
import threading
import time
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw
from pystray import Icon, Menu, MenuItem
from win10toast import ToastNotifier


class BlinkReminderApp:
    """Main application class for the Eye Blink Reminder."""
    
    # Reminder messages (randomized for variety)
    MESSAGES = [
        "👁️ Time to blink! Give your eyes a break.",
        "💧 Blink reminder: Keep your eyes hydrated!",
        "✨ Don't forget to blink and look away from the screen.",
        "🌟 Eye care reminder: Blink 10 times slowly.",
        "💙 Your eyes need a break - blink and relax!",
        "🌈 Blink break! Look at something 20 feet away for 20 seconds.",
    ]
    
    def __init__(self):
        """Initialize the Eye Blink Reminder application."""
        self.config_file = Path(__file__).parent / "config.json"
        self.icon_file = Path(__file__).parent / "icon.png"
        
        # Load configuration
        self.config = self.load_config()
        self.interval_minutes = self.config.get("interval_minutes", 20)
        
        # Application state
        self.is_running = False
        self.is_paused = False
        self.timer_thread = None
        self.icon = None
        self.toaster = ToastNotifier()
        
        # Timer tracking
        self.next_reminder_time = None
        
    def load_config(self):
        """Load configuration from JSON file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading config: {e}")
                return self.get_default_config()
        return self.get_default_config()
    
    def get_default_config(self):
        """Return default configuration."""
        return {
            "interval_minutes": 20,
            "sound_enabled": False,
            "auto_start": False,
            "last_run": None
        }
    
    def save_config(self):
        """Save current configuration to JSON file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def create_icon_image(self):
        """Create or load the system tray icon."""
        if self.icon_file.exists():
            try:
                return Image.open(self.icon_file)
            except Exception as e:
                print(f"Error loading icon: {e}")
        
        # Fallback: Create a simple icon programmatically
        width = 64
        height = 64
        image = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(image)
        
        # Draw a simple eye shape
        draw.ellipse([10, 20, 54, 44], fill='lightblue', outline='blue', width=2)
        draw.ellipse([26, 26, 38, 38], fill='darkblue')
        draw.ellipse([29, 29, 35, 35], fill='black')
        
        return image
    
    def show_notification(self):
        """Display a Windows toast notification."""
        message = random.choice(self.MESSAGES)
        try:
            self.toaster.show_toast(
                "Eye Blink Reminder",
                message,
                icon_path=str(self.icon_file) if self.icon_file.exists() else None,
                duration=10,
                threaded=True
            )
        except Exception as e:
            print(f"Error showing notification: {e}")
    
    def timer_worker(self):
        """Background worker that triggers reminders at intervals."""
        while self.is_running:
            if not self.is_paused:
                # Calculate next reminder time
                self.next_reminder_time = time.time() + (self.interval_minutes * 60)
                
                # Wait for the interval
                time.sleep(self.interval_minutes * 60)
                
                # Show notification if still running and not paused
                if self.is_running and not self.is_paused:
                    self.show_notification()
            else:
                # If paused, check every second
                time.sleep(1)
    
    def start_reminders(self, icon=None, item=None):
        """Start the reminder timer."""
        if not self.is_running:
            self.is_running = True
            self.is_paused = False
            self.timer_thread = threading.Thread(target=self.timer_worker, daemon=True)
            self.timer_thread.start()
            print("Reminders started")
            if self.icon:
                self.icon.title = f"Eye Blink Reminder - Active ({self.interval_minutes}min)"
    
    def pause_reminders(self, icon=None, item=None):
        """Pause the reminder timer."""
        self.is_paused = True
        print("Reminders paused")
        if self.icon:
            self.icon.title = "Eye Blink Reminder - Paused"
    
    def resume_reminders(self, icon=None, item=None):
        """Resume the reminder timer."""
        if self.is_running:
            self.is_paused = False
            print("Reminders resumed")
            if self.icon:
                self.icon.title = f"Eye Blink Reminder - Active ({self.interval_minutes}min)"
    
    def stop_reminders(self, icon=None, item=None):
        """Stop the reminder timer."""
        self.is_running = False
        self.is_paused = False
        print("Reminders stopped")
        if self.icon:
            self.icon.title = "Eye Blink Reminder - Stopped"
    
    def snooze_reminder(self, icon=None, item=None):
        """Snooze the reminder for 5 minutes."""
        if self.is_running and not self.is_paused:
            # Reset the timer by updating next reminder time
            self.next_reminder_time = time.time() + (5 * 60)
            print("Reminder snoozed for 5 minutes")
    
    def set_interval(self, minutes):
        """Set a new reminder interval."""
        def _set(icon=None, item=None):
            self.interval_minutes = minutes
            self.config["interval_minutes"] = minutes
            self.save_config()
            print(f"Interval set to {minutes} minutes")
            if self.icon:
                self.icon.title = f"Eye Blink Reminder - Active ({self.interval_minutes}min)"
        return _set
    
    def quit_app(self, icon=None, item=None):
        """Quit the application."""
        self.stop_reminders()
        if self.icon:
            self.icon.stop()
        print("Application closed")
    
    def create_menu(self):
        """Create the system tray menu."""
        return Menu(
            MenuItem(
                "Start",
                self.start_reminders,
                default=True
            ),
            MenuItem(
                "Pause",
                self.pause_reminders
            ),
            MenuItem(
                "Resume",
                self.resume_reminders
            ),
            MenuItem(
                "Snooze (5 min)",
                self.snooze_reminder
            ),
            Menu.SEPARATOR,
            MenuItem(
                "Set Interval",
                Menu(
                    MenuItem("10 minutes", self.set_interval(10)),
                    MenuItem("15 minutes", self.set_interval(15)),
                    MenuItem("20 minutes", self.set_interval(20)),
                    MenuItem("30 minutes", self.set_interval(30)),
                    MenuItem("45 minutes", self.set_interval(45)),
                    MenuItem("60 minutes", self.set_interval(60)),
                )
            ),
            Menu.SEPARATOR,
            MenuItem(
                "Quit",
                self.quit_app
            )
        )
    
    def run(self):
        """Run the application with system tray icon."""
        # Create the icon
        icon_image = self.create_icon_image()
        self.icon = Icon(
            "Eye Blink Reminder",
            icon_image,
            "Eye Blink Reminder",
            menu=self.create_menu()
        )
        
        # Auto-start if configured
        if self.config.get("auto_start", False):
            self.start_reminders()
        
        # Run the icon (this blocks until quit)
        print("Eye Blink Reminder is running in the system tray")
        print(f"Default interval: {self.interval_minutes} minutes")
        self.icon.run()


def main():
    """Main entry point for the application."""
    app = BlinkReminderApp()
    app.run()


if __name__ == "__main__":
    main()
