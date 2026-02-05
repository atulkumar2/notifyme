"""
Timer management for the NotifyMe application.

This module handles the background timer threads that trigger reminders
at specified intervals, with support for idle detection and pause states.
"""

import logging
import threading
import time
from typing import Optional, Callable

from notifyme_app.constants import DEFAULT_OFFSETS_SECONDS
from notifyme_app.utils import get_idle_seconds


class ReminderTimer:
    """Manages a single reminder timer with idle detection and pause support."""

    def __init__(
        self,
        reminder_type: str,
        interval_minutes: int,
        callback: Callable[[], None],
        offset_seconds: int = 0,
    ):
        """Initialize a reminder timer.
        
        Args:
            reminder_type: Type of reminder (blink, walking, water, pranayama)
            interval_minutes: Interval between reminders in minutes
            callback: Function to call when reminder triggers
            offset_seconds: Initial offset to stagger reminders
        """
        self.reminder_type = reminder_type
        self.interval_minutes = interval_minutes
        self.callback = callback
        self.offset_seconds = offset_seconds
        
        self.is_running = False
        self.is_paused = False
        self.thread: Optional[threading.Thread] = None
        self.next_reminder_time: Optional[float] = None
        self.idle_suppressed = False

    def start(self) -> None:
        """Start the reminder timer."""
        if not self.is_running:
            self.is_running = True
            self.is_paused = False
            self.thread = threading.Thread(target=self._timer_worker, daemon=True)
            self.thread.start()
            logging.info("%s timer started", self.reminder_type.capitalize())

    def stop(self) -> None:
        """Stop the reminder timer."""
        self.is_running = False
        self.is_paused = False
        logging.info("%s timer stopped", self.reminder_type.capitalize())

    def pause(self) -> None:
        """Pause the reminder timer."""
        self.is_paused = True
        logging.info("%s timer paused", self.reminder_type.capitalize())

    def resume(self) -> None:
        """Resume the reminder timer."""
        self.is_paused = False
        logging.info("%s timer resumed", self.reminder_type.capitalize())

    def snooze(self, minutes: int = 5) -> None:
        """Snooze the reminder for specified minutes."""
        if self.is_running and not self.is_paused:
            self.next_reminder_time = time.time() + (minutes * 60)
            logging.info(
                "%s timer snoozed for %d minutes",
                self.reminder_type.capitalize(), minutes)

    def update_interval(self, interval_minutes: int) -> None:
        """Update the reminder interval."""
        self.interval_minutes = interval_minutes
        logging.info(
            "%s interval updated to %d minutes",
            self.reminder_type.capitalize(), interval_minutes)

    def _should_reset_due_to_idle(self, interval_seconds: int) -> bool:
        """Return True if idle time exceeds interval and the timer should reset."""
        idle_seconds = get_idle_seconds()
        if idle_seconds is None:
            return False
        
        if idle_seconds >= interval_seconds:
            if not self.idle_suppressed:
                logging.info("%s reminder reset due to user idle/lock", self.reminder_type.capitalize())
            return True
        return False

    def _timer_worker(self) -> None:
        """Background worker that triggers reminders at intervals."""
        while self.is_running:
            if not self.is_paused:
                interval_seconds = self.interval_minutes * 60
                now = time.time()

                if self._should_reset_due_to_idle(interval_seconds):
                    self.idle_suppressed = True
                    self.next_reminder_time = now + interval_seconds
                    time.sleep(1)
                    continue

                if self.idle_suppressed:
                    self.idle_suppressed = False

                if self.next_reminder_time is None:
                    self.next_reminder_time = now + interval_seconds + self.offset_seconds

                if now >= self.next_reminder_time:
                    self.callback()
                    self.next_reminder_time = now + interval_seconds
                
                time.sleep(1)
            else:
                # If paused, check every second
                time.sleep(1)


class TimerManager:
    """Manages all reminder timers for the application."""

    def __init__(self):
        """Initialize the timer manager."""
        self.timers = {}
        self.is_global_paused = False

    def create_timer(
        self,
        reminder_type: str,
        interval_minutes: int,
        callback: Callable[[], None],
    ) -> ReminderTimer:
        """Create and register a new reminder timer."""
        offset_seconds = DEFAULT_OFFSETS_SECONDS.get(reminder_type, 0)
        timer = ReminderTimer(reminder_type, interval_minutes, callback, offset_seconds)
        self.timers[reminder_type] = timer
        return timer

    def start_all(self) -> None:
        """Start all registered timers."""
        self.is_global_paused = False
        for timer in self.timers.values():
            timer.start()
        logging.info("All timers started")

    def stop_all(self) -> None:
        """Stop all registered timers."""
        self.is_global_paused = False
        for timer in self.timers.values():
            timer.stop()
        logging.info("All timers stopped")

    def pause_all(self) -> None:
        """Pause all registered timers."""
        self.is_global_paused = True
        for timer in self.timers.values():
            timer.pause()
        logging.info("All timers paused")

    def resume_all(self) -> None:
        """Resume all registered timers."""
        self.is_global_paused = False
        for timer in self.timers.values():
            timer.resume()
        logging.info("All timers resumed")

    def snooze_all(self, minutes: int = 5) -> None:
        """Snooze all active timers."""
        for timer in self.timers.values():
            if not timer.is_paused:
                timer.snooze(minutes)
        logging.info("All active timers snoozed for %d minutes", minutes)

    def get_timer(self, reminder_type: str) -> Optional[ReminderTimer]:
        """Get a specific timer by reminder type."""
        return self.timers.get(reminder_type)

    def update_timer_interval(self, reminder_type: str, interval_minutes: int) -> None:
        """Update the interval for a specific timer."""
        timer = self.get_timer(reminder_type)
        if timer:
            timer.update_interval(interval_minutes)

    def is_timer_paused(self, reminder_type: str) -> bool:
        """Check if a specific timer is paused."""
        timer = self.get_timer(reminder_type)
        return timer.is_paused if timer else False

    def pause_timer(self, reminder_type: str) -> None:
        """Pause a specific timer."""
        timer = self.get_timer(reminder_type)
        if timer:
            timer.pause()

    def resume_timer(self, reminder_type: str) -> None:
        """Resume a specific timer."""
        timer = self.get_timer(reminder_type)
        if timer:
            timer.resume()

    def toggle_timer_pause(self, reminder_type: str) -> None:
        """Toggle pause state for a specific timer."""
        timer = self.get_timer(reminder_type)
        if timer:
            if timer.is_paused:
                timer.resume()
            else:
                timer.pause()
