# Configuration Guide

## Configuration File Location

Your settings are saved in:

```
%APPDATA%\NotifyMe\config.json
```

Quick access: Right-click tray icon → "📂 Open Locations" → "⚙ Config Location"

## Configuration Options

### 👁️ interval_minutes

- **Type:** Integer
- **Default:** 20 minutes
- **Range:** 10-60 minutes
- **Purpose:** Time between blink reminders
- **Recommended:** 15-20 min for screen work, 30+ min for mixed tasks

```json
"interval_minutes": 20
```

### 🚶 walking_interval_minutes

- **Type:** Integer
- **Default:** 60 minutes
- **Range:** 30-120 minutes
- **Purpose:** Time between walking reminders
- **Recommended:** 45-60 min for desk jobs, 90-120 min for active roles

```json
"walking_interval_minutes": 60
```

### 💧 water_interval_minutes

- **Type:** Integer
- **Default:** 30 minutes
- **Range:** 20-90 minutes
- **Purpose:** Time between water reminders
- **Recommended:** 20-30 min to build hydration habit, adjust to comfort

```json
"water_interval_minutes": 30
```

### 🧘 pranayama_interval_minutes

- **Type:** Integer
- **Default:** 120 minutes
- **Range:** 60-240 minutes
- **Purpose:** Time between pranayama reminders
- **Recommended:** 120 min for steady work blocks, 180-240 min for lighter days

```json
"pranayama_interval_minutes": 120
```

### 🔊 sound_enabled

- **Type:** Boolean
- **Default:** false
- **Purpose:** Enable/disable notification sounds
- **When to enable:** If you often miss visual notifications

```json
"sound_enabled": false
```

## Example Configurations

### 📺 Heavy Screen Work (Coding, Design, Writing)

```json
{
  "interval_minutes": 15,
  "walking_interval_minutes": 45,
  "water_interval_minutes": 20,
  "pranayama_interval_minutes": 120,
  "sound_enabled": true,
}
```

### 🏢 Office Work (Meetings, Mixed Tasks)

```json
{
  "interval_minutes": 25,
  "walking_interval_minutes": 60,
  "water_interval_minutes": 30,
  "pranayama_interval_minutes": 120,
  "sound_enabled": false,
}
```

### 🎯 Focus Sessions (Pomodoro Style)

```json
{
  "interval_minutes": 25,
  "walking_interval_minutes": 50,
  "water_interval_minutes": 25,
  "pranayama_interval_minutes": 120,
  "sound_enabled": true,
}
```

## Modifying Configuration

**Method 1: Through the App (Easiest)**

1. Right-click tray icon → "📂 Open Locations" → "⚙️ Config Location"
2. Edit the values in `config.json`
3. Changes apply automatically on next reminder

**Method 2: Direct JSON Edit**

1. Open `%APPDATA%\NotifyMe\config.json` in a text editor
2. Modify the values (keep JSON syntax valid)
3. Save the file
4. Restart NotifyMe for changes to apply

## Default Configuration

If `config.json` is missing or corrupted, NotifyMe will create it with these defaults on next launch.

---

[← Back: Usage](usage.md) | [Next: Troubleshooting →](troubleshooting.md)
