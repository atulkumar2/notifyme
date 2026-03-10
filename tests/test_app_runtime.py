"""Runtime tests for the main NotifyMe application loop."""

import signal
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from notifyme_app.app import NotifyMeApp

sys.path.insert(0, str(Path(__file__).parent.parent))


class TestNotifyMeAppRuntime(unittest.TestCase):
    """Tests for application runtime shutdown behavior."""

    @patch("notifyme_app.app.Icon")
    def test_run_registers_signals_and_stops_cleanly(self, mock_icon_cls) -> None:
        """The tray loop should run on the main thread with signal-driven shutdown."""
        mock_icon = MagicMock()
        mock_icon.visible = False
        captured_setup = {}

        def run_side_effect(*, setup):
            captured_setup["setup"] = setup
            setup(mock_icon)

        mock_icon_cls.return_value = mock_icon
        mock_icon.run.side_effect = run_side_effect

        app = NotifyMeApp()
        app.start_reminders = MagicMock()
        app._start_background_watchers = MagicMock()
        app.system.show_startup_help = MagicMock()
        app.notifications.show_welcome_notification = MagicMock()
        app.updater.check_for_updates_async = MagicMock()

        original_getsignal = signal.getsignal
        installed_handlers = {}
        captured_handlers = {}

        def fake_signal(sig, handler):
            installed_handlers[sig] = handler
            if sig in (signal.SIGINT, signal.SIGTERM) and sig not in captured_handlers:
                captured_handlers[sig] = handler

        with patch("notifyme_app.app.signal.signal", side_effect=fake_signal):
            with patch(
                "notifyme_app.app.signal.getsignal", side_effect=original_getsignal
            ):
                app.run()

        self.assertIn("setup", captured_setup)
        mock_icon.run.assert_called_once()
        self.assertTrue(mock_icon.visible)
        app.start_reminders.assert_called_once_with()
        app._start_background_watchers.assert_called_once_with()
        self.assertIn(signal.SIGINT, captured_handlers)
        self.assertIn(signal.SIGTERM, captured_handlers)

        captured_handlers[signal.SIGINT](signal.SIGINT, None)

        mock_icon.stop.assert_called_once_with()
        self.assertTrue(app._quitting)


if __name__ == "__main__":
    unittest.main()
