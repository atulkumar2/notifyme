# � NotifyMe

A modern Windows desktop application that helps you stay healthy by reminding you to blink your eyes and take walking breaks at regular intervals.

![NotifyMe Icon](icon.png)

## ✨ Features

- **Dual Reminders**: Eye blink reminders (default: 20 min) and walking reminders (default: 60 min)
- **Background Operation**: Runs silently in the system tray
- **Windows Toast Notifications**: Native Windows 10/11 notifications
- **Customizable Intervals**: Set blink reminders from 10-60 minutes, walking reminders from 30-120 minutes
- **Pause/Resume**: Full control over when reminders appear
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
   uv run blink_reminder.py
   ```

The application will appear in your system tray (look for the icon in the bottom-right corner of your screen).

## 📖 How to Use

### Starting Reminders

1. Right-click the icon in the system tray
2. Click **"Start"** to begin receiving reminders
3. You'll receive blink reminders every 20 minutes and walking reminders every 60 minutes (defaults)

### Customizing the Intervals

1. Right-click the system tray icon
2. Hover over **"Blink Interval"** or **"Walking Interval"**
3. Choose your preferred interval:
   - Blink: 10, 15, 20, 30, 45, or 60 minutes
   - Walking: 30, 45, 60, 90, or 120 minutes

### Testing Notifications

1. Right-click the system tray icon
2. Hover over **"Test Notifications"**
3. Click **"Test Blink"** or **"Test Walking"** to preview notifications

### Pausing and Resuming

- Click **"Pause"** to temporarily stop reminders
- Click **"Resume"** to continue receiving reminders

### Snoozing a Reminder

- Click **"Snooze (5 min)"** to delay the next reminder by 5 minutes

### Quitting the Application

- Right-click the system tray icon
- Click **"Quit"**

## 🎯 Why Blink?

When we focus on screens, we blink less frequently, which can lead to:

- Dry eyes
- Eye strain
- Blurred vision
- Headaches

This app helps you maintain healthy blinking habits by providing gentle, regular reminders.

## 🔧 Configuration

The app stores your preferences in `config.json`:

```json
{
  "interval_minutes": 20,
  "walking_interval_minutes": 60,
  "sound_enabled": false,
  "auto_start": false,
  "last_run": null
}
```

You can manually edit this file to:

- Set `auto_start` to `true` to automatically start reminders when the app launches
- Adjust the default `interval_minutes` for blink reminders
- Adjust the default `walking_interval_minutes` for walking reminders

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
- **Stay hydrated**: Drink water throughout the day

---

**Stay healthy! 👁️🚶✨**
