$ErrorActionPreference = "Stop"
$Project = "$HOME\Documents\xauusd_ai_analyst"
Set-Location $Project

if (!(Test-Path ".\.venv\Scripts\python.exe")) {
    python -m venv .venv
}

Set-ExecutionPolicy -Scope Process Bypass -Force
$env:PYTHONPATH = $Project
$env:PYTHONUNBUFFERED = "1"

& "$Project\.venv\Scripts\python.exe" -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) { throw "Dependency installation failed." }

Write-Host "Starting XAUUSD API and continuous analysis..." -ForegroundColor Cyan
Write-Host "API: http://localhost:8000" -ForegroundColor Yellow
Write-Host "API docs: http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop." -ForegroundColor Gray

& "$Project\.venv\Scripts\python.exe" -m uvicorn app.api:app --host 0.0.0.0 --port 8000
