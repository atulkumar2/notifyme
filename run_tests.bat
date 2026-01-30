@echo off
REM Run tests for NotifyMe application

echo Running NotifyMe tests...
uv run python -m pytest tests/test_notifyme.py -v

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Tests passed successfully!
) else (
    echo.
    echo Tests failed!
    exit /b 1
)
