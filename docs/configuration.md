# NotifyMe - Configuration Guide

[← Back to Home](index.md) | [🚀 Installation](installation.md) | [📖 Usage](usage.md) | [🆘 Troubleshooting](troubleshooting.md)

---

## Configuration File Location

Your settings are saved in:

```
%APPDATA%\NotifyMe\config.json
```

Quick access: Right-click tray icon → "📂 Open Locations" → "⚙ Config Location"

## Configuration Options

The configuration file uses sections for global settings and per-reminder settings:

```json
{
  "global": {
    "sound_enabled": false,
    "tts_enabled": true,
    "tts_language": "auto",
    "last_run": null
  },
  "reminders": {
    "blink": {
      "interval_minutes": 20,
      "sound_enabled": true,
      "tts_enabled": true,
      "hidden": false
    }
  }
}
```

### 👁️ reminders.blink.interval_minutes

- **Type:** Integer
- **Default:** 20 minutes
- **Range:** 10-60 minutes
- **Purpose:** Time between blink reminders
- **Recommended:** 15-20 min for screen work, 30+ min for mixed tasks

```json
"reminders": {
  "blink": {
    "interval_minutes": 20
  }
}
```

### 🚶 reminders.walking.interval_minutes

- **Type:** Integer
- **Default:** 60 minutes
- **Range:** 30-120 minutes
- **Purpose:** Time between walking reminders
- **Recommended:** 45-60 min for desk jobs, 90-120 min for active roles

```json
"reminders": {
  "walking": {
    "interval_minutes": 60
  }
}
```

### 💧 reminders.water.interval_minutes

- **Type:** Integer
- **Default:** 30 minutes
- **Range:** 20-90 minutes
- **Purpose:** Time between water reminders
- **Recommended:** 20-30 min to build hydration habit, adjust to comfort

```json
"reminders": {
  "water": {
    "interval_minutes": 30
  }
}
```

### 🧘 reminders.pranayama.interval_minutes

- **Type:** Integer
- **Default:** 120 minutes
- **Range:** 60-240 minutes
- **Purpose:** Time between pranayama reminders
- **Recommended:** 120 min for steady work blocks, 180-240 min for lighter days

```json
"reminders": {
  "pranayama": {
    "interval_minutes": 120
  }
}
```

### 🔊 global.sound_enabled

- **Type:** Boolean
- **Default:** false (legacy setting)
- **Purpose:** Enable/disable built-in notification sounds
- **When to enable:** If you often miss visual notifications

```json
"global": {
  "sound_enabled": false
}
```

### 🗣️ global.tts_enabled (NEW)

- **Type:** Boolean
- **Default:** true (enabled for new users)
- **Purpose:** Enable/disable offline Text-to-Speech reminders
- **Details:** Uses Windows SAPI (pyttsx3) for offline speech synthesis. No internet required. Speaks reminders in English by default, or Hindi if a Hindi voice is installed on your system
- **Upgrade Note:** Existing users get this feature enabled automatically on upgrade

```json
"global": {
  "tts_enabled": true
}
```

### 🗣️ global.tts_language

- **Type:** String
- **Default:** "auto"
- **Values:** "auto", "en", "hi"
- **Purpose:** Preferred language for Text-to-Speech
  - `"auto"`: Prefers Hindi if available, falls back to English
  - `"en"`: Always use English
  - `"hi"`: Always use Hindi (if a Hindi voice is installed)

```json
"global": {
  "tts_language": "auto"
}
```

### Per-Reminder TTS Control

Each reminder type can have TTS independently enabled/disabled:

- **Type:** Boolean
- **Default:** true
- **Options:** `reminders.[type].tts_enabled`

```json
"reminders": {
  "blink": { "tts_enabled": true },
  "walking": { "tts_enabled": true },
  "water": { "tts_enabled": true },
  "pranayama": { "tts_enabled": true }
}
```

## Example Configurations

### 📺 Heavy Screen Work (Coding, Design, Writing)

```json
{
  "global": {
    "sound_enabled": true,
    "tts_enabled": true,
    "tts_language": "auto"
  },
  "reminders": {
    "blink": { "interval_minutes": 15 },
    "walking": { "interval_minutes": 45 },
    "water": { "interval_minutes": 20 },
    "pranayama": { "interval_minutes": 120 }
  }
}
```

### 🏢 Office Work (Meetings, Mixed Tasks)

```json
{
  "global": {
    "sound_enabled": false,
    "tts_enabled": true,
    "tts_language": "auto"
  },
  "reminders": {
    "blink": { "interval_minutes": 25 },
    "walking": { "interval_minutes": 60 },
    "water": { "interval_minutes": 30 },
    "pranayama": { "interval_minutes": 120 }
  }
}
```

### 🎯 Focus Sessions (Pomodoro Style)

```json
{
  "global": {
    "sound_enabled": true,
    "tts_enabled": true,
    "tts_language": "en"
  },
  "reminders": {
    "blink": { "interval_minutes": 25 },
    "walking": { "interval_minutes": 50 },
    "water": { "interval_minutes": 25 },
    "pranayama": { "interval_minutes": 120 }
  }
}
```

### 🤫 Silent Mode (TTS Only, No Sounds)

```json
{
  "global": {
    "sound_enabled": false,
    "tts_enabled": true,
    "tts_language": "auto"
  },
  "reminders": {
    "blink": { "interval_minutes": 20 },
    "walking": { "interval_minutes": 60 },
    "water": { "interval_minutes": 30 },
    "pranayama": { "interval_minutes": 120 }
  }
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
