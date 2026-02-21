"""
Medicine reminder management for the NotifyMe application.

This module handles medicine schedules, tracking, and completion status.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Any

from notifyme_app.constants import (
    DEFAULT_MEDICINE_TIME_WINDOWS,
)
from notifyme_app.utils import get_app_data_dir


class Medicine:
    """Represents a single medicine with its details."""

    def __init__(
        self,
        name: str,
        dosage: str,
        disease: str,
        meal_times: list[str],
        duration_days: int = 0,
        start_date: str | None = None,
        custom_disease: str | None = None,
    ):
        """
        Initialize a medicine.

        Args:
            name: Medicine name
            dosage: Dosage information (e.g., "1 tablet", "5ml")
            disease: Disease type (from COMMON_DISEASES or "Other")
            meal_times: List of meal times (breakfast, lunch, dinner)
            duration_days: Duration in days (0 = continuous)
            start_date: Start date in YYYY-MM-DD format (defaults to today)
            custom_disease: Custom disease name if disease is "Other"
        """
        self.name = name
        self.dosage = dosage
        self.disease = disease
        self.meal_times = meal_times
        self.duration_days = duration_days
        self.start_date = start_date or datetime.now().strftime("%Y-%m-%d")
        self.custom_disease = custom_disease

    def to_dict(self) -> dict[str, Any]:
        """Convert medicine to dictionary."""
        return {
            "name": self.name,
            "dosage": self.dosage,
            "disease": self.disease,
            "meal_times": self.meal_times,
            "duration_days": self.duration_days,
            "start_date": self.start_date,
            "custom_disease": self.custom_disease,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Medicine":
        """Create medicine from dictionary."""
        return cls(
            name=data["name"],
            dosage=data["dosage"],
            disease=data["disease"],
            meal_times=data["meal_times"],
            duration_days=data.get("duration_days", 0),
            start_date=data.get("start_date"),
            custom_disease=data.get("custom_disease"),
        )

    def is_active(self) -> bool:
        """Check if medicine is still active based on duration."""
        if self.duration_days == 0:
            return True  # Continuous medicine

        start = datetime.strptime(self.start_date, "%Y-%m-%d")
        end = start + timedelta(days=self.duration_days)
        return datetime.now() < end

    def get_display_disease(self) -> str:
        """Get the display name for the disease."""
        if self.disease == "Other" and self.custom_disease:
            return self.custom_disease
        return self.disease


class MedicineManager:
    """Manages medicine schedules and completion tracking."""

    def __init__(self):
        """Initialize the medicine manager."""
        self.medicines_file = get_app_data_dir() / "medicines.json"
        self.completion_file = get_app_data_dir() / "medicine_completion.json"
        self.medicines: list[Medicine] = []
        self.completions: dict[str, dict[str, str]] = {}
        self._load_medicines()
        self._load_completions()

    def _load_medicines(self) -> None:
        """Load medicines from file."""
        if self.medicines_file.exists():
            try:
                with open(self.medicines_file, encoding="utf-8") as f:
                    data = json.load(f)
                    self.medicines = [Medicine.from_dict(m) for m in data]
                logging.info("Loaded %d medicines", len(self.medicines))
            except Exception as e:
                logging.error("Error loading medicines: %s", e)
                self.medicines = []
        else:
            self.medicines = []

    def _save_medicines(self) -> None:
        """Save medicines to file."""
        try:
            with open(self.medicines_file, "w", encoding="utf-8") as f:
                json.dump([m.to_dict() for m in self.medicines], f, indent=4)
            logging.info("Saved %d medicines", len(self.medicines))
        except Exception as e:
            logging.error("Error saving medicines: %s", e)

    def _load_completions(self) -> None:
        """Load completion tracking from file."""
        if self.completion_file.exists():
            try:
                with open(self.completion_file, encoding="utf-8") as f:
                    self.completions = json.load(f)
                # Clean up old completions (older than 7 days)
                self._cleanup_old_completions()
            except Exception as e:
                logging.error("Error loading completions: %s", e)
                self.completions = {}
        else:
            self.completions = {}

    def _save_completions(self) -> None:
        """Save completion tracking to file."""
        try:
            with open(self.completion_file, "w", encoding="utf-8") as f:
                json.dump(self.completions, f, indent=4)
        except Exception as e:
            logging.error("Error saving completions: %s", e)

    def _cleanup_old_completions(self) -> None:
        """Remove completion records older than 7 days."""
        cutoff = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        dates_to_remove = [date for date in self.completions.keys() if date < cutoff]
        for date in dates_to_remove:
            del self.completions[date]
        if dates_to_remove:
            self._save_completions()

    def add_medicine(self, medicine: Medicine) -> None:
        """Add a new medicine."""
        self.medicines.append(medicine)
        self._save_medicines()
        logging.info("Added medicine: %s", medicine.name)

    def remove_medicine(self, index: int) -> None:
        """Remove a medicine by index."""
        if 0 <= index < len(self.medicines):
            medicine = self.medicines.pop(index)
            self._save_medicines()
            logging.info("Removed medicine: %s", medicine.name)

    def get_active_medicines(self) -> list[Medicine]:
        """Get all active medicines."""
        return [m for m in self.medicines if m.is_active()]

    def get_medicines_for_meal_time(self, meal_time: str) -> list[Medicine]:
        """Get active medicines for a specific meal time."""
        return [m for m in self.get_active_medicines() if meal_time in m.meal_times]

    def mark_completed(self, meal_time: str) -> None:
        """Mark medicine as completed for today's meal time."""
        today = datetime.now().strftime("%Y-%m-%d")
        if today not in self.completions:
            self.completions[today] = {}

        self.completions[today][meal_time] = datetime.now().strftime("%H:%M:%S")
        self._save_completions()
        logging.info("Marked %s medicine as completed for %s", meal_time, today)

    def is_completed_today(self, meal_time: str) -> bool:
        """Check if medicine for meal time is completed today."""
        today = datetime.now().strftime("%Y-%m-%d")
        return today in self.completions and meal_time in self.completions[today]

    def should_remind(self, meal_time: str) -> bool:
        """
        Check if reminder should be shown for this meal time.

        Returns True if:
        - Current time is within the time window
        - Medicine not completed today
        - There are active medicines for this meal time
        """
        if self.is_completed_today(meal_time):
            return False

        medicines = self.get_medicines_for_meal_time(meal_time)
        if not medicines:
            return False

        # Check if current time is within the window
        time_window = DEFAULT_MEDICINE_TIME_WINDOWS[meal_time]
        current_time = datetime.now().strftime("%H:%M")

        return time_window["start"] <= current_time <= time_window["end"]

    def get_time_window_config(self) -> dict[str, dict[str, str]]:
        """Get the time window configuration for all meal times."""
        return DEFAULT_MEDICINE_TIME_WINDOWS.copy()

    def update_time_window(self, meal_time: str, start: str, end: str) -> None:
        """Update time window for a meal time (currently not persisted)."""
        # For now, this modifies the in-memory constant
        # In future, could be persisted to config
        DEFAULT_MEDICINE_TIME_WINDOWS[meal_time] = {"start": start, "end": end}
        logging.info("Updated %s time window: %s-%s", meal_time, start, end)
