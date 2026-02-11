@echo off
setlocal enabledelayedexpansion

REM Change to repo root
cd /d "%~dp0\.."

echo Building NotifyMe executable...
REM echo .

REM Define temporary build directory
set "TEMP_DIST=dist_tmp"

REM Clean up any previous failed temporary build
if exist %TEMP_DIST% (
    echo Cleaning up previous temporary build...
    rmdir /s /q %TEMP_DIST% >NUL 2>&1
)

REM Check if icon.ico exists, if not create it from icon.png
if not exist icon.ico (
    echo Creating icon.ico from icon.png...
    uv run python -c "from PIL import Image; Image.open('icon.png').save('icon.ico', format='ICO')"
    if !errorlevel! neq 0 goto :build_failed
)

REM Build the executable to temporary location
echo Running PyInstaller...
.venv\Scripts\python.exe -m PyInstaller --distpath %TEMP_DIST% NotifyMe.spec
if !errorlevel! neq 0 goto :build_failed

REM Verify the temporary exe exists before proceeding
if not exist %TEMP_DIST%\NotifyMe.exe (
    echo Build failed: executable not created in temporary location
    goto :build_failed
)

echo.
echo Build successful in temporary location!
echo .

REM Now that build succeeded, kill the running process
tasklist /fi "imagename eq NotifyMe.exe" 2>NUL | findstr /i /c:"NotifyMe.exe" >NUL
if !errorlevel! == 0 (
    echo Closing running NotifyMe.exe...
    taskkill /f /im NotifyMe.exe >NUL 2>&1
)

REM Remove previous build artifact if present (retry a few times in case it is locked)
if exist dist\NotifyMe.exe (
    echo Removing old dist\NotifyMe.exe...
    for /l %%i in (1,1,5) do (
        del /f /q dist\NotifyMe.exe >NUL 2>&1
        if not exist dist\NotifyMe.exe goto :old_exe_removed
        timeout /t 1 >NUL
    )
    if exist dist\NotifyMe.exe (
        echo Failed to remove dist\NotifyMe.exe (file is locked)
        goto :build_failed
    )
)
:old_exe_removed

REM Move temporary exe to final location
echo Moving executable to final location...
move /y %TEMP_DIST%\NotifyMe.exe dist\NotifyMe.exe >NUL 2>&1
if !errorlevel! neq 0 (
    echo Failed to move executable to dist folder
    goto :build_failed
)

REM Clean up temporary directory
if exist %TEMP_DIST% (
    rmdir /s /q %TEMP_DIST% >NUL 2>&1
)

echo Executable created at: dist\NotifyMe.exe
echo .
echo Generating SHA256 hash...
.venv\Scripts\python.exe -c "import hashlib; p = r'dist\NotifyMe.exe'; h = hashlib.sha256(open(p, 'rb').read()).hexdigest(); open(r'dist\SHA256SUMS.txt', 'w').write(f'{h}  NotifyMe.exe\n')"
if !errorlevel! neq 0 goto :build_failed
echo SHA256 hash created at: dist\SHA256SUMS.txt
echo .
echo You can now:
echo   1. Run dist\NotifyMe.exe directly
echo   2. Create a shortcut on your desktop
echo   3. Copy to Startup folder for auto-start: shell:startup
goto :build_done

:build_failed
echo .
echo Build failed! Check the output above for errors.
exit /b 1

:build_done
echo .
pause
