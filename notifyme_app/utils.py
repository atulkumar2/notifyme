"""
Utility functions for the NotifyMe application.

This module contains helper functions for file paths, system operations,
and other utility functions used throughout the application.
"""

import ctypes
import os
import sys
from pathlib import Path
from ctypes import wintypes


class LASTINPUTINFO(ctypes.Structure):
    """Windows structure for getting last input information."""
    _fields_ = [
        ("cbSize", wintypes.UINT),
        ("dwTime", wintypes.DWORD),
    ]


def get_app_data_dir() -> Path:
    """Return the per-user app data directory for config and logs."""
    app_data = Path(os.environ.get("APPDATA", Path.home())) / "NotifyMe"
    app_data.mkdir(parents=True, exist_ok=True)
    return app_data


def get_resource_path(filename: str) -> Path:
    """Return path to a bundled or local resource (PyInstaller compatible)."""
    if getattr(sys, "frozen", False):
        # Running as compiled executable
        base_path = Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
    else:
        # Running as script
        base_path = Path(__file__).parent.parent
    return base_path / filename


def get_idle_seconds() -> float | None:
    """Return system idle time in seconds, or None if unavailable."""
    try:
        info = LASTINPUTINFO()
        info.cbSize = ctypes.sizeof(LASTINPUTINFO)
        if not ctypes.windll.user32.GetLastInputInfo(ctypes.byref(info)):
            return None
        tick_ms = ctypes.windll.kernel32.GetTickCount64()
        idle_ms = int(tick_ms) - int(info.dwTime)
        if idle_ms < 0:
            return None
        return idle_ms / 1000.0
    except Exception:
        return None


def format_elapsed(seconds: float) -> str:
    """Format elapsed time in a short, human-readable form."""
    minutes = int(round(seconds / 60))
    if minutes <= 1:
        return "1 min"
    if minutes < 60:
        return f"{minutes} mins"
    hours = minutes // 60
    rem_minutes = minutes % 60
    if rem_minutes == 0:
        return f"{hours}h"
    return f"{hours}h {rem_minutes}m"


def parse_version(version: str) -> tuple[int, int, int]:
    """Parse a version string into a numeric tuple (major, minor, patch)."""
    cleaned = version.strip().lower().lstrip("v")
    parts = cleaned.split(".")
    nums = []
    for part in parts[:3]:
        num = ""
        for ch in part:
            if ch.isdigit():
                num += ch
            else:
                break
        nums.append(int(num or 0))
    while len(nums) < 3:
        nums.append(0)
    return tuple(nums[:3])