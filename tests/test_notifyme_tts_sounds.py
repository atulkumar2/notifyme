"""Tests ensuring test notifications play sound as a preview."""

import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from notifyme_app.app import NotifyMeApp

sys.path.insert(0, str(Path(__file__).parent.parent))


class TestNotificationSoundPreview(unittest.TestCase):
    """Test that the test notification for eye blink reminders plays sound as a preview."""

    @patch("notifyme_app.notifications.Notification")
    def test_test_blink_notification_plays_sound_when_global_disabled(
        self, mock_notification
    ):
        """
        Test that the test notification for eye blink reminders plays sound as a preview
        even when global sound is disabled, as long as blink sound is enabled.
        """
        mock_toast = MagicMock()
        mock_notification.return_value = mock_toast

        app = NotifyMeApp()
        # Ensure global sound is disabled but blink sound is enabled
        app.config.sound_enabled = False
        app.config.blink_sound_enabled = True

        app.test_blink_notification()

        # The test notification should set audio to Default
        mock_toast.set_audio.assert_called_once()
        mock_toast.show.assert_called_once()


if __name__ == "__main__":
    unittest.main()
