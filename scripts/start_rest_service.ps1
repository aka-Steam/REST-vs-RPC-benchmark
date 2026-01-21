# PowerShell script to start REST service
# Usage: .\scripts\start_rest_service.ps1

$ErrorActionPreference = "Stop"

Write-Host "Starting REST service..." -ForegroundColor Cyan
Write-Host ""

# Get project root directory
$projectRoot = Split-Path $PSScriptRoot -Parent

# Check for virtual environment
$venvPath = Join-Path $projectRoot ".venv"
$venvPython = Join-Path $venvPath "Scripts\python.exe"

if (Test-Path $venvPython) {
    $pythonCmd = $venvPython
    Write-Host "Using virtual environment: $venvPath" -ForegroundColor Green
} else {
    $pythonCmd = "python"
    Write-Host "Warning: Virtual environment not found. Using system Python." -ForegroundColor Yellow
    Write-Host "Consider creating venv: python -m venv .venv" -ForegroundColor Yellow
}

# Change to REST service directory
$restServiceDir = Join-Path $projectRoot "glossary_RESTservice"
$restServiceDir = Resolve-Path $restServiceDir

if (-not (Test-Path $restServiceDir)) {
    Write-Host "Error: REST service directory not found: $restServiceDir" -ForegroundColor Red
    exit 1
}

Set-Location $restServiceDir

# Check if uvicorn is available
try {
    $uvicornVersion = & $pythonCmd -m uvicorn --version 2>&1
    Write-Host "Uvicorn: $uvicornVersion" -ForegroundColor Green
} catch {
    Write-Host "Error: uvicorn is not installed. Installing..." -ForegroundColor Yellow
    & $pythonCmd -m pip install uvicorn[standard]
}

Write-Host ""
Write-Host "Starting REST service on http://localhost:8000" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop the service" -ForegroundColor Yellow
Write-Host ""

# Start uvicorn
& $pythonCmd -m uvicorn app.main:app --host 0.0.0.0 --port 8000

