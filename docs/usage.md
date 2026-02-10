# NotifyMe - Usage Guide

[← Back to Home](index.md) | [🚀 Installation](installation.md) | [⚙️ Configuration](configuration.md) | [🆘 Troubleshooting](troubleshooting.md)

---

## Getting Started

1. **Launch NotifyMe** - Find the icon in your system tray (bottom-right corner of taskbar)
2. **Right-click the tray icon** - Opens the menu
3. **Select "⚙ Controls" → "▶ Start"** - Begin all reminders

💡 **Tip:** If you don't see the tray icon, click the arrow on the taskbar to show hidden icons

## Understanding the Menu

### ⚙ Controls - Global Control

- **▶ Start** - Begin all reminders (blink, walking, water, pranayama)
- **⏸ Pause All** - Pause all reminders without stopping them
- **▶ Resume All** - Resume all paused reminders
- **🗣️ Global TTS** - Enable/disable text-to-speech for all reminders
- **❓ Help** - Open user guide (local or online)
- **🐙 GitHub Repository** - Visit project repository

### 🗣️ Text-to-Speech (TTS) - Spoken Reminders

NotifyMe includes **offline Text-to-Speech** reminders using Windows SAPI:

**Features:**

- **No internet required** - Runs completely offline on your system
- **Language support** - English by default, Hindi if a Hindi voice is installed
- **Non-blocking** - Speaks in background without freezing the app
- **Per-reminder control** - Enable/disable TTS for each reminder type individually
- **Global control** - Toggle all TTS at once from the Controls menu

**How to use:**

1. **Global TTS:** Right-click tray icon → **"⚙ Controls"** → **"🗣️ Global TTS"** to toggle all
2. **Per-reminder TTS:** Right-click tray icon → Select reminder (👁️ Blink, 🚶 Walking, etc.) → **"🗣️ TTS"** to toggle that specific reminder

**Configuration:**

For advanced control, edit `config.json` (see [Configuration Guide](configuration.md)):

- `tts_enabled`: Toggle global TTS (default: `true`)
- `tts_language`: Set language preference: `"auto"` (default), `"en"`, or `"hi"`
- Per-reminder toggles: `blink_tts_enabled`, `walking_tts_enabled`, `water_tts_enabled`, `pranayama_tts_enabled`

**Example:**

- Global TTS enabled, only Water reminders speak: Enable global TTS, then disable TTS for Blink, Walking, and Pranayama
- Silent Hindi reminders only: Set `tts_language` to `"hi"` and disable `sound_enabled` in config.json

### 👁️ Blink Reminder - Eye Health

- **⏸ Pause/Resume** - Toggle blink reminders on/off independently
- **Intervals** - Choose from:
  - 10, 15, 20 (recommended), 30, 45, or 60 minutes
- ℹ️ **Ideal for:** Screen-intensive work, reading, coding

### 🚶 Walking Reminder - Movement & Circulation

- **⏸ Pause/Resume** - Toggle walking reminders on/off independently
- **Intervals** - Choose from:
  - 30, 45, 60 (recommended), 90, or 120 minutes
- ℹ️ **Ideal for:** Desk jobs, long meetings, sedentary work

### 💧 Water Reminder - Hydration & Focus

- **⏸ Pause/Resume** - Toggle water reminders on/off independently
- **Intervals** - Choose from:
  - 20, 30 (recommended), 45, 60, or 90 minutes
- ℹ️ **Ideal for:** All-day work, mental fatigue prevention

### 🧘 Pranayama Reminder - Breathing & Calm

- **⏸ Pause/Resume** - Toggle pranayama reminders on/off independently
- **Intervals** - Choose from:
  - 60, 90, 120 (recommended), 180, or 240 minutes
- ℹ️ **Ideal for:** Long focus sessions, stress reset, calm productivity

### 💤 Snooze (5 min)

Delay the next reminder by 5 minutes. Useful when you're in the middle of something.

### 🔔 Test Notifications

Verify notifications work correctly before relying on reminders:

- **👁️ Test Blink** - Sends test blink reminder
- **🚶 Test Walking** - Sends test walking reminder
- **💧 Test Water** - Sends test water reminder
- **🧘 Test Pranayama** - Sends test pranayama reminder

### 📂 Open Locations

- **📄 Log Location** - View application activity logs
- **⚙️ Config Location** - Edit settings file directly
- **📦 App Location** - Access application files

## Tips & Tricks

**🎯 Work Smarter:**

- Pause reminders during meetings, calls, or focused tasks
- Use **Snooze** when you're 2 minutes away from a break
- Test notifications before a meeting to avoid surprises
- Take a 2-3 minute pranayama reset every couple of hours for calm focus

**🗣️ Text-to-Speech Tips:**

- **Use TTS instead of sounds** if you work in open offices or shared spaces (no noise!)
- **Test TTS:** Click **"Test [Reminder]"** in each reminder menu to hear TTS preview
- **Hindi speakers:** Run `Add Language` in Windows Settings → Languages to install Hindi voice for `tts_language: "auto"` to use it
- **Silent learning:** Enable TTS only for trickier reminders (e.g., pranayama), keep others visual
- **Accessibility:** TTS is great for situations where visual notifications might be missed (e.g., looking away from screen)

**⏱️ Interval Strategy:**

- **Blink:** 15-20 minutes for intense screen work, 30 min for mixed tasks
- **Walking:** 45-60 minutes for desk work, 90-120 min for movement-intensive jobs
- **Water:** 20-30 minutes to build hydration habit, adjust to comfort level
- **Pranayama:** 120 minutes for steady work blocks, 180-240 for less intense days

**📊 Tracking:**

- Check logs to understand reminder patterns
- Adjust intervals based on when reminders are most useful
- Enable sounds if you forget notifications often

## Notification Behavior

When a reminder triggers:

1. **Windows toast notification** appears in top-right corner
2. **Sound plays** (if enabled in settings)
3. **Notification stays visible** for ~10 seconds (you can extend with mouse hover)
4. **Click to dismiss** early or let it auto-expire
5. **Snooze button** available to delay 5 minutes

💡 **Pro Tip:** If you miss a notification, check your action center (press `Win + A`)

---

[← Back: Installation](installation.md) | [Next: Configuration →](configuration.md)
