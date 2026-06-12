$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $repoRoot

if (-not (Test-Path "UI/pallet_coach_ui/node_modules")) {
  throw "UI dependencies not installed. Run .\init_project.ps1 first."
}

Set-Location "UI/pallet_coach_ui"
npm run dev -- --host 127.0.0.1 --port 5173
