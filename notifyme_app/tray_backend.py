"""Helpers for selecting a usable pystray backend before import time."""

import os
import sys


def configure_pystray_backend() -> None:
    """Choose a safe Linux pystray backend before importing pystray.

    pystray's Linux autodetection tries AppIndicator first. In environments
    where PyGObject is installed but the AppIndicator typelib is missing,
    pystray raises ValueError during import instead of falling back cleanly.
    Force the GTK backend in that case so the tray icon and menus still work.
    """

    if sys.platform != "linux" or os.environ.get("PYSTRAY_BACKEND"):
        return

    try:
        import gi

        gi.require_version("Gtk", "3.0")
    except Exception:
        return

    for namespace in ("AppIndicator3", "AyatanaAppIndicator3"):
        try:
            gi.require_version(namespace, "0.1")
            return
        except ValueError:
            continue
        except Exception:
            return

    os.environ["PYSTRAY_BACKEND"] = "gtk"
