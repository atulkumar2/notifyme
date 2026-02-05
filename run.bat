@echo off
REM NotifyMe - Run Script

echo Starting NotifyMe (Modular Version)...

REM Run the new modular app using uv
uv run notifyme.py
if %errorlevel% neq 0 (
    REM Fallback to local path if simple command fails
    "%USERPROFILE%\.local\bin\uv.exe" run notifyme.py
    if %errorlevel% neq 0 (
        echo ERROR: Failed to run application.
        pause
    )
)
