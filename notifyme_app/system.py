"""
System integration functionality for the NotifyMe application.

This module handles system-level operations like opening files in Explorer,
launching web browsers, and managing system tray icons.
"""

import logging
import subprocess
import sys
import tempfile
import webbrowser
from pathlib import Path

from PIL import Image, ImageDraw

from notifyme_app.constants import (
    GITHUB_PAGES_URL,
    GITHUB_PAGES_USAGE_URL,
    GITHUB_RELEASES_URL,
    GITHUB_REPO_URL,
    HELP_ERROR_HTML,
)
from notifyme_app.utils import get_app_data_dir, get_config_path, get_resource_path


class SystemManager:
    """Manages system-level operations and integrations."""

    def __init__(self):
        """Initialize the system manager."""
        self.icon_file = get_resource_path("icon.png")

    def create_icon_image(self) -> Image.Image:
        """Create or load the system tray icon image."""
        if self.icon_file.exists():
            try:
                return Image.open(self.icon_file)
            except Exception as e:
                logging.error("Error loading icon: %s", e)

        # Fallback: Create a simple icon programmatically
        width = 64
        height = 64
        image = Image.new("RGB", (width, height), color="white")
        draw = ImageDraw.Draw(image)

        # Draw a simple eye shape
        draw.ellipse([10, 20, 54, 44], fill="lightblue", outline="blue", width=2)
        draw.ellipse([26, 26, 38, 38], fill="darkblue")
        draw.ellipse([29, 29, 35, 35], fill="black")

        return image

    def open_log_location(self) -> None:
        """Open the log file location in Explorer."""
        log_path = get_app_data_dir() / "notifyme.log"
        try:
            # Open Explorer and select the log file
            subprocess.run(["explorer", "/select,", str(log_path)], check=False)
            logging.info("Opened log location: %s", get_app_data_dir())
        except Exception as e:
            logging.error("Failed to open log location: %s", e)

    def open_exe_location(self) -> None:
        """Open the EXE/script location in Explorer."""
        if getattr(sys, "frozen", False):
            # Running as compiled executable
            exe_path = Path(sys.executable)
        else:
            # Running as script
            exe_path = Path(__file__).parent.parent / "notifyme.py"
        try:
            # Open Explorer and select the executable/script
            subprocess.run(["explorer", "/select,", str(exe_path)], check=False)
            logging.info("Opened EXE location: %s", exe_path.parent)
        except Exception as e:
            logging.error("Failed to open EXE location: %s", e)

    def open_config_location(self) -> None:
        """Open the config file location in Explorer."""
        config_path = get_config_path()
        try:
            # Open Explorer and select the config file
            subprocess.run(["explorer", "/select,", str(config_path)], check=False)
            logging.info("Opened config location: %s", config_path.parent)
        except Exception as e:
            logging.error("Failed to open config location: %s", e)

    def open_help(self) -> None:
        """
        Open help with smart fallback:
        1. Try online help first (GitHub Pages)
        2. Fall back to offline help/index.html if online unavailable
        """
        # Try online help first
        try:
            webbrowser.open(GITHUB_PAGES_USAGE_URL)
            logging.info("Opened online help: usage.html")
            return
        except Exception as e:
            logging.error("Failed to open online help: %s", e)

        # Offline help paths to try (in order of priority)
        help_search_paths = []

        # 1. Check bundled help directory (PyInstaller: help/index.html)
        help_search_paths.append(get_resource_path("help") / "index.html")

        # 2. Check project root help directory (dev mode)
        try:
            help_search_paths.append(
                Path(__file__).parent.parent / "help" / "index.html"
            )
        except Exception:
            logging.debug("Could not determine project root help path")

        # Try to open offline help
        for help_path in help_search_paths:
            if help_path.exists():
                try:
                    webbrowser.open(help_path.as_uri())
                    logging.info("Opened offline help: %s", help_path)
                    return
                except Exception as e:
                    logging.error("Failed to open offline help: %s", e)

        # Final fallback: show error
        try:
            error_html = HELP_ERROR_HTML.format(url=GITHUB_PAGES_URL)
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".html", delete=False, encoding="utf-8"
            ) as f:
                f.write(error_html)
                temp_path = Path(f.name)
            webbrowser.open(temp_path.as_uri())
            logging.info("Displayed help error message")
        except Exception as final_error:
            logging.error("Failed to display help error: %s", final_error)

    def show_startup_help(self) -> None:
        """Show help page on startup."""
        try:
            # Try online help first
            webbrowser.open(GITHUB_PAGES_USAGE_URL)
            logging.info("Opened startup help: online usage.html")
        except Exception as e:
            logging.error("Failed to open online startup help: %s", e)
            # Fall back to offline help
            self.open_help()

    def open_github(self) -> None:
        """Open the GitHub repository in the default browser."""
        try:
            webbrowser.open(GITHUB_REPO_URL)
            logging.info("Opened GitHub repository")
        except Exception as e:
            logging.error("Failed to open GitHub repository: %s", e)

    def open_github_releases(self) -> None:
        """Open the GitHub releases page in the default browser."""
        try:
            webbrowser.open(GITHUB_RELEASES_URL)
            logging.info("Opened GitHub releases")
        except Exception as e:
            logging.error("Failed to open GitHub releases: %s", e)

    def open_github_pages(self) -> None:
        """Open the GitHub Pages documentation in the default browser."""
        try:
            webbrowser.open(GITHUB_PAGES_URL)
            logging.info("Opened GitHub Pages documentation")
        except Exception as e:
            logging.error("Failed to open GitHub Pages documentation: %s", e)
