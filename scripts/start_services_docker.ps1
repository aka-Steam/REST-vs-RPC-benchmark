# PowerShell script to start services using Docker
# Usage: .\scripts\start_services_docker.ps1

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting Services with Docker" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is available
try {
    $dockerVersion = docker --version
    Write-Host "Docker: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "Error: Docker is not installed or not running." -ForegroundColor Red
    Write-Host "Please install Docker Desktop and ensure it's running." -ForegroundColor Yellow
    exit 1
}

# Check if docker-compose is available
try {
    $composeVersion = docker compose version
    Write-Host "Docker Compose: $composeVersion" -ForegroundColor Green
} catch {
    Write-Host "Warning: docker compose not found, trying docker-compose..." -ForegroundColor Yellow
    try {
        $composeVersion = docker-compose --version
        Write-Host "Docker Compose: $composeVersion" -ForegroundColor Green
        $composeCmd = "docker-compose"
    } catch {
        Write-Host "Error: Docker Compose is not available." -ForegroundColor Red
        exit 1
    }
} else {
    $composeCmd = "docker compose"
}

Write-Host ""

# Get project root
$projectRoot = Split-Path $PSScriptRoot -Parent
Set-Location $projectRoot

# Build and start services
Write-Host "Building and starting services..." -ForegroundColor Yellow
Write-Host ""

& $composeCmd up -d --build

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "Services started successfully!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "REST service: http://localhost:8000" -ForegroundColor Cyan
    Write-Host "gRPC service: localhost:50051" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "To view logs:" -ForegroundColor Yellow
    Write-Host "  docker compose logs -f" -ForegroundColor White
    Write-Host ""
    Write-Host "To stop services:" -ForegroundColor Yellow
    Write-Host "  docker compose down" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "Error: Failed to start services" -ForegroundColor Red
    exit 1
}

