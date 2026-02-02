<# start.ps1 — helper script to create venv, install deps, and run the Flask server #>
param (
    [switch]$SkipVenv,
    [string]$VenvPath = ".venv"
)

$ErrorActionPreference = 'Stop'

if (-not $SkipVenv) {
    if (-not (Test-Path $VenvPath)) {
        Write-Host "Creating virtual environment at $VenvPath..." -ForegroundColor Cyan
        python -m venv $VenvPath
    } else {
        Write-Host "Virtual environment already exists at $VenvPath" -ForegroundColor Yellow
    }

    $pip = Join-Path $VenvPath "Scripts\pip.exe"
    if (-not (Test-Path $pip)) {
        Write-Host "Cannot find pip in venv. Ensure Python 3.8+ is installed and on PATH." -ForegroundColor Red
        exit 1
    }

    Write-Host "Upgrading pip and installing requirements..." -ForegroundColor Cyan
    & $pip install --upgrade pip
    & $pip install -r requirements.txt
}

$python = if ($SkipVenv) { "python" } else { Join-Path $VenvPath "Scripts\python.exe" }

Write-Host "Starting Flask server (Ctrl+C to stop)..." -ForegroundColor Green
& $python app.py
