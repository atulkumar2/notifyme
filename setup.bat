@echo off
REM Eye Blink Reminder - Setup Script (using UV)

echo ========================================
echo Eye Blink Reminder - Setup
echo ========================================
echo.

REM Check if uv is installed
uv --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [1/2] Installing uv package manager...
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    REM Add valid path for this session if needed, though powershell installer usually handles it for future sessions
    set "PATH=%USERPROFILE%\.local\bin;%PATH%"
) else (
    echo [1/2] uv is already installed.
)

echo [2/2] Installing dependencies with uv...
uv sync
if %errorlevel% neq 0 (
    REM If global uv failed, try local path
    "%USERPROFILE%\.local\bin\uv.exe" sync
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install dependencies.
        pause
        exit /b 1
    )
)

echo.
echo ========================================
echo Setup completed successfully!
echo ========================================
echo.
echo To run the application:
echo   Double-click: run.bat
echo.
pause
