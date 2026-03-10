"""
Unit tests for NotifyMe notifications.
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from notifyme_app.notifications import NotificationManager

sys.path.insert(0, str(Path(__file__).parent.parent))


class TestNotificationManager(unittest.TestCase):
    """Tests for NotificationManager."""

    @patch("notifyme_app.notifications.plyer_notification")
    def test_show_notification_uses_plyer_on_linux(self, mock_notify):
        """Linux notifications should use plyer."""
        manager = NotificationManager()

        with patch("notifyme_app.notifications.sys.platform", "linux"):
            manager.show_notification("Test", ["Message"], sound_enabled=False)

        mock_notify.notify.assert_called_once()

    @patch("notifyme_app.notifications.Notification")
    @patch("notifyme_app.notifications.audio")
    def test_show_notification_with_sound_sets_audio_default(
        self, mock_audio, mock_notification
    ):
        """Windows notifications should set default audio when enabled."""
        mock_toast = MagicMock()
        mock_notification.return_value = mock_toast
        manager = NotificationManager()
        mock_audio.Default = "default"

        with patch("notifyme_app.notifications.sys.platform", "win32"):
            manager.show_notification("Test", ["Message"], sound_enabled=True)

        mock_toast.set_audio.assert_called_once_with("default", loop=False)
        mock_toast.show.assert_called_once()


if __name__ == "__main__":
    unittest.main()
