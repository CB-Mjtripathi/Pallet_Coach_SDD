$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $repoRoot

if (-not (Test-Path ".venv\Scripts\Activate.ps1")) {
  throw "Missing virtual environment. Run .\init_project.ps1 first."
}

& ".\.venv\Scripts\Activate.ps1"
$env:PYTHONPATH = "scripts"

python -m uvicorn pallet_coach.api.app:app --host 127.0.0.1 --port 8000 --reload
