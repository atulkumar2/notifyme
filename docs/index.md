# NotifyMe - Stay Healthy, Stay Productive

A modern Windows desktop application that helps you stay healthy by reminding you to **blink your eyes**, **take walking breaks**, **stay hydrated**, and **practice pranayama** at regular intervals.

## Features

### 👁️ Eye Blink Reminders

**Default:** 20 minutes | **Range:** 10-60 minutes
Reduce digital eye strain with regular blink reminders following the science-backed 20-20-20 rule.

### 🚶 Walking Reminders

**Default:** 60 minutes | **Range:** 30-120 minutes
Take movement breaks to improve circulation, strengthen muscles, and boost productivity by up to 30%.

### 💧 Water Reminders

**Default:** 30 minutes | **Range:** 20-90 minutes
Stay hydrated to maintain optimal brain function and energy levels throughout the day.

### 🧘 Pranayama Reminders

**Default:** 120 minutes | **Range:** 60-240 minutes
Take short breathing breaks to reset focus, reduce stress, and improve calm productivity.

### ⚙️ Smart Control

- Individually pause/resume each reminder type
- Persistent settings saved automatically
- Snooze function (delay 5 minutes)
- Test notifications for verification

### 🎯 Lightweight & Reliable

- Runs in system tray (minimal footprint)
- Native Windows toast notifications
- No external dependencies
- Cross-compatible (Windows 10/11)

## Quick Navigation

- [🚀 Installation Guide](installation.md)
- [📖 Usage Guide](usage.md)
- [⚙️ Configuration](configuration.md)
- [🆘 Troubleshooting](troubleshooting.md)

## Why These Reminders Matter

### 👁️ Eye Blink Reminders - Prevent Digital Eye Strain

**The Problem:** Screen work reduces blinking by 66%, causing:

- Reduced tear production → dry, uncomfortable eyes
- Continuous eye muscle focus → fatigue and strain
- Long-term vision degradation and eye health issues

**The Solution:** Regular blinking refreshes eyes with natural tears and prevents strain. Ophthalmologists recommend the **20-20-20 rule**: every 20 minutes, look 20 feet away for 20 seconds.

### 🚶 Walking Reminders - Combat Sedentary Health Risks

**The Problem:** Prolonged sitting causes:

- Restricted blood flow → increased heart disease and clot risks
- Muscle weakness and metabolic slowdown
- Postural problems → back and neck pain
- Mental health impact: reduced mood and increased stress

**The Solution:** Even 5-minute movement breaks:

- Improve blood circulation and strengthen muscles
- Enhance posture and reduce pain
- Boost mood, energy, and mental clarity
- Can reduce health risks by up to **30%**

### 💧 Hydration Reminders - Maintain Cognitive Function

**The Problem:** Even 2% dehydration impairs:

- Brain concentration and memory (brain is 75% water)
- Physical performance and energy levels
- Causes workplace headaches and fatigue
- Affects kidney function and digestion

**The Solution:** Regular water intake:

- Maintains optimal brain function and focus
- Improves energy and prevents headaches
- Supports overall health and wellbeing
- Recommended: 8-10 glasses daily

### 🧘 Pranayama Reminders - Restore Calm Focus

**The Problem:** Long stretches of focused work can lead to shallow breathing and stress buildup, reducing clarity.

**The Solution:** Short pranayama breaks:

- Promote calm focus and reduce tension
- Improve breath depth and oxygen intake
- Offer a mental reset every couple of hours
- Learn more: [NirogYoga Knowledge Base](https://www.nirogyoga.in/knowledge-base)

## Getting Started

1. [Download and install NotifyMe](installation.md)
2. Launch the application
3. [Configure your reminder intervals](configuration.md)
4. Start receiving healthy reminders!

## Need Help?

- Check [troubleshooting tips](troubleshooting.md)
- Review [configuration options](configuration.md)
- Open the help page from the tray menu

## Pre-commit Version Check

This repo includes a pre-commit hook that verifies:

- `APP_VERSION` in `notifyme_app/constants.py` matches the `version` in `pyproject.toml`
- The local version is **not older** than the latest GitHub release

To enable the hook locally:

```
python -m pip install pre-commit
pre-commit install
```

If you're offline, you can skip the GitHub check by setting:

```
SKIP_GITHUB_VERSION_CHECK=1
```

## 🔗 Connect

- [X (Twitter)](https://x.com/_AtulKumar2_)
- [LinkedIn](https://www.linkedin.com/in/atulkumar88/)

## 📚 Learn More

- [20-20-20 rule (American Optometric Association)](https://www.aoa.org/healthy-eyes/eye-and-vision-conditions/computer-vision-syndrome)
- [Sitting and sedentary behavior (CDC)](https://www.cdc.gov/physicalactivity/basics/sitting-health/index.htm)
- [Water intake and hydration basics (NHS)](https://www.nhs.uk/live-well/eat-well/water-drinks-nutrition/)
- [Breathing and stress basics (NHS)](https://www.nhs.uk/mental-health/self-help/guides-tools-and-activities/breathing-exercises-for-stress/)

---

Footer: Made with ❤️ to help you stay healthy and productive
