@echo off
REM Eye Blink Reminder - Run Script

echo Starting Eye Blink Reminder...

REM Run the app using uv
uv run blink_reminder.py
if %errorlevel% neq 0 (
    REM Fallback to local path if simple command fails
    "%USERPROFILE%\.local\bin\uv.exe" run blink_reminder.py
    if %errorlevel% neq 0 (
        echo ERROR: Failed to run application.
        pause
    )
)
