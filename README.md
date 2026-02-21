# 💧 NotifyMe

A modern Windows desktop application that helps you stay healthy by reminding you to blink your eyes, take walking breaks, stay hydrated, and practice pranayama at regular intervals.

<img src="icon.png" alt="NotifyMe Icon" width="160" height="160" />

Online docs: <https://atulkumar2.github.io/notifyme/>

## 📌 Table of Contents

- [Features](#features)
- [Quick Start](#quick-start)
- [New Modular Architecture](#new-modular-architecture)
- [Data Storage](#data-storage)
- [How to Use](#how-to-use)
- [Why These Reminders?](#why-these-reminders)
- [Configuration](#configuration)
- [Reminder Messages](#reminder-messages)
- [Technical Details](#technical-details)
- [Build & Development Scripts](#build--development-scripts)
- [License](#license)
- [Contributing](#contributing)
- [Connect](#connect)
- [Learn More](#learn-more)
- [Tips for Health](#tips-for-health)

## Features

- **Quad Reminders**: Eye blink reminders (default: 20 min), walking reminders (default: 60 min), water drinking reminders (default: 30 min), and pranayama reminders (default: 120 min)
- **Background Operation**: Runs silently in the system tray
- **Windows Toast Notifications**: Native Windows 10/11 notifications with sound control
- **Customizable Intervals**:
  - Blink reminders: 10-60 minutes
  - Walking reminders: 30-120 minutes
  - Water reminders: 20-90 minutes
  - Pranayama reminders: 60-240 minutes
- **Advanced Controls**:
  - **Global Sound Control**: Enable/disable sounds for all notifications
  - **Per-Reminder Sound Control**: Individual sound settings for each reminder type
  - **Hide/Show Reminders**: Hide specific reminder types from the menu while keeping them active
  - **Flexible Pause/Resume**: Pause all reminders at once, or pause each reminder type individually
- **Smart Features**:
  - **Startup Help**: Automatically opens help page when first launched
  - **Welcome Notification**: Friendly introduction when app starts
  - **Snooze Function**: Delay the next reminder by 5 minutes
  - **Idle Detection**: Pauses reminders when system is idle or locked
- **User Experience**:
  - **Randomized Messages**: Variety of friendly reminder messages
  - **Persistent Settings**: Your preferences are saved between sessions
  - **Dynamic Menu**: Menu adapts based on your visibility and sound preferences
  - **Offline Text-to-Speech**: Optional TTS using Windows SAPI (pyttsx3). Enables offline spoken reminders (English by default, attempts Hindi when a Hindi voice is installed). Toggle per-reminder and globally via the tray menu.
  - **Rolling Logs**: Log files automatically rotate to prevent disk space issues
  - **Easy Access**: Quickly open log, config, and app locations from the system tray menu
  - **Visual Menu Icons**: Emoji icons for easy navigation of menu options

## Quick Start

### Option 1: Download Pre-built Executable (Recommended)

1. **Download** the latest `NotifyMe.exe` from [GitHub Releases](../../releases/latest)
2. **Run** `NotifyMe.exe` - no installation required!
3. **Optional: Auto-start with Windows**:
   - Press `Win + R`, type `shell:startup`, press Enter
   - Copy `NotifyMe.exe` or create a shortcut there

### Option 2: Run from Source

#### Prerequisites

- Windows 10 or Windows 11
- Python 3.13+ (greater than 3.13)

#### Installation

1. **Clone or download this repository**

2. **Run setup**:

   **Batch** (for CMD):

   ```bash
   scripts\setup.bat
   ```

   **PowerShell** (recommended):

   ```powershell
   .\scripts\setup.ps1
   ```

   Or manually with uv:

   ```bash
   uv sync
   ```

3. **Run the application**:

   **Batch** (for CMD):

   ```bash
   scripts\run.bat
   ```

   **PowerShell**:

   ```powershell
   .\scripts\run.ps1
   ```

   Or manually:

   ```bash
   python notifyme.py
   ```

The application will appear in your system tray (look for the icon in the bottom-right corner of your screen).

## New Modular Architecture

NotifyMe has been refactored into a clean, modular architecture for better maintainability and extensibility. The application is now organized into focused modules:

### Module Structure

```sh
notifyme_app/
├── __init__.py          # Package initialization
├── app.py              # Main application coordinator
├── config.py           # Configuration management
├── constants.py        # Constants and messages
├── menu.py             # System tray menu management
├── notifications.py    # Toast notification system
├── system.py           # System integration
├── timers.py           # Background timer management
├── updater.py          # Update checking
├── utils.py            # Utility functions
└── README.md           # Module documentation
```

### Benefits of the New Architecture

- **🔧 Maintainability**: Each module has a single, clear responsibility
- **🧪 Testability**: Components can be tested in isolation
- **📈 Extensibility**: Easy to add new features without affecting existing code
- **♻️ Reusability**: Components can be reused in different contexts
- **📚 Documentation**: Each module is well-documented with clear interfaces

### Migration

- **For Users**: No changes needed - all functionality remains the same
- **For Developers**: See [MIGRATION.md](MIGRATION.md) for detailed migration guide
- **Entry Point**: `python notifyme.py` (now uses the new modular architecture)

### Building a Standalone Executable (For Developers)

You can create a portable `.exe` file that doesn't require Python:

1. **Build the executable**:

   **Batch** (for CMD):

   ```bash
   scripts\build.bat
   ```

   **PowerShell** (recommended):

   ```powershell
   .\scripts\build.ps1
   ```

   Or manually:

   ```bash
   .venv\Scripts\python.exe -m PyInstaller NotifyMe.spec
   ```

   The build process automatically:
   - Bundles all dependencies (including pyttsx3 for offline TTS)
   - Includes required data files (icon, help HTML)
   - Detects and includes hidden modules

2. **Find your executable** at `dist/NotifyMe.exe` (~18.5 MB)

3. **Optional: Generate SHA256 hash** for integrity verification:

   ```bash
   .venv\Scripts\python.exe -c "import hashlib; p = r'dist\NotifyMe.exe'; h = hashlib.sha256(open(p, 'rb').read()).hexdigest(); print(f'{h}  NotifyMe.exe')"
   ```

### Running Tests (For Developers)

The project includes comprehensive unit tests to ensure reliability:

1. **Run all tests**:

   **Batch** (for CMD):

   ```bash
   scripts\run_tests.bat
   ```

   **PowerShell** (recommended):

   ```powershell
   .\scripts\run_tests.ps1
   ```

   Or manually:

   ```bash
   uv run python -m pytest tests/test_notifyme.py -v
   ```

2. **Run tests with coverage**:

   ```bash
   uv run python -m pytest tests/test_notifyme.py --cov=notifyme --cov-report=html
   ```

3. **View coverage report**: Open `htmlcov/index.html` in your browser

The test suite covers:

- Configuration management
- Reminder intervals and timing
- Pause/resume functionality
- Menu creation and actions
- File location helpers
- Notification display
- System tray integration

## Data Storage

NotifyMe stores its configuration and logs in your user data folder:

- **Windows**: `%APPDATA%\NotifyMe\`
  - `config.json` - Your preferences
  - `notifyme.log` - Application logs

To open this folder:

- **Via System Tray**: Right-click the NotifyMe icon → **"📂 Open Locations"** → **"📄 Log Location"** or **"⚙ Config Location"**
- **Via Windows**: Press `Win + R`, type `%APPDATA%\NotifyMe`, press Enter

## How to Use

### First Launch

When you first run NotifyMe:

1. **Help Page Opens**: The application automatically opens the online help page
2. **Welcome Notification**: A friendly notification explains that the app is running in your system tray
3. **Ready to Use**: All reminders are enabled by default

### Starting Reminders

1. Right-click the icon in the system tray
2. Open **"⚙ Controls"** and click **"▶ Start"** to begin receiving reminders
3. You'll receive blink reminders every 20 minutes, walking reminders every 60 minutes, water reminders every 30 minutes, and pranayama reminders every 120 minutes (defaults)
4. Hover over the system tray icon to see the current status of all reminders

### Sound Controls

**Global Sound Control:**

1. Right-click the system tray icon
2. Open **"⚙ Controls"**
3. Click **"🔊 Global Sound"** to toggle sounds for all notifications

**Per-Reminder Sound Control:**

1. Right-click the system tray icon
2. Hover over any reminder type (e.g., **"👁 Blink Reminder"**)
3. Click **"🔊 Sound"** to toggle sound for that specific reminder type
4. A checkmark (✓) indicates sound is enabled for that reminder

### Text-to-Speech (TTS) Controls

**Global TTS Control:**

1. Right-click the system tray icon
2. Open **"⚙ Controls"**
3. Click **"🗣️ Global TTS"** to toggle text-to-speech for all reminders
4. A checkmark (✓) indicates TTS is enabled

**Per-Reminder TTS Control:**

1. Right-click the system tray icon
2. Hover over any reminder type (e.g., **"👁 Blink Reminder"**)
3. Click **"🗣️ TTS"** to toggle TTS for that specific reminder type
4. A checkmark (✓) indicates TTS is enabled for that reminder

**Language Preference:**

- Edit `%APPDATA%\NotifyMe\config.json` and set `tts_language`:
  - `"auto"` (default) - Prefers Hindi if available, falls back to English
  - `"en"` - Always use English
  - `"hi"` - Restrict to Hindi only (install Hindi voice first)

### Hiding/Showing Reminders

**Hide a Reminder:**

1. Right-click the system tray icon
2. Hover over the reminder you want to hide
3. Click **"🙈 Hide Reminder"**
4. The reminder will disappear from the main menu but continue running

**Show Hidden Reminders:**

1. Right-click the system tray icon
2. Look for **"👁 Hidden Reminders"** menu (appears when any reminders are hidden)
3. Click on the reminder you want to show again

### Customizing the Intervals

1. Right-click the system tray icon
2. Hover over **"Blink Reminder"**, **"Walking Reminder"**, **"Water Reminder"**, or **"Pranayama Reminder"**
3. Choose your preferred interval:
   - Blink: 10, 15, 20, 30, 45, or 60 minutes
   - Walking: 30, 45, 60, 90, or 120 minutes
   - Water: 20, 30, 45, 60, or 90 minutes
   - Pranayama: 60, 90, 120, 180, or 240 minutes

### Testing Notifications

1. Right-click the system tray icon
2. Hover over **"🔔 Test Notifications"**
3. Click **"Test Blink"**, **"Test Walking"**, **"Test Water"**, or **"Test Pranayama"** to preview notifications

### Pausing and Resuming

**Pause/Resume All:**

- Open **"⚙ Controls"** and click **"⏸ Pause All"** to temporarily stop all reminders
- Open **"⚙ Controls"** and click **"▶ Resume All"** to continue receiving all reminders

**Pause/Resume Individual Reminders:**

1. Hover over **"Blink Reminder"**, **"Walking Reminder"**, **"Water Reminder"**, or **"Pranayama Reminder"**
2. Click **"⏸ Pause/Resume"** to toggle that specific reminder
3. A checkmark (✓) indicates the reminder is currently running
4. The system tray icon shows ⏸ next to paused reminders

### Snoozing a Reminder

- Click **"💤 Snooze (5 min)"** to delay the next reminder by 5 minutes

### Accessing Locations

Quickly access important files and folders:

1. Right-click the system tray icon
2. Hover over **"📂 Open Locations"**
3. Select:
   - **"📄 Log Location"** - Opens the folder containing application logs
   - **"⚙ Config Location"** - Opens the folder containing config.json
   - **"📦 App Location"** - Opens the folder containing the executable or script

### Getting Help

1. Right-click the system tray icon
2. Hover over **"❓ Help"**
3. Select:
   - **"🌐 User Guide"** - Opens the comprehensive help page (online with offline fallback)
   - **"📖 Online Documentation"** - Opens the GitHub Pages documentation
   - **"🔄 Check for Updates"** - Manually check for application updates
   - **"ℹ️ About NotifyMe"** - Shows application information and version
   - **"🐙 GitHub Repository"** - Opens the project repository
   - **"⬆ Releases"** - Opens the releases page for updates

### Quitting the Application

- Right-click the system tray icon
- Click **"❌ Quit"**

## Why These Reminders?

### Eye Blinking

When we focus on screens, we blink less frequently, which can lead to:

- Dry eyes
- Eye strain
- Blurred vision
- Headaches

### Walking Breaks

Prolonged sitting can cause:

- Poor circulation
- Muscle stiffness
- Increased health risks
- Reduced productivity

### Water Hydration

Staying hydrated is essential for:

- Brain function and focus
- Energy levels
- Healthy skin
- Proper digestion
- Overall health

### Pranayama Breathing

Short breathing breaks help:

- Reduce stress and tension
- Improve calm focus and clarity
- Reset shallow breathing patterns from long screen sessions
- Learn more: [NirogYoga Knowledge Base](https://www.nirogyoga.in/knowledge-base)

## Configuration

The app stores your preferences in `config.json`:

```json
{
  "blink_interval_minutes": 20,
  "walking_interval_minutes": 60,
  "water_interval_minutes": 30,
  "pranayama_interval_minutes": 120,
  "sound_enabled": false,
  "blink_sound_enabled": true,
  "walking_sound_enabled": true,
  "water_sound_enabled": true,
  "pranayama_sound_enabled": true,
  "tts_enabled": true,
  "tts_language": "auto",
  "blink_tts_enabled": true,
  "walking_tts_enabled": true,
  "water_tts_enabled": true,
  "pranayama_tts_enabled": true,
  "blink_hidden": false,
  "walking_hidden": false,
  "water_hidden": false,
  "pranayama_hidden": false,
  "last_run": null
}
```

### Configuration Options

- **Reminder Intervals**: Adjust the default intervals for each reminder type
- **Sound Controls**:
  - `sound_enabled`: Global sound toggle for all notifications
  - `[type]_sound_enabled`: Individual sound controls for each reminder type
- **Text-to-Speech Controls** (NEW):
  - `tts_enabled`: Global TTS toggle for all reminders
  - `tts_language`: Preferred language (`"auto"`, `"en"`, or `"hi"`)
  - `[type]_tts_enabled`: Individual TTS controls for each reminder type
- **Visibility Controls**:
  - `[type]_hidden`: Hide specific reminder types from the menu while keeping them active
- **System**: `last_run` tracks the last application run time

### Advanced Configuration

You can manually edit the config file to:

- Set custom intervals beyond the menu options
- Enable/disable sounds globally or per reminder type
- Enable/disable TTS globally or per reminder type
- Choose TTS language preference (auto-detect Hindi/English, English only, or Hindi only)
- Hide reminder types you don't want to see in the menu
- The "Hidden Reminders" menu will appear when any reminders are hidden

## Reminder Messages

The app randomly selects from these friendly messages:

### Blink Reminders

- 👁️ Time to blink! Give your eyes a break.
- 💧 Blink reminder: Keep your eyes hydrated!
- ✨ Don't forget to blink and look away from the screen.
- 🌟 Eye care reminder: Blink 10 times slowly.
- 💙 Your eyes need a break - blink and relax!
- 🌈 Blink break! Look at something 20 feet away for 20 seconds.

### Walking Reminders

- 🚶 Time for a walk! Stretch your legs.
- 🏃 Walking break: Get up and move around!
- 🌿 Take a short walk - your body will thank you.
- 💪 Stand up and walk for a few minutes!
- 🚶‍♂️ Sitting too long? Time for a walking break!
- 🌞 Walk around for 5 minutes - refresh your mind and body!

### Water Reminders

- 💧 Time to hydrate! Drink a glass of water.
- 🚰 Water break: Stay hydrated for better health!
- 💦 Don't forget to drink water - your body needs it!
- 🌊 Hydration reminder: Drink some water now.
- 💙 Keep yourself hydrated - drink water regularly!
- 🥤 Water time! Drink at least 250ml now.

### Pranayama Reminders

- 🧘 Pranayama break: Slow, deep breathing for 2-3 minutes.
- 🌬️ Breathing reminder: Inhale 4, hold 4, exhale 6.
- 🫁 Reset with pranayama: Calm breath, clear mind.
- 🧘‍♀️ Pause and breathe: Gentle pranayama now.
- 🌿 Take a breathing break: Relax your shoulders and breathe.
- 🧘‍♂️ Pranayama time: Smooth, steady breaths.

## Technical Details

**Built with:**

- Python 3.13+
- `pystray` - System tray integration
- `winotify` - Windows toast notifications
- `Pillow` - Icon image processing

## Build & Development Scripts

All build and development scripts are in the `scripts/` folder. Both batch (`.bat`) and PowerShell (`.ps1`) versions are available:

| Task  | PowerShell                | Batch                     |
| ----- | ------------------------- | ------------------------- |
| Setup | `.\scripts\setup.ps1`     | `.\scripts\setup.bat`     |
| Run   | `.\scripts\run.ps1`       | `.\scripts\run.bat`       |
| Build | `.\scripts\build.ps1`     | `.\scripts\build.bat`     |
| Test  | `.\scripts\run_tests.ps1` | `.\scripts\run_tests.bat` |

See [scripts/README.md](scripts/README.md) for detailed documentation on each script.

**Quick reference:**

- **Setup**: `.\scripts\setup.ps1` - Install dependencies with uv
- **Run**: `.\scripts\run.ps1` - Launch the application
- **Build**: `.\scripts\build.ps1` - Create executable (safe two-stage build)
- **Test**: `.\scripts\run_tests.ps1` - Run test suite

## License

This project is free to use and modify for personal use.

## Contributing

Feel free to submit issues or pull requests to improve the application!

### Pre-commit Version Check

This repo includes a pre-commit hook that verifies:

- `APP_VERSION` in `notifyme_app/constants.py` matches the `version` in `pyproject.toml`
- The local version is **not older** than the latest GitHub release

To enable the hook locally:

```bash
python -m pip install pre-commit
pre-commit install
```

If you're offline, you can skip the GitHub check by setting:

```bash
SKIP_GITHUB_VERSION_CHECK=1
```

## Connect

- [X (Twitter)](https://x.com/_AtulKumar2_/)
- [LinkedIn](https://www.linkedin.com/in/atulkumar88/)

## Learn More

- [20-20-20 rule (American Optometric Association)](https://www.aoa.org/healthy-eyes/eye-and-vision-conditions/computer-vision-syndrome)
- [Sitting and sedentary behavior (CDC)](https://www.cdc.gov/physicalactivity/basics/sitting-health/index.htm)
- [Water intake and hydration basics (NHS)](https://www.nhs.uk/live-well/eat-well/water-drinks-nutrition/)
- [Breathing exercises for stress (NHS)](https://www.nhs.uk/mental-health/self-help/guides-tools-and-activities/breathing-exercises-for-stress/)

## Tips for Health

- **20-20-20 Rule**: Every 20 minutes, look at something 20 feet away for 20 seconds
- **Blink consciously**: Try to blink 10-15 times when you get a reminder
- **Adjust screen brightness**: Match your screen brightness to your surroundings
- **Use proper lighting**: Avoid glare and ensure adequate ambient lighting
- **Take regular breaks**: Stand up and move around every hour
- **Stay hydrated**: Drink at least 8 glasses (2 liters) of water throughout the day
- **Set a hydration goal**: Track your water intake to ensure you're drinking enough
- **Pranayama reset**: Take 2-3 minutes of slow breathing every couple of hours

---

## Stay healthy! 👁️🚶💧🧘✨
