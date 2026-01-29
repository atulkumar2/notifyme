# 💧 NotifyMe

A modern Windows desktop application that helps you stay healthy by reminding you to blink your eyes, take walking breaks, and stay hydrated at regular intervals.

![NotifyMe Icon](icon.png)

## ✨ Features

- **Triple Reminders**: Eye blink reminders (default: 20 min), walking reminders (default: 60 min), and water drinking reminders (default: 30 min)
- **Background Operation**: Runs silently in the system tray
- **Windows Toast Notifications**: Native Windows 10/11 notifications
- **Customizable Intervals**:
  - Blink reminders: 10-60 minutes
  - Walking reminders: 30-120 minutes
  - Water reminders: 20-90 minutes
- **Flexible Pause/Resume**: Pause all reminders at once, or pause each reminder type individually
- **Snooze Function**: Delay the next reminder by 5 minutes
- **Randomized Messages**: Variety of friendly reminder messages
- **Persistent Settings**: Your preferences are saved between sessions
- **Rolling Logs**: Log files automatically rotate to prevent disk space issues

## 🚀 Quick Start

### Prerequisites

- Windows 10 or Windows 11
- Python 3.8 or higher

### Installation

1. **Clone or download this repository**

2. **Run setup**:
   Double-click `setup.bat` to install `uv` and all dependencies automatically.

   Or manually with uv:

   ```bash
   uv sync
   ```

3. **Run the application**:
   Double-click `run.bat`

   Or manually:

   ```bash
   uv run notifyme.py
   ```

The application will appear in your system tray (look for the icon in the bottom-right corner of your screen).

### Building a Standalone Executable (Optional)

You can create a portable `.exe` file that doesn't require Python:

1. **Build the executable**:
   Double-click `build.bat`

   Or manually:

   ```bash
   uv run pyinstaller --onefile --windowed --icon=icon.ico --name=NotifyMe --add-data "icon.png;." --add-data "icon.ico;." notifyme.py
   ```

2. **Find your executable** at `dist/NotifyMe.exe`

3. **Optional: Auto-start with Windows**:
   - Press `Win + R`, type `shell:startup`, press Enter
   - Copy `NotifyMe.exe` or create a shortcut there

## 📖 How to Use

### Starting Reminders

1. Right-click the icon in the system tray
2. Click **"Start"** to begin receiving reminders
3. You'll receive blink reminders every 20 minutes, walking reminders every 60 minutes, and water reminders every 30 minutes (defaults)

### Customizing the Intervals

1. Right-click the system tray icon
2. Hover over **"Blink Reminder"**, **"Walking Reminder"**, or **"Water Reminder"**
3. Choose your preferred interval:
   - Blink: 10, 15, 20, 30, 45, or 60 minutes
   - Walking: 30, 45, 60, 90, or 120 minutes
   - Water: 20, 30, 45, 60, or 90 minutes

### Testing Notifications

1. Right-click the system tray icon
2. Hover over **"Test Notifications"**
3. Click **"Test Blink"**, **"Test Walking"**, or **"Test Water"** to preview notifications

### Pausing and Resuming

**Pause/Resume All:**

- Click **"Pause All"** to temporarily stop all reminders
- Click **"Resume All"** to continue receiving all reminders

**Pause/Resume Individual Reminders:**

1. Hover over **"Blink Reminder"**, **"Walking Reminder"**, or **"Water Reminder"**
2. Click **"Pause/Resume"** to toggle that specific reminder
3. A checkmark (✓) indicates the reminder is currently paused
4. The system tray icon shows ⏸ next to paused reminders

### Snoozing a Reminder

- Click **"Snooze (5 min)"** to delay the next reminder by 5 minutes

### Quitting the Application

- Right-click the system tray icon
- Click **"Quit"**

## 🎯 Why These Reminders?

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

## 🔧 Configuration

The app stores your preferences in `config.json`:

```json
{
  "interval_minutes": 20,
  "walking_interval_minutes": 60,
  "water_interval_minutes": 30,
  "sound_enabled": false,
  "auto_start": false,
  "last_run": null
}
```

You can manually edit this file to:

- Set `auto_start` to `true` to automatically start reminders when the app launches
- Adjust the default `interval_minutes` for blink reminders
- Adjust the default `walking_interval_minutes` for walking reminders
- Adjust the default `water_interval_minutes` for water reminders

## 📋 Reminder Messages

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

## 🛠️ Technical Details

**Built with:**

- Python 3.13+
- `pystray` - System tray integration
- `winotify` - Windows toast notifications
- `Pillow` - Icon image processing

## 📝 License

This project is free to use and modify for personal use.

## 🤝 Contributing

Feel free to submit issues or pull requests to improve the application!

## 💡 Tips for Health

- **20-20-20 Rule**: Every 20 minutes, look at something 20 feet away for 20 seconds
- **Blink consciously**: Try to blink 10-15 times when you get a reminder
- **Adjust screen brightness**: Match your screen brightness to your surroundings
- **Use proper lighting**: Avoid glare and ensure adequate ambient lighting
- **Take regular breaks**: Stand up and move around every hour
- **Stay hydrated**: Drink at least 8 glasses (2 liters) of water throughout the day
- **Set a hydration goal**: Track your water intake to ensure you're drinking enough

---

## Stay healthy! 👁️🚶💧✨
