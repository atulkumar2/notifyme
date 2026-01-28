# 👁️ Eye Blink Reminder

A modern Windows desktop application that helps reduce eye strain by reminding you to blink your eyes at regular intervals.

![Eye Blink Reminder Icon](icon.png)

## ✨ Features

- **Background Operation**: Runs silently in the system tray
- **Windows Toast Notifications**: Native Windows 10/11 notifications
- **Customizable Intervals**: Set reminders from 10 to 60 minutes
- **Pause/Resume**: Full control over when reminders appear
- **Snooze Function**: Delay the next reminder by 5 minutes
- **Randomized Messages**: Variety of friendly reminder messages
- **Persistent Settings**: Your preferences are saved between sessions

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

The application will appear in your system tray (look for the eye icon in the bottom-right corner of your screen).

## 📖 How to Use

### Starting Reminders

1. Right-click the eye icon in the system tray
2. Click **"Start"** to begin receiving reminders
3. You'll receive a notification every 20 minutes (default)

### Customizing the Interval

1. Right-click the system tray icon
2. Hover over **"Set Interval"**
3. Choose your preferred interval (10, 15, 20, 30, 45, or 60 minutes)

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
    "sound_enabled": false,
    "auto_start": false,
    "last_run": null
}
```

You can manually edit this file to:

- Set `auto_start` to `true` to automatically start reminders when the app launches
- Adjust the default `interval_minutes`

## 📋 Reminder Messages

The app randomly selects from these friendly messages:

- 👁️ Time to blink! Give your eyes a break.
- 💧 Blink reminder: Keep your eyes hydrated!
- ✨ Don't forget to blink and look away from the screen.
- 🌟 Eye care reminder: Blink 10 times slowly.
- 💙 Your eyes need a break - blink and relax!
- 🌈 Blink break! Look at something 20 feet away for 20 seconds.

## 🛠️ Technical Details

**Built with:**

- Python 3
- `pystray` - System tray integration
- `win10toast` - Windows toast notifications
- `Pillow` - Icon image processing

## 📝 License

This project is free to use and modify for personal use.

## 🤝 Contributing

Feel free to submit issues or pull requests to improve the application!

## 💡 Tips for Eye Health

- **20-20-20 Rule**: Every 20 minutes, look at something 20 feet away for 20 seconds
- **Blink consciously**: Try to blink 10-15 times when you get a reminder
- **Adjust screen brightness**: Match your screen brightness to your surroundings
- **Use proper lighting**: Avoid glare and ensure adequate ambient lighting
- **Take regular breaks**: Stand up and move around every hour

---

**Stay healthy, keep blinking! 👁️✨**
