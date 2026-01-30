# Troubleshooting Guide

## Notifications Not Appearing

### Windows Notification Settings

1. Open Settings (Win + I)
2. Go to "System" → "Notifications"
3. Scroll to "NotifyMe" and ensure it's allowed
4. Toggle "Show notifications from apps and other senders" ON

### Test Notifications

1. Right-click NotifyMe icon
2. Select "🔔 Test Notifications"
3. Choose a test type (Blink, Walking, or Water)
4. A notification should appear immediately

### App Not in Notification List

- Try restarting NotifyMe
- If still missing, check Windows Notification Settings → scroll down and enable unknown apps

## Application Won't Start

### Python Not Installed

If running from source:

1. Download Python 3.8+ from [python.org](https://www.python.org/)
2. Install with "Add Python to PATH" checked
3. Restart and try again

### Missing Dependencies

If running from source:

1. Run `setup.bat` in the project folder
2. Or manually: `uv sync`

### Check Logs

1. Right-click NotifyMe icon
2. Select "📂 Open Locations" → "📄 Log Location"
3. Open `notifyme.log` in a text editor
4. Look for error messages

## Settings Not Saving

### Check File Permissions

1. Right-click `%APPDATA%\NotifyMe` folder
2. Select Properties → Security
3. Ensure your account has "Write" permission

### Corrupted Config File

1. Close NotifyMe
2. Delete `%APPDATA%\NotifyMe\config.json`
3. Restart NotifyMe (will create fresh config)

## High CPU Usage

### Check Running Instances

1. Open Task Manager (Ctrl + Shift + Esc)
2. Look for multiple NotifyMe processes
3. Close extras and keep only one running

### Restart Application

1. Right-click tray icon → "❌ Quit"
2. Wait 5 seconds
3. Relaunch NotifyMe

## Reminders Not Triggering

### Verify Reminders Started

1. Right-click tray icon
2. Check that "⚙ Controls" → "▶ Start" shows the app is running
3. Icon title should show intervals like "Blink: 20min"

### Check Individual Pause States

1. Right-click tray icon
2. Select each reminder (Blink, Walking, Water)
3. Ensure they're not showing "⏸" (paused)
4. Un-pause if needed

### Verify Intervals

1. Right-click → reminder type (e.g., "👁 Blink Reminder")
2. Confirm selected interval is reasonable
3. Intervals are counted from last trigger, not elapsed

## Still Need Help?

1. **Check the logs**: Open via tray menu → "📂 Open Locations" → "📄 Log Location"
2. **Review configuration**: "📂 Open Locations" → "⚙ Config Location"
3. **Reset to defaults**: Delete config.json and restart (recreates with defaults)
4. **Reinstall**: Try the latest version from GitHub Releases

---

[← Back: Configuration](configuration.md) | [Next: Home →](index.md)
