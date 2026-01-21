# PowerShell script to stop Docker services
# Usage: .\scripts\stop_services_docker.ps1

$ErrorActionPreference = "Stop"

Write-Host "Stopping Docker services..." -ForegroundColor Yellow

# Get project root
$projectRoot = Split-Path $PSScriptRoot -Parent
Set-Location $projectRoot

# Check if docker-compose is available
try {
    docker compose version | Out-Null
    $composeCmd = "docker compose"
} catch {
    try {
        docker-compose --version | Out-Null
        $composeCmd = "docker-compose"
    } catch {
        Write-Host "Error: Docker Compose is not available." -ForegroundColor Red
        exit 1
    }
}

& $composeCmd down

if ($LASTEXITCODE -eq 0) {
    Write-Host "Services stopped successfully." -ForegroundColor Green
} else {
    Write-Host "Error: Failed to stop services" -ForegroundColor Red
    exit 1
}

