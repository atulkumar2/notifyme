<#
.SYNOPSIS
Run script to start the NotifyMe application.

.DESCRIPTION
Starts the NotifyMe application using uv package manager.
Falls back to local uv installation if global uv is not available.

.EXAMPLE
.\scripts\run.ps1
#>

# Change to repo root
$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot

Write-Host "Starting NotifyMe (Modular Version)..."
Write-Host ""

try {
    # Try global uv first
    & uv run notifyme.py
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Trying fallback local uv installation..." -ForegroundColor Yellow
        & "$env:USERPROFILE\.local\bin\uv.exe" run notifyme.py
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to run application"
        }
    }
}
catch {
    Write-Host ""
    Write-Host "ERROR: Failed to run application." -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}
