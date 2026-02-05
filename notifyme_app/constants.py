"""
Constants and configuration values for the NotifyMe application.

This module contains all the constant values used throughout the application,
including reminder types, default intervals, messages, and URLs.
"""

# Reminder types
REMINDER_BLINK = "blink"
REMINDER_WALKING = "walking"
REMINDER_WATER = "water"
REMINDER_PRANAYAMA = "pranayama"

# Default intervals (minutes)
DEFAULT_BLINK_INTERVAL_MIN = 20
DEFAULT_WALKING_INTERVAL_MIN = 60
DEFAULT_WATER_INTERVAL_MIN = 30
DEFAULT_PRANAYAMA_INTERVAL_MIN = 120

# Reminder titles
TITLE_BLINK = "Eye Blink Reminder"
TITLE_WALKING = "Walking Reminder"
TITLE_WATER = "Water Reminder"
TITLE_PRANAYAMA = "Pranayama Reminder"

# Initial stagger offsets (seconds) to avoid simultaneous notifications
DEFAULT_OFFSETS_SECONDS = {
    REMINDER_BLINK: 30,
    REMINDER_WATER: 10,
    REMINDER_WALKING: 50,
    REMINDER_PRANAYAMA: 20,
}

# Versioning and update checks
APP_VERSION = "2.1.0"
GITHUB_REPO_URL = "https://github.com/atulkumar2/notifyme"
GITHUB_RELEASES_URL = f"{GITHUB_REPO_URL}/releases/latest"
GITHUB_RELEASES_API_URL = (
    "https://api.github.com/repos/atulkumar2/notifyme/releases/latest"
)
GITHUB_PAGES_URL = "https://atulkumar2.github.io/notifyme/"
GITHUB_PAGES_USAGE_URL = "https://atulkumar2.github.io/notifyme/usage.html"

UPDATE_CHECK_TIMEOUT_SECONDS = 5

# Error HTML template for help fallback
HELP_ERROR_HTML = """
<html>
<head><title>Help Not Available</title></head>
<body style="font-family: Arial, sans-serif; margin: 40px; color: #666;">
    <h1>❌ Help Not Available</h1>
    <p>Could not open offline help or GitHub Pages.</p>
    <p>Please visit: <a href="{url}">{url}</a></p>
    <p>Or check the offline help at: help/index.html</p>
</body>
</html>
"""

# Reminder messages (randomized for variety)
BLINK_MESSAGES = [
    "👁️ Time to blink! Give your eyes a break.",
    "💧 Blink reminder: Keep your eyes hydrated!",
    "✨ Don't forget to blink and look away from the screen.",
    "🌟 Eye care reminder: Blink 10 times slowly.",
    "💙 Your eyes need a break - blink and relax!",
    "🌈 Blink break! Look at something 20 feet away for 20 seconds.",
]

WALKING_MESSAGES = [
    "🚶 Time for a walk! Stretch your legs.",
    "🏃 Walking break: Get up and move around!",
    "🌿 Take a short walk - your body will thank you.",
    "💪 Stand up and walk for a few minutes!",
    "🚶‍♂️ Sitting too long? Time for a walking break!",
    "🌞 Walk around for 5 minutes - refresh your mind and body!",
]

WATER_MESSAGES = [
    "💧 Time to hydrate! Drink a glass of water.",
    "🚰 Water break: Stay hydrated for better health!",
    "💦 Don't forget to drink water - your body needs it!",
    "🌊 Hydration reminder: Drink some water now.",
    "💙 Keep yourself hydrated - drink water regularly!",
    "🥤 Water time! Drink at least 250ml now.",
]

PRANAYAMA_MESSAGES = [
    "🧘 Pranayama break: Slow, deep breathing for 2-3 minutes.",
    "🌬️ Breathing reminder: Inhale 4, hold 4, exhale 6.",
    "🫁 Reset with pranayama: Calm breath, clear mind.",
    "🧘‍♀️ Pause and breathe: Gentle pranayama now.",
    "🌿 Take a breathing break: Relax your shoulders and breathe.",
    "🧘‍♂️ Pranayama time: Smooth, steady breaths.",
]
