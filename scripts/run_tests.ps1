<#
.SYNOPSIS
Run tests for the NotifyMe application.

.DESCRIPTION
Runs pytest tests for the NotifyMe application using uv.

.EXAMPLE
.\scripts\run_tests.ps1
#>

# Change to repo root
$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot

Write-Host "Running NotifyMe tests..."
Write-Host ""

try {
    & uv run python -m pytest tests/test_notifyme.py -v

    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "Tests passed successfully!" -ForegroundColor Green
        exit 0
    }
    else {
        Write-Host ""
        Write-Host "Tests failed!" -ForegroundColor Red
        exit 1
    }
}
catch {
    Write-Host ""
    Write-Host "ERROR: Failed to run tests." -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}
