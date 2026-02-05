"""
Unit tests for NotifyMe notifications.
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from winotify import audio

sys.path.insert(0, str(Path(__file__).parent.parent))

from notifyme_app.notifications import NotificationManager


class TestNotificationManager(unittest.TestCase):
    """Tests for NotificationManager."""

    @patch("notifyme_app.notifications.Notification")
    def test_show_notification_silent_does_not_set_audio(self, mock_notification):
        """Silent notifications should not set audio explicitly."""
        mock_toast = MagicMock()
        mock_notification.return_value = mock_toast
        manager = NotificationManager()

        with patch.object(NotificationManager, "_get_icon_path", return_value=None):
            manager.show_notification("Test", ["Message"], sound_enabled=False)

        mock_toast.set_audio.assert_not_called()
        mock_toast.show.assert_called_once()

    @patch("notifyme_app.notifications.Notification")
    def test_show_notification_with_sound_sets_audio_default(self, mock_notification):
        """Sound-enabled notifications should set default audio."""
        mock_toast = MagicMock()
        mock_notification.return_value = mock_toast
        manager = NotificationManager()

        with patch.object(NotificationManager, "_get_icon_path", return_value=None):
            manager.show_notification("Test", ["Message"], sound_enabled=True)

        mock_toast.set_audio.assert_called_once_with(audio.Default, loop=False)
        mock_toast.show.assert_called_once()


if __name__ == "__main__":
    unittest.main()
