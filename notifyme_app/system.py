"""
System integration functionality for the NotifyMe application.

This module handles system-level operations like opening files in Explorer,
launching web browsers, and managing system tray icons.
"""

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
from notifyme_app.logger import get_logger

from notifyme_app.utils import get_app_data_dir, get_config_path, get_resource_path


class SystemManager:
    """Manages system-level operations and integrations."""

    def __init__(self):
        """Initialize the system manager."""
        self.icon_file = get_resource_path("icon.png")
        self.icon_ico_file = get_resource_path("icon.ico")

    def _open_path(self, path: Path, select_file: bool = False) -> None:
        """Open a file or directory using the platform's default file manager."""
        target = path.parent if select_file else path
        if sys.platform == "win32":
            args = ["explorer", str(target)]
            if select_file:
                args = ["explorer", "/select,", str(path)]
        elif sys.platform == "darwin":
            args = ["open", "-R", str(path)] if select_file else ["open", str(target)]
        else:
            args = ["xdg-open", str(target)]
        subprocess.run(args, check=False)

    def create_icon_image(self) -> Image.Image:
        """Create or load the system tray icon image."""
        candidate_paths = []
        if sys.platform == "win32":
            candidate_paths.append(self.icon_ico_file)
        candidate_paths.append(self.icon_file)

        for icon_path in candidate_paths:
            if not icon_path.exists():
                continue
            try:
                with Image.open(icon_path) as image:
                    return image.convert("RGBA")
            except Exception as e:
                get_logger(__name__).error(
                    "Error loading tray icon from %s: %s", icon_path, e
                )

        # Fallback: Create a simple icon programmatically
        width = 64
        height = 64
        image = Image.new("RGBA", (width, height), color=(0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        # Draw a simple eye shape
        draw.ellipse([10, 20, 54, 44], fill="lightblue", outline="blue", width=2)
        draw.ellipse([26, 26, 38, 38], fill="darkblue")
        draw.ellipse([29, 29, 35, 35], fill="black")

        return image

    def open_log_location(self) -> None:
        """Open the log file location in the system file manager."""
        log_path = get_app_data_dir() / "notifyme.log"
        try:
            self._open_path(log_path, select_file=True)
            get_logger(__name__).info("Opened log location: %s", get_app_data_dir())
        except Exception as e:
            get_logger(__name__).error("Failed to open log location: %s", e)

    def open_exe_location(self) -> None:
        """Open the executable or script location in the system file manager."""
        if getattr(sys, "frozen", False):
            # Running as compiled executable
            exe_path = Path(sys.executable)
        else:
            # Running as script
            exe_path = Path(__file__).parent.parent / "notifyme.py"
        try:
            self._open_path(exe_path, select_file=True)
            get_logger(__name__).info("Opened EXE location: %s", exe_path.parent)
        except Exception as e:
            get_logger(__name__).error("Failed to open EXE location: %s", e)

    def open_config_location(self) -> None:
        """Open the config file location in the system file manager."""
        config_path = get_config_path()
        try:
            self._open_path(config_path, select_file=True)
            get_logger(__name__).info("Opened config location: %s", config_path.parent)
        except Exception as e:
            get_logger(__name__).error("Failed to open config location: %s", e)

    def open_help(self) -> None:
        """
        Open help with smart fallback:
        1. Try online help first (GitHub Pages)
        2. Fall back to offline help/index.html if online unavailable
        """
        # Try online help first
        try:
            webbrowser.open(GITHUB_PAGES_USAGE_URL)
            get_logger(__name__).info("Opened online help: usage.html")
            return
        except Exception as e:
            get_logger(__name__).error("Failed to open online help: %s", e)

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
            get_logger(__name__).debug("Could not determine project root help path")

        # Try to open offline help
        for help_path in help_search_paths:
            if help_path.exists():
                try:
                    webbrowser.open(help_path.as_uri())
                    get_logger(__name__).info("Opened offline help: %s", help_path)
                    return
                except Exception as e:
                    get_logger(__name__).error("Failed to open offline help: %s", e)

        # Final fallback: show error
        try:
            error_html = HELP_ERROR_HTML.format(url=GITHUB_PAGES_URL)
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".html", delete=False, encoding="utf-8"
            ) as f:
                f.write(error_html)
                temp_path = Path(f.name)
            webbrowser.open(temp_path.as_uri())
            get_logger(__name__).info("Displayed help error message")
        except Exception as final_error:
            get_logger(__name__).error("Failed to display help error: %s", final_error)

    def show_startup_help(self) -> None:
        """Show help page on startup."""
        try:
            # Try online help first
            webbrowser.open(GITHUB_PAGES_USAGE_URL)
            get_logger(__name__).info("Opened startup help: online usage.html")
        except Exception as e:
            get_logger(__name__).error("Failed to open online startup help: %s", e)
            # Fall back to offline help
            self.open_help()

    def open_github(self) -> None:
        """Open the GitHub repository in the default browser."""
        try:
            webbrowser.open(GITHUB_REPO_URL)
            get_logger(__name__).info("Opened GitHub repository")
        except Exception as e:
            get_logger(__name__).error("Failed to open GitHub repository: %s", e)

    def open_github_releases(self) -> None:
        """Open the GitHub releases page in the default browser."""
        try:
            webbrowser.open(GITHUB_RELEASES_URL)
            get_logger(__name__).info("Opened GitHub releases")
        except Exception as e:
            get_logger(__name__).error("Failed to open GitHub releases: %s", e)

    def open_github_pages(self) -> None:
        """Open the GitHub Pages documentation in the default browser."""
        try:
            webbrowser.open(GITHUB_PAGES_URL)
            get_logger(__name__).info("Opened GitHub Pages documentation")
        except Exception as e:
            get_logger(__name__).error(
                "Failed to open GitHub Pages documentation: %s", e
            )
