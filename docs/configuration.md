# Configuration Guide

## Configuration File Location

Your settings are saved in:

```
%APPDATA%\NotifyMe\config.json
```

Quick access: Right-click tray icon → "📂 Open Locations" → "⚙ Config Location"

## Configuration Options

### interval_minutes

**Type:** Integer
**Default:** 20
**Range:** 10-60 minutes
**Purpose:** Time between blink reminders

```json
"interval_minutes": 20
```

### walking_interval_minutes

**Type:** Integer
**Default:** 60
**Range:** 30-120 minutes
**Purpose:** Time between walking reminders

```json
"walking_interval_minutes": 60
```

### water_interval_minutes

**Type:** Integer
**Default:** 30
**Range:** 20-90 minutes
**Purpose:** Time between water reminders

```json
"water_interval_minutes": 30
```

### sound_enabled

**Type:** Boolean
**Default:** false
**Purpose:** Enable/disable notification sounds

```json
"sound_enabled": false
```

### auto_start

**Type:** Boolean
**Default:** false
**Purpose:** Automatically start reminders when app launches

```json
"auto_start": false
```

## Example Configuration

```json
{
  "interval_minutes": 20,
  "walking_interval_minutes": 60,
  "water_interval_minutes": 30,
  "sound_enabled": false,
  "auto_start": true,
  "last_run": "2026-01-30T14:00:00"
}
```

## Modifying Configuration

### Method 1: Using the Tray Menu (Easiest)

1. Right-click the NotifyMe icon
2. Select the reminder type (Blink, Walking, or Water)
3. Choose your desired interval
4. Settings are saved automatically

### Method 2: Editing the JSON File

1. Open `%APPDATA%\NotifyMe\config.json` in a text editor
2. Modify the values
3. Save the file
4. Restart NotifyMe for changes to take effect

## Default Configuration

If `config.json` is missing or corrupted, NotifyMe will create it with these defaults on next launch.

---

[← Back: Usage](usage.md) | [Next: Troubleshooting →](troubleshooting.md)
