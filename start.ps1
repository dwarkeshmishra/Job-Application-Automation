# Job Application Copilot — Windows Startup Script
# Run this script from the project root: .\start.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Job Application Copilot - Starting... " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$ProjectRoot = $PSScriptRoot
if (-not $ProjectRoot) { $ProjectRoot = Get-Location }

# 1. Start Backend
Write-Host "[1/2] Starting Backend (FastAPI)..." -ForegroundColor Yellow
$backendDir = Join-Path $ProjectRoot "backend"
$venvPython = Join-Path $backendDir "venv\Scripts\python.exe"

if (Test-Path $venvPython) {
    $backendProcess = Start-Process -FilePath $venvPython -ArgumentList "-m", "uvicorn", "main:app", "--reload", "--port", "8000" -WorkingDirectory $backendDir -PassThru -NoNewWindow
} else {
    Write-Host "  Virtual environment not found. Run: cd backend && python -m venv venv && venv\Scripts\activate && pip install -r requirements.txt" -ForegroundColor Red
    $backendProcess = Start-Process -FilePath "python" -ArgumentList "-m", "uvicorn", "main:app", "--reload", "--port", "8000" -WorkingDirectory $backendDir -PassThru -NoNewWindow
}
Write-Host "  Backend PID: $($backendProcess.Id)" -ForegroundColor Green

Start-Sleep -Seconds 2

# 2. Start Frontend
Write-Host "[2/2] Starting Frontend (Vite)..." -ForegroundColor Yellow
$frontendDir = Join-Path $ProjectRoot "frontend"
$frontendProcess = Start-Process -FilePath "npm" -ArgumentList "run", "dev" -WorkingDirectory $frontendDir -PassThru -NoNewWindow
Write-Host "  Frontend PID: $($frontendProcess.Id)" -ForegroundColor Green

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  All services started!                " -ForegroundColor Green
Write-Host "  Dashboard:  http://localhost:5173     " -ForegroundColor White
Write-Host "  API Docs:   http://localhost:8000/docs" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop all services." -ForegroundColor Gray

# Wait for either process to exit
try {
    while ($true) {
        if ($backendProcess.HasExited -or $frontendProcess.HasExited) {
            Write-Host "A service has stopped." -ForegroundColor Red
            break
        }
        Start-Sleep -Seconds 2
    }
} finally {
    Write-Host "Stopping services..." -ForegroundColor Yellow
    if (-not $backendProcess.HasExited) { Stop-Process -Id $backendProcess.Id -Force -ErrorAction SilentlyContinue }
    if (-not $frontendProcess.HasExited) { Stop-Process -Id $frontendProcess.Id -Force -ErrorAction SilentlyContinue }
    Write-Host "All services stopped." -ForegroundColor Green
}
