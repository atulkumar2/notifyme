"""Tests for platform-aware system helpers."""

import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from notifyme_app.system import SystemManager
from notifyme_app.utils import get_app_data_dir

sys.path.insert(0, str(Path(__file__).parent.parent))


class TestUtils(unittest.TestCase):
    """Tests for platform-specific utility behavior."""

    @patch("notifyme_app.utils.Path.mkdir")
    @patch("notifyme_app.utils.Path.home", return_value=Path("/home/tester"))
    @patch("notifyme_app.utils.sys.platform", "linux")
    def test_get_app_data_dir_on_linux(self, _mock_home, mock_mkdir):
        """Linux should store app data under ~/.config/NotifyMe."""
        result = get_app_data_dir()
        self.assertEqual(result, Path("/home/tester/.config/NotifyMe"))
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)


class TestSystemManager(unittest.TestCase):
    """Tests for platform-aware folder opening."""

    @patch("notifyme_app.system.subprocess.run")
    @patch("notifyme_app.system.sys.platform", "linux")
    def test_open_path_uses_xdg_open_for_linux(self, mock_run):
        """Linux should use xdg-open with the parent directory when selecting a file."""
        manager = SystemManager()
        manager._open_path(Path("/tmp/config.json"), select_file=True)
        mock_run.assert_called_once_with(["xdg-open", "/tmp"], check=False)

    @patch("notifyme_app.system.subprocess.run")
    @patch("notifyme_app.system.sys.platform", "win32")
    def test_open_path_uses_explorer_select_for_windows(self, mock_run):
        """Windows should continue using explorer select."""
        manager = SystemManager()
        manager._open_path(Path("C:/tmp/config.json"), select_file=True)
        mock_run.assert_called_once_with(
            ["explorer", "/select,", "C:/tmp/config.json"], check=False
        )

    @patch("notifyme_app.system.sys.platform", "win32")
    @patch("notifyme_app.system.Image.open")
    def test_create_icon_image_prefers_ico_on_windows(self, mock_open):
        """Windows should prefer the ICO asset for the tray icon."""
        manager = SystemManager()
        manager.icon_ico_file = Path("/tmp/icon.ico")
        manager.icon_file = Path("/tmp/icon.png")

        opened_image = MagicMock()
        opened_image.convert.return_value = "converted-image"
        context_manager = MagicMock()
        context_manager.__enter__.return_value = opened_image
        context_manager.__exit__.return_value = None
        mock_open.return_value = context_manager

        with patch.object(
            Path, "exists", new=lambda path_self: path_self == manager.icon_ico_file
        ):
            image = manager.create_icon_image()

        self.assertEqual(image, "converted-image")
        mock_open.assert_called_once_with(manager.icon_ico_file)
        opened_image.convert.assert_called_once_with("RGBA")

    @patch("notifyme_app.system.Image.open", side_effect=OSError("broken image"))
    def test_create_icon_image_falls_back_when_asset_load_fails(self, _mock_open):
        """Icon loading failures should not prevent tray startup."""
        manager = SystemManager()
        manager.icon_file = Path("/tmp/icon.png")
        manager.icon_ico_file = Path("/tmp/icon.ico")

        with patch.object(Path, "exists", new=lambda _path: True):
            image = manager.create_icon_image()

        self.assertEqual(image.mode, "RGBA")
        self.assertEqual(image.size, (64, 64))


if __name__ == "__main__":
    unittest.main()
