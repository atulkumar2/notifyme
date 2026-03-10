"""Tests for Linux pystray backend selection."""

import os
import unittest
from unittest.mock import patch

from notifyme_app.tray_backend import configure_pystray_backend


class TestTrayBackend(unittest.TestCase):
    """Tests for pre-import pystray backend configuration."""

    @patch.dict(os.environ, {}, clear=True)
    @patch("notifyme_app.tray_backend.sys.platform", "linux")
    def test_falls_back_to_gtk_when_appindicator_namespaces_missing(self) -> None:
        """Linux should force GTK when gi exists but AppIndicator typelibs do not."""

        class FakeGI:
            def require_version(self, namespace, _version):
                if namespace == "Gtk":
                    return
                raise ValueError(f"Namespace {namespace} not available")

        with patch("builtins.__import__", side_effect=lambda name, *args, **kwargs: FakeGI() if name == "gi" else __import__(name, *args, **kwargs)):
            configure_pystray_backend()

        self.assertEqual(os.environ.get("PYSTRAY_BACKEND"), "gtk")


if __name__ == "__main__":
    unittest.main()
