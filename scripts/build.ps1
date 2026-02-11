<#
.SYNOPSIS
Build script for NotifyMe executable using PyInstaller.

.DESCRIPTION
Builds the NotifyMe executable with the following steps:
1. Validates icon.ico exists (creates from icon.png if needed)
2. Builds executable to temporary directory
3. Verifies build success
4. Stops running NotifyMe process
5. Replaces old executable with new one
6. Generates SHA256 hash

The two-stage build (temp -> final) ensures the existing executable is not
touched if the build fails.

.PARAMETER SkipPause
If set, skips the pause at the end of the script.

.EXAMPLE
.\scripts\build.ps1
.\scripts\build.ps1 -SkipPause
#>

param(
    [switch]$SkipPause
)

# Change to repo root
$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot

$ErrorActionPreference = "Stop"

Write-Host "Building NotifyMe executable..."
Write-Host ""

# Define temporary build directory
$TempDist = "dist_tmp"
$FinalDist = "dist"

# Clean up any previous failed temporary build
if (Test-Path $TempDist) {
    Write-Host "Cleaning up previous temporary build..."
    Remove-Item -Path $TempDist -Recurse -Force | Out-Null
}

try {
    # Check if icon.ico exists, if not create it from icon.png
    if (-not (Test-Path "icon.ico")) {
        Write-Host "Creating icon.ico from icon.png..."
        & .\.venv\Scripts\python.exe -c "from PIL import Image; Image.open('icon.png').save('icon.ico', format='ICO')"
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to create icon.ico"
        }
    }

    # Build the executable to temporary location
    Write-Host "Running PyInstaller..."
    & .\.venv\Scripts\python.exe -m PyInstaller --distpath $TempDist NotifyMe.spec
    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller failed"
    }

    # Verify the temporary exe exists before proceeding
    if (-not (Test-Path "$TempDist\NotifyMe.exe")) {
        throw "Build failed: executable not created in temporary location"
    }

    Write-Host ""
    Write-Host "Build successful in temporary location!"
    Write-Host ""

    # Now that build succeeded, kill the running process
    $Process = Get-Process NotifyMe -ErrorAction SilentlyContinue
    if ($Process) {
        Write-Host "Closing running NotifyMe.exe..."
        $Process | Stop-Process -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 1
    }

    # Remove previous build artifact if present (retry a few times in case it is locked)
    if (Test-Path "$FinalDist\NotifyMe.exe") {
        Write-Host "Removing old $FinalDist\NotifyMe.exe..."
        for ($i = 1; $i -le 5; $i++) {
            try {
                Remove-Item -Path "$FinalDist\NotifyMe.exe" -Force -ErrorAction Stop
                break
            }
            catch {
                if ($i -eq 5) {
                    throw "Failed to remove $FinalDist\NotifyMe.exe (file is locked)"
                }
                Start-Sleep -Seconds 1
            }
        }
    }

    # Move temporary exe to final location
    if (-not (Test-Path $FinalDist)) {
        New-Item -ItemType Directory -Path $FinalDist | Out-Null
    }

    Write-Host "Moving executable to final location..."
    Move-Item -Path "$TempDist\NotifyMe.exe" -Destination "$FinalDist\NotifyMe.exe" -Force
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to move executable to $FinalDist folder"
    }

    # Clean up temporary directory
    if (Test-Path $TempDist) {
        Remove-Item -Path $TempDist -Recurse -Force | Out-Null
    }

    Write-Host "Executable created at: $FinalDist\NotifyMe.exe"
    Write-Host ""
    Write-Host "Generating SHA256 hash..."
    & .\.venv\Scripts\python.exe -c "import hashlib; p = r'dist\NotifyMe.exe'; h = hashlib.sha256(open(p, 'rb').read()).hexdigest(); open(r'dist\SHA256SUMS.txt', 'w').write(f'{h}  NotifyMe.exe\n')"
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to generate SHA256 hash"
    }

    Write-Host "SHA256 hash created at: $FinalDist\SHA256SUMS.txt"
    Write-Host ""
    Write-Host "You can now:"
    Write-Host "  1. Run $FinalDist\NotifyMe.exe directly"
    Write-Host "  2. Create a shortcut on your desktop"
    Write-Host "  3. Copy to Startup folder for auto-start: shell:startup"
}
catch {
    Write-Host ""
    Write-Host "Build failed! Error:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host ""

    # Clean up temporary directory on failure
    if (Test-Path $TempDist) {
        Remove-Item -Path $TempDist -Recurse -Force -ErrorAction SilentlyContinue | Out-Null
    }

    if (-not $SkipPause) {
        Read-Host "Press Enter to exit"
    }
    exit 1
}

if (-not $SkipPause) {
    Write-Host ""
    Read-Host "Press Enter to exit"
}
