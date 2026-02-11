@echo off
REM Backward compatibility wrapper - calls the actual script in scripts folder
powershell -ExecutionPolicy Bypass -File "%~dp0scripts\build.ps1" %*
