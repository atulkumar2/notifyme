@echo off
echo Building NotifyMe executable...
echo.

REM Check if icon.ico exists, if not create it from icon.png
if not exist icon.ico (
    echo Creating icon.ico from icon.png...
    uv run python -c "from PIL import Image; Image.open('icon.png').save('icon.ico', format='ICO')"
)

REM Build the executable
echo Running PyInstaller...
uv run pyinstaller --onefile --windowed --icon=icon.ico --name=NotifyMe --add-data "icon.png;." --add-data "icon.ico;." --add-data "help;help" notifyme.py

echo.
if exist dist\NotifyMe.exe (
    echo Build successful!
    echo.
    echo Executable created at: dist\NotifyMe.exe
    echo.
    echo You can now:
    echo   1. Run dist\NotifyMe.exe directly
    echo   2. Create a shortcut on your desktop
    echo   3. Copy to Startup folder for auto-start: shell:startup
) else (
    echo Build failed! Check the output above for errors.
)
echo.
pause
