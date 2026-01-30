"""
Unit tests for the NotifyMe application.
"""

import sys
import tempfile
import unittest
from pathlib import Path
from typing import Iterable, cast
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent))

from notifyme import NotifyMeApp, get_app_data_dir, get_resource_path


class TestGetAppDataDir(unittest.TestCase):
    """Tests for get_app_data_dir function."""

    @patch("notifyme.Path.home")
    @patch.dict("os.environ", {"APPDATA": ""}, clear=True)
    def test_get_app_data_dir_no_appdata(self, mock_home):
        """Test get_app_data_dir when APPDATA is not set."""
        mock_home.return_value = Path("/home/user")
        result = get_app_data_dir()
        self.assertEqual(result.name, "NotifyMe")

    @patch.dict("os.environ", {"APPDATA": "C:\\Users\\Test\\AppData\\Roaming"})
    @patch("notifyme.Path.mkdir")
    def test_get_app_data_dir_with_appdata(self, mock_mkdir):
        """Test get_app_data_dir when APPDATA is set."""
        result = get_app_data_dir()
        self.assertTrue(str(result).endswith("NotifyMe"))
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)


class TestGetResourcePath(unittest.TestCase):
    """Tests for get_resource_path function."""

    def test_get_resource_path_not_frozen(self):
        """Test get_resource_path when running as script."""
        result = get_resource_path("icon.png")
        self.assertEqual(result.name, "icon.png")

    @patch("notifyme.sys")
    def test_get_resource_path_frozen(self, mock_sys):
        """Test get_resource_path when running as compiled exe."""
        mock_sys.frozen = True
        mock_sys._MEIPASS = Path("/temp/meipass")
        result = get_resource_path("icon.png")
        self.assertTrue(str(result).endswith("icon.png"))


class TestNotifyMeApp(unittest.TestCase):
    """Tests for NotifyMeApp class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = Path(self.temp_dir) / "config.json"
        self.icon_file = Path(self.temp_dir) / "icon.png"
        self.icon_file_ico = Path(self.temp_dir) / "icon.ico"

        # Create a simple icon file for testing
        from PIL import Image

        img = Image.new("RGB", (64, 64), color="blue")
        img.save(self.icon_file)

        # Patch the paths
        with patch("notifyme.APP_DATA_DIR", Path(self.temp_dir)):
            with patch("notifyme.get_resource_path") as mock_resource:
                mock_resource.side_effect = lambda x: Path(self.temp_dir) / x
                self.app = NotifyMeApp()
                self.app.config_file = self.config_file
                self.app.icon_file = self.icon_file
                self.app.icon_file_ico = self.icon_file_ico

    def test_initialization(self):
        """Test app initialization with default values."""
        self.assertEqual(self.app.interval_minutes, 20)
        self.assertEqual(self.app.walking_interval_minutes, 60)
        self.assertEqual(self.app.water_interval_minutes, 30)
        self.assertFalse(self.app.is_running)
        self.assertFalse(self.app.is_paused)

    def test_get_default_config(self):
        """Test default configuration values."""
        config = self.app.get_default_config()
        self.assertEqual(config["interval_minutes"], 20)
        self.assertEqual(config["walking_interval_minutes"], 60)
        self.assertEqual(config["water_interval_minutes"], 30)
        self.assertFalse(config["sound_enabled"])
        self.assertFalse(config["auto_start"])

    def test_save_and_load_config(self):
        """Test saving and loading configuration."""
        self.app.config["interval_minutes"] = 30
        self.app.config["walking_interval_minutes"] = 90
        self.app.save_config()

        # Load config in a new instance
        loaded_config = self.app.load_config()
        self.assertEqual(loaded_config["interval_minutes"], 30)
        self.assertEqual(loaded_config["walking_interval_minutes"], 90)

    def test_set_interval(self):
        """Test setting blink reminder interval."""
        set_func = self.app.set_interval(30)
        set_func()
        self.assertEqual(self.app.interval_minutes, 30)
        self.assertEqual(self.app.config["interval_minutes"], 30)

    def test_set_walking_interval(self):
        """Test setting walking reminder interval."""
        set_func = self.app.set_walking_interval(90)
        set_func()
        self.assertEqual(self.app.walking_interval_minutes, 90)
        self.assertEqual(self.app.config["walking_interval_minutes"], 90)

    def test_set_water_interval(self):
        """Test setting water reminder interval."""
        set_func = self.app.set_water_interval(45)
        set_func()
        self.assertEqual(self.app.water_interval_minutes, 45)
        self.assertEqual(self.app.config["water_interval_minutes"], 45)

    def test_start_reminders(self):
        """Test starting reminders."""
        with patch("threading.Thread"):
            self.app.start_reminders()
            self.assertTrue(self.app.is_running)
            self.assertFalse(self.app.is_paused)

    def test_pause_reminders(self):
        """Test pausing all reminders."""
        self.app.is_running = True
        self.app.is_blink_paused = True
        self.app.is_walking_paused = False
        self.app.is_water_paused = True
        self.app.pause_reminders()
        self.assertTrue(self.app.is_paused)
        self.assertTrue(self.app.is_blink_paused)
        self.assertFalse(self.app.is_walking_paused)
        self.assertTrue(self.app.is_water_paused)

    def test_resume_reminders(self):
        """Test resuming all reminders clears all pause states."""
        self.app.is_running = False
        self.app.is_paused = True
        self.app.is_blink_paused = True
        self.app.is_walking_paused = True
        self.app.is_water_paused = True
        self.app.resume_reminders()
        self.assertFalse(self.app.is_paused)
        self.assertFalse(self.app.is_blink_paused)
        self.assertFalse(self.app.is_walking_paused)
        self.assertFalse(self.app.is_water_paused)

    def test_toggle_blink_pause(self):
        """Test toggling blink reminder pause."""
        initial_state = self.app.is_blink_paused
        self.app.toggle_blink_pause()
        self.assertEqual(self.app.is_blink_paused, not initial_state)
        self.app.toggle_blink_pause()
        self.assertEqual(self.app.is_blink_paused, initial_state)

    def test_toggle_walking_pause(self):
        """Test toggling walking reminder pause."""
        initial_state = self.app.is_walking_paused
        self.app.toggle_walking_pause()
        self.assertEqual(self.app.is_walking_paused, not initial_state)

    def test_toggle_water_pause(self):
        """Test toggling water reminder pause."""
        initial_state = self.app.is_water_paused
        self.app.toggle_water_pause()
        self.assertEqual(self.app.is_water_paused, not initial_state)

    def test_stop_reminders(self):
        """Test stopping reminders."""
        self.app.is_running = True
        self.app.icon = MagicMock()
        self.app.stop_reminders()
        self.assertFalse(self.app.is_running)
        self.assertFalse(self.app.is_paused)

    @patch("notifyme.subprocess.run")
    def test_open_log_location(self, mock_run):
        """Test opening log location."""
        self.app.open_log_location()
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        self.assertEqual(args[0], "explorer")
        self.assertEqual(args[1], "/select,")

    @patch("notifyme.subprocess.run")
    def test_open_exe_location(self, mock_run):
        """Test opening exe location."""
        self.app.open_exe_location()
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        self.assertEqual(args[0], "explorer")
        self.assertEqual(args[1], "/select,")

    @patch("notifyme.subprocess.run")
    def test_open_config_location(self, mock_run):
        """Test opening config location."""
        self.app.open_config_location()
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        self.assertEqual(args[0], "explorer")
        self.assertEqual(args[1], "/select,")

    @patch("notifyme.webbrowser.open")
    def test_open_user_guide(self, mock_open):
        """Test opening the user guide in browser."""
        help_dir = Path(self.temp_dir) / "help"
        help_dir.mkdir(exist_ok=True)
        help_path = help_dir / "index.html"
        help_path.write_text("<html><body>User Guide</body></html>", encoding="utf-8")
        with patch("notifyme.get_resource_path", return_value=help_dir):
            self.app.open_help()

        mock_open.assert_called_once()

    def test_update_icon_title_paused(self):
        """Test icon title when all reminders are paused."""
        self.app.icon = MagicMock()
        self.app.is_paused = True
        self.app.update_icon_title()
        self.assertEqual(self.app.icon.title, "NotifyMe - All Paused")

    def test_update_icon_title_running(self):
        """Test icon title when reminders are running."""
        self.app.icon = MagicMock()
        self.app.is_paused = False
        self.app.interval_minutes = 20
        self.app.walking_interval_minutes = 60
        self.app.water_interval_minutes = 30
        self.app.update_icon_title()
        self.assertIn("20min", self.app.icon.title)
        self.assertIn("60min", self.app.icon.title)
        self.assertIn("30min", self.app.icon.title)

    def test_update_icon_title_individual_paused(self):
        """Test icon title when individual reminders are paused."""
        self.app.icon = MagicMock()
        self.app.is_paused = False
        self.app.is_blink_paused = True
        self.app.update_icon_title()
        self.assertIn("⏸", self.app.icon.title)

    def test_get_initial_title_auto_start(self):
        """Test initial title when auto_start is enabled."""
        self.app.config["auto_start"] = True
        self.app.interval_minutes = 20
        self.app.walking_interval_minutes = 60
        self.app.water_interval_minutes = 30
        title = self.app.get_initial_title()
        self.assertIn("20min", title)
        self.assertIn("60min", title)
        self.assertIn("30min", title)

    def test_get_initial_title_no_auto_start(self):
        """Test initial title when auto_start is disabled."""
        self.app.config["auto_start"] = False
        title = self.app.get_initial_title()
        self.assertIn("Click 'Start' to begin", title)

    @patch("notifyme.Notification")
    def test_show_notification(self, mock_notification):
        """Test showing a notification."""
        mock_toast = MagicMock()
        mock_notification.return_value = mock_toast

        self.app.show_notification("Test Title", ["Test Message"])

        mock_notification.assert_called_once()
        mock_toast.set_audio.assert_called_once()
        mock_toast.show.assert_called_once()

    @patch("notifyme.Notification")
    def test_show_blink_notification(self, mock_notification):
        """Test showing a blink notification."""
        mock_toast = MagicMock()
        mock_notification.return_value = mock_toast

        self.app.show_blink_notification()

        call_args = mock_notification.call_args[1]
        self.assertEqual(call_args["title"], "Eye Blink Reminder")

    @patch("notifyme.Notification")
    def test_show_walking_notification(self, mock_notification):
        """Test showing a walking notification."""
        mock_toast = MagicMock()
        mock_notification.return_value = mock_toast

        self.app.show_walking_notification()

        call_args = mock_notification.call_args[1]
        self.assertEqual(call_args["title"], "Walking Reminder")

    @patch("notifyme.Notification")
    def test_show_water_notification(self, mock_notification):
        """Test showing a water notification."""
        mock_toast = MagicMock()
        mock_notification.return_value = mock_toast

        self.app.show_water_notification()

        call_args = mock_notification.call_args[1]
        self.assertEqual(call_args["title"], "Water Reminder")

    def test_create_icon_image(self):
        """Test creating icon image."""
        image = self.app.create_icon_image()
        self.assertIsNotNone(image)
        self.assertEqual(image.size, (64, 64))

    def test_create_menu(self):
        """Test creating system tray menu."""
        menu = self.app.create_menu()
        self.assertIsNotNone(menu)
        # Ensure Help menu item exists
        items = cast(Iterable, getattr(menu, "items", getattr(menu, "_items", ())))
        self.assertTrue(any(item.text == "❓ Help" for item in items))


class TestTimerWorkers(unittest.TestCase):
    """Tests for timer worker threads."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        with patch("notifyme.APP_DATA_DIR", Path(self.temp_dir)):
            with patch("notifyme.get_resource_path") as mock_resource:
                mock_resource.side_effect = lambda x: Path(self.temp_dir) / x
                self.app = NotifyMeApp()
                # Create a simple icon
                from PIL import Image

                img = Image.new("RGB", (64, 64), color="blue")
                img.save(Path(self.temp_dir) / "icon.png")
                self.app.icon_file = Path(self.temp_dir) / "icon.png"

    @patch("notifyme.time.sleep")
    @patch("notifyme.time.time")
    def test_timer_worker_runs_when_not_paused(self, mock_time, mock_sleep):
        """Test that timer worker runs when not paused."""
        mock_time.return_value = 1000.0
        self.app.is_running = True
        self.app.interval_minutes = 1  # 1 minute for quick test

        # Mock to stop after first iteration
        def stop_after_first(*args):
            self.app.is_running = False

        mock_sleep.side_effect = stop_after_first

        with patch.object(self.app, "show_blink_notification"):
            self.app.timer_worker()
            self.assertIsNotNone(self.app.next_reminder_time)

    @patch("notifyme.time.sleep")
    def test_timer_worker_checks_when_paused(self, mock_sleep):
        """Test that timer worker checks frequently when paused."""
        self.app.is_running = True
        self.app.is_paused = True

        # Stop after first check
        def stop_after_first(*args):
            self.app.is_running = False

        mock_sleep.side_effect = stop_after_first

        self.app.timer_worker()
        mock_sleep.assert_called_with(1)


if __name__ == "__main__":
    unittest.main()
