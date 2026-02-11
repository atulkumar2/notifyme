<#
.SYNOPSIS
Setup script for NotifyMe project dependencies using uv package manager.

.DESCRIPTION
Sets up the NotifyMe project by:
1. Installing uv package manager (if not already installed)
2. Installing project dependencies using uv sync

.EXAMPLE
.\scripts\setup.ps1
#>

$ErrorActionPreference = "Stop"

# Change to repo root
$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot

Write-Host "========================================"
Write-Host "NotifyMe - Setup"
Write-Host "========================================"
Write-Host ""

try {
    # Check if uv is installed
    $UvInstalled = $false
    try {
        $output = & uv --version 2>&1
        $UvInstalled = $true
        Write-Host "[1/2] uv is already installed."
    }
    catch {
        Write-Host "[1/2] Installing uv package manager..."

        # Run the uv installer
        $InstallScript = @"
#Requires -Version 5.0
`$UvUrl = 'https://astral.sh/uv/install.ps1'
`$TempFile = Join-Path ([System.IO.Path]::GetTempPath()) 'uv_install.ps1'
try {
    Invoke-WebRequest -Uri `$UvUrl -OutFile `$TempFile -UseBasicParsing
    & `$TempFile
} finally {
    Remove-Item `$TempFile -Force -ErrorAction SilentlyContinue
}
"@

        & powershell -ExecutionPolicy ByPass -Command $InstallScript

        if ($LASTEXITCODE -ne 0) {
            throw "Failed to install uv"
        }

        # Update PATH for this session
        $env:PATH = "$env:USERPROFILE\.local\bin;$env:PATH"
        $UvInstalled = $true
    }

    if ($UvInstalled) {
        Write-Host "[2/2] Installing dependencies with uv..."

        # Try global uv first
        $Success = $false
        try {
            & uv sync
            if ($LASTEXITCODE -eq 0) {
                $Success = $true
            }
        }
        catch {
            # Try local uv
            Write-Host "Trying fallback local uv installation..." -ForegroundColor Yellow
            & "$env:USERPROFILE\.local\bin\uv.exe" sync
            if ($LASTEXITCODE -eq 0) {
                $Success = $true
            }
        }

        if (-not $Success) {
            throw "Failed to install dependencies"
        }
    }

    Write-Host ""
    Write-Host "========================================"
    Write-Host "Setup completed successfully!"
    Write-Host "========================================"
    Write-Host ""
    Write-Host "To run the application:"
    Write-Host "  Double-click: scripts/run.ps1"
    Write-Host "  Or run: .\scripts\run.ps1"
    Write-Host ""
    Read-Host "Press Enter to exit"
}
catch {
    Write-Host ""
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}
