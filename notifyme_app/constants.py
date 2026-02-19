"""
Constants and configuration values for the NotifyMe application.

This module contains all the constant values used throughout the application,
including reminder types, default intervals, messages, and URLs.
"""

# Application naming
APP_NAME = "NotifyMe"
APP_REMINDER_APP_ID = f"{APP_NAME} Reminder"


class ConfigKeys:
    """String keys for persisted configuration."""

    BLINK_INTERVAL_MINUTES = "blink_interval_minutes"
    WALKING_INTERVAL_MINUTES = "walking_interval_minutes"
    WATER_INTERVAL_MINUTES = "water_interval_minutes"
    PRANAYAMA_INTERVAL_MINUTES = "pranayama_interval_minutes"
    SOUND_ENABLED = "sound_enabled"
    BLINK_SOUND_ENABLED = "blink_sound_enabled"
    WALKING_SOUND_ENABLED = "walking_sound_enabled"
    WATER_SOUND_ENABLED = "water_sound_enabled"
    PRANAYAMA_SOUND_ENABLED = "pranayama_sound_enabled"
    TTS_ENABLED = "tts_enabled"
    BLINK_TTS_ENABLED = "blink_tts_enabled"
    WALKING_TTS_ENABLED = "walking_tts_enabled"
    WATER_TTS_ENABLED = "water_tts_enabled"
    PRANAYAMA_TTS_ENABLED = "pranayama_tts_enabled"
    TTS_LANGUAGE = "tts_language"
    BLINK_HIDDEN = "blink_hidden"
    WALKING_HIDDEN = "walking_hidden"
    WATER_HIDDEN = "water_hidden"
    PRANAYAMA_HIDDEN = "pranayama_hidden"
    LAST_RUN = "last_run"


class ReminderConfigKeys:
    """String keys for reminder configuration dictionaries."""

    ID = "id"
    ICON = "icon"
    DISPLAY_TITLE = "display_title"
    NOTIFICATION_TITLE = "notification_title"
    DEFAULT_INTERVAL = "default_interval"
    DEFAULT_OFFSET = "default_offset"
    INTERVAL_OPTIONS = "interval_options"
    MESSAGES = "messages"


class MenuCallbacks:
    """String keys for menu callback mapping."""

    CHECK_FOR_UPDATES_ASYNC = "check_for_updates_async"
    OPEN_CONFIG_LOCATION = "open_config_location"
    OPEN_EXE_LOCATION = "open_exe_location"
    OPEN_GITHUB = "open_github"
    OPEN_GITHUB_PAGES = "open_github_pages"
    OPEN_GITHUB_RELEASES = "open_github_releases"
    OPEN_HELP = "open_help"
    OPEN_LOG_LOCATION = "open_log_location"
    PAUSE_REMINDERS = "pause_reminders"
    QUIT_APP = "quit_app"
    RESUME_REMINDERS = "resume_reminders"
    SET_BLINK_INTERVAL = "set_blink_interval"
    SET_PRANAYAMA_INTERVAL = "set_pranayama_interval"
    SET_WALKING_INTERVAL = "set_walking_interval"
    SET_WATER_INTERVAL = "set_water_interval"
    SHOW_ABOUT = "show_about"
    SNOOZE_REMINDER = "snooze_reminder"
    START_REMINDERS = "start_reminders"
    TEST_BLINK_NOTIFICATION = "test_blink_notification"
    TEST_PRANAYAMA_NOTIFICATION = "test_pranayama_notification"
    TEST_WALKING_NOTIFICATION = "test_walking_notification"
    TEST_WATER_NOTIFICATION = "test_water_notification"
    TOGGLE_BLINK_HIDDEN = "toggle_blink_hidden"
    TOGGLE_BLINK_PAUSE = "toggle_blink_pause"
    TOGGLE_BLINK_SOUND = "toggle_blink_sound"
    TOGGLE_BLINK_TTS = "toggle_blink_tts"
    TOGGLE_PRANAYAMA_HIDDEN = "toggle_pranayama_hidden"
    TOGGLE_PRANAYAMA_PAUSE = "toggle_pranayama_pause"
    TOGGLE_PRANAYAMA_SOUND = "toggle_pranayama_sound"
    TOGGLE_PRANAYAMA_TTS = "toggle_pranayama_tts"
    TOGGLE_SOUND = "toggle_sound"
    TOGGLE_TTS = "toggle_tts"
    TOGGLE_WALKING_HIDDEN = "toggle_walking_hidden"
    TOGGLE_WALKING_PAUSE = "toggle_walking_pause"
    TOGGLE_WALKING_SOUND = "toggle_walking_sound"
    TOGGLE_WALKING_TTS = "toggle_walking_tts"
    TOGGLE_WATER_HIDDEN = "toggle_water_hidden"
    TOGGLE_WATER_PAUSE = "toggle_water_pause"
    TOGGLE_WATER_SOUND = "toggle_water_sound"
    TOGGLE_WATER_TTS = "toggle_water_tts"


# Reminder types
REMINDER_BLINK = "blink"
REMINDER_WALKING = "walking"
REMINDER_WATER = "water"
REMINDER_PRANAYAMA = "pranayama"

# All available reminder types (for iteration)
ALL_REMINDER_TYPES = [
    REMINDER_BLINK,
    REMINDER_WALKING,
    REMINDER_WATER,
    REMINDER_PRANAYAMA,
]

# Default intervals (minutes)
DEFAULT_INTERVALS_MIN = {
    REMINDER_BLINK: 20,
    REMINDER_WALKING: 60,
    REMINDER_WATER: 30,
    REMINDER_PRANAYAMA: 120,
}

# Initial stagger offsets (seconds) to avoid simultaneous notifications
DEFAULT_OFFSETS_SECONDS = {
    REMINDER_BLINK: 30,
    REMINDER_WATER: 10,
    REMINDER_WALKING: 50,
    REMINDER_PRANAYAMA: 20,
}


# Reminder titles
REMINDER_TITLES = {
    REMINDER_BLINK: "Eye Blink Reminder",
    REMINDER_WALKING: "Walking Reminder",
    REMINDER_WATER: "Water Reminder",
    REMINDER_PRANAYAMA: "Pranayama Reminder",
}


# Versioning and update checks
APP_VERSION = "2.2.0"
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

# Interval options for menu (in minutes)
INTERVAL_OPTIONS = {
    REMINDER_BLINK: [10, 15, 20, 30, 45, 60],
    REMINDER_WALKING: [30, 45, 60, 90, 120],
    REMINDER_WATER: [20, 30, 45, 60, 90],
    REMINDER_PRANAYAMA: [60, 90, 120, 180, 240],
}

# Reminder messages (randomized for variety)
REMINDER_MESSAGES = {
    REMINDER_BLINK: [
        "👁️ Time to blink! Give your eyes a break.",
        "💧 Blink reminder: Keep your eyes hydrated!",
        "✨ Don't forget to blink and look away from the screen.",
        "🌟 Eye care reminder: Blink 10 times slowly.",
        "💙 Your eyes need a break - blink and relax!",
        "🌈 Blink break! Look at something 20 feet away for 20 seconds.",
    ],
    REMINDER_WALKING: [
        "🚶 Time for a walk! Stretch your legs.",
        "🏃 Walking break: Get up and move around!",
        "🌿 Take a short walk - your body will thank you.",
        "💪 Stand up and walk for a few minutes!",
        "🚶‍♂️ Sitting too long? Time for a walking break!",
        "🌞 Walk around for 5 minutes - refresh your mind and body!",
    ],
    REMINDER_WATER: [
        "💧 Time to hydrate! Drink a glass of water.",
        "🚰 Water break: Stay hydrated for better health!",
        "💦 Don't forget to drink water - your body needs it!",
        "🌊 Hydration reminder: Drink some water now.",
        "💙 Keep yourself hydrated - drink water regularly!",
        "🥤 Water time! Drink at least 250ml now.",
    ],
    REMINDER_PRANAYAMA: [
        "🧘 Pranayama break: Slow, deep breathing for 2-3 minutes.",
        "🌬️ Breathing reminder: Inhale 4, hold 4, exhale 6.",
        "🫁 Reset with pranayama: Calm breath, clear mind.",
        "🧘‍♀️ Pause and breathe: Gentle pranayama now.",
        "🌿 Take a breathing break: Relax your shoulders and breathe.",
        "🧘‍♂️ Pranayama time: Smooth, steady breaths.",
    ],
}

# Comprehensive reminder configuration (single source of truth)
REMINDER_CONFIGS = {
    REMINDER_BLINK: {
        ReminderConfigKeys.ID: REMINDER_BLINK,
        ReminderConfigKeys.ICON: "👁",
        ReminderConfigKeys.DISPLAY_TITLE: f"👁 {REMINDER_TITLES[REMINDER_BLINK]}",
        ReminderConfigKeys.NOTIFICATION_TITLE: REMINDER_TITLES[REMINDER_BLINK],
        ReminderConfigKeys.DEFAULT_INTERVAL: DEFAULT_INTERVALS_MIN[REMINDER_BLINK],
        ReminderConfigKeys.DEFAULT_OFFSET: DEFAULT_OFFSETS_SECONDS[REMINDER_BLINK],
        ReminderConfigKeys.INTERVAL_OPTIONS: INTERVAL_OPTIONS[REMINDER_BLINK],
        ReminderConfigKeys.MESSAGES: REMINDER_MESSAGES[REMINDER_BLINK],
    },
    REMINDER_WALKING: {
        ReminderConfigKeys.ID: REMINDER_WALKING,
        ReminderConfigKeys.ICON: "🚶",
        ReminderConfigKeys.DISPLAY_TITLE: f"🚶 {REMINDER_TITLES[REMINDER_WALKING]}",
        ReminderConfigKeys.NOTIFICATION_TITLE: REMINDER_TITLES[REMINDER_WALKING],
        ReminderConfigKeys.DEFAULT_INTERVAL: DEFAULT_INTERVALS_MIN[REMINDER_WALKING],
        ReminderConfigKeys.DEFAULT_OFFSET: DEFAULT_OFFSETS_SECONDS[REMINDER_WALKING],
        ReminderConfigKeys.INTERVAL_OPTIONS: INTERVAL_OPTIONS[REMINDER_WALKING],
        ReminderConfigKeys.MESSAGES: REMINDER_MESSAGES[REMINDER_WALKING],
    },
    REMINDER_WATER: {
        ReminderConfigKeys.ID: REMINDER_WATER,
        ReminderConfigKeys.ICON: "💧",
        ReminderConfigKeys.DISPLAY_TITLE: f"💧 {REMINDER_TITLES[REMINDER_WATER]}",
        ReminderConfigKeys.NOTIFICATION_TITLE: REMINDER_TITLES[REMINDER_WATER],
        ReminderConfigKeys.DEFAULT_INTERVAL: DEFAULT_INTERVALS_MIN[REMINDER_WATER],
        ReminderConfigKeys.DEFAULT_OFFSET: DEFAULT_OFFSETS_SECONDS[REMINDER_WATER],
        ReminderConfigKeys.INTERVAL_OPTIONS: INTERVAL_OPTIONS[REMINDER_WATER],
        ReminderConfigKeys.MESSAGES: REMINDER_MESSAGES[REMINDER_WATER],
    },
    REMINDER_PRANAYAMA: {
        ReminderConfigKeys.ID: REMINDER_PRANAYAMA,
        ReminderConfigKeys.ICON: "🧘",
        ReminderConfigKeys.DISPLAY_TITLE: f"🧘 {REMINDER_TITLES[REMINDER_PRANAYAMA]}",
        ReminderConfigKeys.NOTIFICATION_TITLE: REMINDER_TITLES[REMINDER_PRANAYAMA],
        ReminderConfigKeys.DEFAULT_INTERVAL: DEFAULT_INTERVALS_MIN[REMINDER_PRANAYAMA],
        ReminderConfigKeys.DEFAULT_OFFSET: DEFAULT_OFFSETS_SECONDS[REMINDER_PRANAYAMA],
        ReminderConfigKeys.INTERVAL_OPTIONS: INTERVAL_OPTIONS[REMINDER_PRANAYAMA],
        ReminderConfigKeys.MESSAGES: REMINDER_MESSAGES[REMINDER_PRANAYAMA],
    },
}
