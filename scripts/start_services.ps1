# PowerShell script to start both services in separate windows
# Usage: .\scripts\start_services.ps1

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting Glossary Services" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir

# Start REST service in new window
Write-Host "Starting REST service in new window..." -ForegroundColor Yellow
$restScript = Join-Path $scriptDir "start_rest_service.ps1"
Start-Process powershell -ArgumentList "-NoExit", "-File", $restScript

# Wait a bit
Start-Sleep -Seconds 2

# Start gRPC service in new window
Write-Host "Starting gRPC service in new window..." -ForegroundColor Yellow
$grpcScript = Join-Path $scriptDir "start_grpc_service.ps1"
Start-Process powershell -ArgumentList "-NoExit", "-File", $grpcScript

Write-Host ""
Write-Host "Services are starting in separate windows." -ForegroundColor Green
Write-Host "REST service: http://localhost:8000" -ForegroundColor Cyan
Write-Host "gRPC service: localhost:50051" -ForegroundColor Cyan
Write-Host ""
Write-Host "Wait a few seconds for services to start, then run your tests." -ForegroundColor Yellow
Write-Host ""

