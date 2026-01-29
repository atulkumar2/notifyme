@echo off
REM NotifyMe - Run Script

echo Starting NotifyMe...

REM Run the app using uv
uv run notifyme.py
if %errorlevel% neq 0 (
    REM Fallback to local path if simple command fails
    "%USERPROFILE%\.local\bin\uv.exe" run notifyme.py
    if %errorlevel% neq 0 (
        echo ERROR: Failed to run application.
        pause
    )
)
