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
- **Default:** false (legacy setting)
- **Purpose:** Enable/disable built-in notification sounds
- **When to enable:** If you often miss visual notifications

```json
"sound_enabled": false
```

### 🗣️ tts_enabled (NEW)

- **Type:** Boolean
- **Default:** true (enabled for new users)
- **Purpose:** Enable/disable offline Text-to-Speech reminders
- **Details:** Uses Windows SAPI (pyttsx3) for offline speech synthesis. No internet required. Speaks reminders in English by default, or Hindi if a Hindi voice is installed on your system
- **Upgrade Note:** Existing users get this feature enabled automatically on upgrade

```json
"tts_enabled": true
```

### 🗣️ tts_language

- **Type:** String
- **Default:** "auto"
- **Values:** "auto", "en", "hi"
- **Purpose:** Preferred language for Text-to-Speech
  - `"auto"`: Prefers Hindi if available, falls back to English
  - `"en"`: Always use English
  - `"hi"`: Always use Hindi (if a Hindi voice is installed)

```json
"tts_language": "auto"
```

### Per-Reminder TTS Control

Each reminder type can have TTS independently enabled/disabled:

- **Type:** Boolean
- **Default:** true
- **Options:** `blink_tts_enabled`, `walking_tts_enabled`, `water_tts_enabled`, `pranayama_tts_enabled`

```json
"blink_tts_enabled": true,
"walking_tts_enabled": true,
"water_tts_enabled": true,
"pranayama_tts_enabled": true
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
  "tts_enabled": true,
  "tts_language": "auto"
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
  "tts_enabled": true,
  "tts_language": "auto"
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
  "tts_enabled": true,
  "tts_language": "en"
}
```

### 🤫 Silent Mode (TTS Only, No Sounds)

```json
{
  "interval_minutes": 20,
  "walking_interval_minutes": 60,
  "water_interval_minutes": 30,
  "pranayama_interval_minutes": 120,
  "sound_enabled": false,
  "tts_enabled": true,
  "tts_language": "auto"
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
