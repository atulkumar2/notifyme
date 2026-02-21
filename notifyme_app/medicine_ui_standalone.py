"""
Standalone entry point for medicine UI dialog.

This module provides a standalone entry point for launching the medicine
management UI in a separate subprocess, avoiding event loop conflicts with
the main pystray application.
"""

import logging
import sys
import tkinter as tk

from notifyme_app.medicine import MedicineManager
from notifyme_app.medicine_ui import MedicineManagementWindow

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def run_medicine_ui() -> None:
    """Run the medicine management UI in a standalone tkinter window."""
    try:
        # Initialize the medicine manager
        medicine_manager = MedicineManager()

        # Create the root window
        root = tk.Tk()
        root.title("Medicine Management")
        root.geometry("800x600")

        # Create and display the medicine management window
        MedicineManagementWindow(root, medicine_manager)

        # Start the event loop
        root.mainloop()

    except Exception as e:
        logging.error("Failed to run medicine UI: %s", e, exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    run_medicine_ui()
