# MeetFlow AI — one-click launcher: starts backend + frontend and opens the site
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$py = Join-Path $root ".venv\Scripts\python.exe"
if (-not (Test-Path $py)) { $py = "python" }
$appDir = Join-Path $root "meetflow_ai"

if (-not (Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue)) {
    Start-Process -FilePath $py -ArgumentList "-m","uvicorn","backend.main:app","--host","127.0.0.1","--port","8000" -WorkingDirectory $appDir -WindowStyle Minimized
    Write-Host "Backend starting on http://127.0.0.1:8000 ..."
} else { Write-Host "Backend already running." }

if (-not (Get-NetTCPConnection -LocalPort 5500 -State Listen -ErrorAction SilentlyContinue)) {
    Start-Process -FilePath $py -ArgumentList "-m","http.server","5500","--bind","127.0.0.1","--directory","frontend" -WorkingDirectory $appDir -WindowStyle Minimized
    Write-Host "Frontend starting on http://127.0.0.1:5500 ..."
} else { Write-Host "Frontend already running." }

Start-Sleep -Seconds 3
Start-Process "http://127.0.0.1:5500"
Write-Host "Site opened in your browser. You can close this window."
