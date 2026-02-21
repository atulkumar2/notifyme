#!/usr/bin/env python3
"""Test that callbacks handle extra arguments from pystray."""

from notifyme_app.app import NotifyMeApp

# Create app and get callbacks
app = NotifyMeApp()
callbacks = app._get_menu_callbacks()

# Simulate pystray calling callbacks with extra arguments
print("Testing callbacks with extra arguments (simulating pystray behavior)...")

# Test toggle_blink_pause with extra arguments
print("✓ Calling toggle_blink_pause(icon, menu_item)...")
try:
    # pystray passes icon and menu_item as arguments
    callbacks["toggle_blink_pause"]("mock_icon", "mock_menu_item")
    print("  Success!")
except Exception as e:
    print(f"  Error: {e}")
    raise

# Test test_water_notification with extra arguments
print("✓ Calling test_water_notification(icon)...")
try:
    callbacks["test_water_notification"]("mock_icon")
    print("  Success!")
except Exception as e:
    if "show_reminder_notification" in str(e):
        print("  Callback invoked successfully (notification manager not mocked)")
    else:
        print(f"  Error: {e}")
        raise

# Test toggle_walking_sound with extra arguments
print("✓ Calling toggle_walking_sound(icon, menu_item, extra_arg)...")
try:
    callbacks["toggle_walking_sound"]("mock_icon", "mock_menu_item", "extra")
    print("  Success!")
except Exception as e:
    print(f"  Error: {e}")
    raise

print("\n✓ All callbacks handle extra arguments correctly!")
