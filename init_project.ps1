$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $repoRoot

Write-Host "Initializing project environment..."

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
  throw "Python is not available in PATH. Install Python 3.10+ first."
}

if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
  throw "npm is not available in PATH. Install Node 18+ first."
}

if (-not (Test-Path ".venv")) {
  python -m venv .venv
}

& ".\.venv\Scripts\Activate.ps1"
python -m pip install --upgrade pip
python -m pip install -r scripts/requirements.txt

Push-Location "UI/pallet_coach_ui"
npm install
Pop-Location

Write-Host "Initialization complete."
