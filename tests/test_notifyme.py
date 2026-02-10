"""
Unit tests for the NotifyMe application.
"""

import sys
import tempfile
import unittest
from pathlib import Path
from typing import Iterable, cast
from unittest.mock import MagicMock, patch

from PIL import Image

from notifyme import APP_VERSION, NotifyMeApp, get_app_data_dir, get_resource_path

sys.path.insert(0, str(Path(__file__).parent.parent))


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
        self.assertEqual(self.app.pranayama_interval_minutes, 120)
        self.assertFalse(self.app.is_running)
        self.assertFalse(self.app.is_paused)

    def test_version_matches_pyproject(self):
        """Ensure APP_VERSION matches pyproject.toml version."""
        pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
        content = pyproject_path.read_text(encoding="utf-8")
        version_line = next(
            (
                line
                for line in content.splitlines()
                if line.strip().startswith("version")
            ),
            "",
        )
        _, value = version_line.split("=", 1)
        pyproject_version = value.strip().strip('"').strip("'")
        self.assertEqual(APP_VERSION, pyproject_version)

    def test_get_default_config(self):
        """Test default configuration values."""
        config = self.app.get_default_config()
        self.assertEqual(config["interval_minutes"], 20)
        self.assertEqual(config["walking_interval_minutes"], 60)
        self.assertEqual(config["water_interval_minutes"], 30)
        self.assertEqual(config["pranayama_interval_minutes"], 120)
        self.assertFalse(config["sound_enabled"])

    def test_save_and_load_config(self):
        """Test saving and loading configuration."""
        self.app.config["interval_minutes"] = 30
        self.app.config["walking_interval_minutes"] = 90
        self.app.config["pranayama_interval_minutes"] = 180
        self.app.save_config()

        # Load config in a new instance
        loaded_config = self.app.load_config()
        self.assertEqual(loaded_config["interval_minutes"], 30)
        self.assertEqual(loaded_config["walking_interval_minutes"], 90)
        self.assertEqual(loaded_config["pranayama_interval_minutes"], 180)

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

    def test_set_pranayama_interval(self):
        """Test setting pranayama reminder interval."""
        set_func = self.app.set_pranayama_interval(180)
        set_func()
        self.assertEqual(self.app.pranayama_interval_minutes, 180)
        self.assertEqual(self.app.config["pranayama_interval_minutes"], 180)

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
        self.app.is_pranayama_paused = True
        self.app.pause_reminders()
        self.assertTrue(self.app.is_paused)
        self.assertTrue(self.app.is_blink_paused)
        self.assertFalse(self.app.is_walking_paused)
        self.assertTrue(self.app.is_water_paused)
        self.assertTrue(self.app.is_pranayama_paused)

    def test_resume_reminders(self):
        """Test resuming all reminders clears all pause states."""
        self.app.is_running = False
        self.app.is_paused = True
        self.app.is_blink_paused = True
        self.app.is_walking_paused = True
        self.app.is_water_paused = True
        self.app.is_pranayama_paused = True
        self.app.resume_reminders()
        self.assertFalse(self.app.is_paused)
        self.assertFalse(self.app.is_blink_paused)
        self.assertFalse(self.app.is_walking_paused)
        self.assertFalse(self.app.is_water_paused)
        self.assertFalse(self.app.is_pranayama_paused)

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

    def test_toggle_pranayama_pause(self):
        """Test toggling pranayama reminder pause."""
        initial_state = self.app.is_pranayama_paused
        self.app.toggle_pranayama_pause()
        self.assertEqual(self.app.is_pranayama_paused, not initial_state)

    def test_stop_reminders(self):
        """Test stopping reminders."""
        self.app.is_running = True
        with patch.object(self.app, "icon", MagicMock()):
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
        self.app.pranayama_interval_minutes = 120
        self.app.update_icon_title()
        self.assertIn("20min", self.app.icon.title)
        self.assertIn("60min", self.app.icon.title)
        self.assertIn("30min", self.app.icon.title)
        self.assertIn("120min", self.app.icon.title)

    def test_update_icon_title_individual_paused(self):
        """Test icon title when individual reminders are paused."""
        self.app.icon = MagicMock()
        self.app.is_paused = False
        self.app.is_blink_paused = True
        self.app.update_icon_title()
        self.assertIn("⏸", self.app.icon.title)

    def test_get_initial_title(self):
        """Test initial title shows reminder intervals."""
        self.app.interval_minutes = 20
        self.app.walking_interval_minutes = 60
        self.app.water_interval_minutes = 30
        self.app.pranayama_interval_minutes = 120
        title = self.app.get_initial_title()
        self.assertIn("20min", title)
        self.assertIn("60min", title)
        self.assertIn("30min", title)
        self.assertIn("120min", title)

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

    @patch("notifyme.Notification")
    def test_show_pranayama_notification(self, mock_notification):
        """Test showing a pranayama notification."""
        mock_toast = MagicMock()
        mock_notification.return_value = mock_toast

        self.app.show_pranayama_notification()

        call_args = mock_notification.call_args[1]
        self.assertEqual(call_args["title"], "Pranayama Reminder")

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
                img = Image.new("RGB", (64, 64), color="blue")
                img.save(Path(self.temp_dir) / "icon.png")
                self.app.icon_file = Path(self.temp_dir) / "icon.png"

    @patch("notifyme.get_idle_seconds")
    @patch("notifyme.time.sleep")
    @patch("notifyme.time.time")
    def test_timer_worker_runs_when_not_paused(self, mock_time, mock_sleep, mock_idle):
        """Test that timer worker runs when not paused."""
        mock_time.return_value = 1000.0
        mock_idle.return_value = None
        self.app.is_running = True
        self.app.interval_minutes = 1  # 1 minute for quick test
        self.app.blink_offset_seconds = 0

        # Mock to stop after first iteration
        def stop_after_first(*args):
            self.app.is_running = False

        mock_sleep.side_effect = stop_after_first

        with patch.object(self.app, "show_blink_notification"):
            self.app.timer_worker()
            self.assertIsNotNone(self.app.next_reminder_time)

    @patch("notifyme.get_idle_seconds")
    @patch("notifyme.time.sleep")
    @patch("notifyme.time.time")
    def test_timer_worker_resets_on_idle(self, mock_time, mock_sleep, mock_idle):
        """Test that idle time resets the timer without showing a reminder."""
        mock_time.return_value = 1000.0
        mock_idle.return_value = 60.0
        self.app.is_running = True
        self.app.interval_minutes = 1
        self.app.blink_offset_seconds = 0

        def stop_after_first(*args):
            self.app.is_running = False

        mock_sleep.side_effect = stop_after_first

        with patch.object(self.app, "show_blink_notification") as mock_show:
            self.app.timer_worker()
            mock_show.assert_not_called()
            self.assertEqual(self.app.next_reminder_time, 1060.0)
            self.assertTrue(self.app._blink_idle_suppressed)

    @patch("notifyme.get_idle_seconds")
    @patch("notifyme.time.sleep")
    @patch("notifyme.time.time")
    def test_timer_worker_fires_after_idle_clears(
        self, mock_time, mock_sleep, mock_idle
    ):
        """Test that a reminder fires once idle clears and time elapses."""
        mock_time.side_effect = [1000.0, 1061.0]
        mock_idle.side_effect = [60.0, 0.0]
        self.app.is_running = True
        self.app.interval_minutes = 1
        self.app.blink_offset_seconds = 0

        call_count = {"count": 0}

        def stop_after_second(*args):
            call_count["count"] += 1
            if call_count["count"] >= 2:
                self.app.is_running = False

        mock_sleep.side_effect = stop_after_second

        with patch.object(self.app, "show_blink_notification") as mock_show:
            self.app.timer_worker()
            mock_show.assert_called_once()

    @patch("notifyme.get_idle_seconds")
    @patch("notifyme.time.sleep")
    @patch("notifyme.time.time")
    def test_walking_timer_worker_resets_on_idle(
        self, mock_time, mock_sleep, mock_idle
    ):
        """Test that walking idle time resets the timer without showing a reminder."""
        mock_time.return_value = 2000.0
        mock_idle.return_value = 60.0
        self.app.is_running = True
        self.app.walking_interval_minutes = 1
        self.app.walking_offset_seconds = 0

        def stop_after_first(*args):
            self.app.is_running = False

        mock_sleep.side_effect = stop_after_first

        with patch.object(self.app, "show_walking_notification") as mock_show:
            self.app.walking_timer_worker()
            mock_show.assert_not_called()
            self.assertEqual(self.app.next_walking_reminder_time, 2060.0)
            self.assertTrue(self.app._walking_idle_suppressed)

    @patch("notifyme.get_idle_seconds")
    @patch("notifyme.time.sleep")
    @patch("notifyme.time.time")
    def test_walking_timer_worker_fires_after_idle_clears(
        self, mock_time, mock_sleep, mock_idle
    ):
        """Test that walking reminder fires once idle clears and time elapses."""
        mock_time.side_effect = [2000.0, 2061.0]
        mock_idle.side_effect = [60.0, 0.0]
        self.app.is_running = True
        self.app.walking_interval_minutes = 1
        self.app.walking_offset_seconds = 0

        call_count = {"count": 0}

        def stop_after_second(*args):
            call_count["count"] += 1
            if call_count["count"] >= 2:
                self.app.is_running = False

        mock_sleep.side_effect = stop_after_second

        with patch.object(self.app, "show_walking_notification") as mock_show:
            self.app.walking_timer_worker()
            mock_show.assert_called_once()

    @patch("notifyme.get_idle_seconds")
    @patch("notifyme.time.sleep")
    @patch("notifyme.time.time")
    def test_water_timer_worker_resets_on_idle(self, mock_time, mock_sleep, mock_idle):
        """Test that water idle time resets the timer without showing a reminder."""
        mock_time.return_value = 3000.0
        mock_idle.return_value = 60.0
        self.app.is_running = True
        self.app.water_interval_minutes = 1
        self.app.water_offset_seconds = 0

        def stop_after_first(*args):
            self.app.is_running = False

        mock_sleep.side_effect = stop_after_first

        with patch.object(self.app, "show_water_notification") as mock_show:
            self.app.water_timer_worker()
            mock_show.assert_not_called()
            self.assertEqual(self.app.next_water_reminder_time, 3060.0)
            self.assertTrue(self.app._water_idle_suppressed)

    @patch("notifyme.get_idle_seconds")
    @patch("notifyme.time.sleep")
    @patch("notifyme.time.time")
    def test_water_timer_worker_fires_after_idle_clears(
        self, mock_time, mock_sleep, mock_idle
    ):
        """Test that water reminder fires once idle clears and time elapses."""
        mock_time.side_effect = [3000.0, 3061.0]
        mock_idle.side_effect = [60.0, 0.0]
        self.app.is_running = True
        self.app.water_interval_minutes = 1
        self.app.water_offset_seconds = 0

        call_count = {"count": 0}

        def stop_after_second(*args):
            call_count["count"] += 1
            if call_count["count"] >= 2:
                self.app.is_running = False

        mock_sleep.side_effect = stop_after_second

        with patch.object(self.app, "show_water_notification") as mock_show:
            self.app.water_timer_worker()
            mock_show.assert_called_once()

    @patch("notifyme.get_idle_seconds")
    @patch("notifyme.time.sleep")
    @patch("notifyme.time.time")
    def test_pranayama_timer_worker_resets_on_idle(
        self, mock_time, mock_sleep, mock_idle
    ):
        """Test that pranayama idle time resets the timer without showing a reminder."""
        mock_time.return_value = 4000.0
        mock_idle.return_value = 120.0
        self.app.is_running = True
        self.app.pranayama_interval_minutes = 2
        self.app.pranayama_offset_seconds = 0

        def stop_after_first(*args):
            self.app.is_running = False

        mock_sleep.side_effect = stop_after_first

        with patch.object(self.app, "show_pranayama_notification") as mock_show:
            self.app.pranayama_timer_worker()
            mock_show.assert_not_called()
            self.assertEqual(self.app.next_pranayama_reminder_time, 4120.0)
            self.assertTrue(self.app._pranayama_idle_suppressed)

    @patch("notifyme.get_idle_seconds")
    @patch("notifyme.time.sleep")
    @patch("notifyme.time.time")
    def test_pranayama_timer_worker_fires_after_idle_clears(
        self, mock_time, mock_sleep, mock_idle
    ):
        """Test that pranayama reminder fires once idle clears and time elapses."""
        mock_time.side_effect = [4000.0, 4121.0]
        mock_idle.side_effect = [120.0, 0.0]
        self.app.is_running = True
        self.app.pranayama_interval_minutes = 2
        self.app.pranayama_offset_seconds = 0

        call_count = {"count": 0}

        def stop_after_second(*args):
            call_count["count"] += 1
            if call_count["count"] >= 2:
                self.app.is_running = False

        mock_sleep.side_effect = stop_after_second

        with patch.object(self.app, "show_pranayama_notification") as mock_show:
            self.app.pranayama_timer_worker()
            mock_show.assert_called_once()

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
