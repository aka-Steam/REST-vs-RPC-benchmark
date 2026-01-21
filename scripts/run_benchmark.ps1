# PowerShell script to run Locust benchmark tests
# Usage:
#   .\scripts\run_benchmark.ps1 -Service rest -Scenario sanity
#   .\scripts\run_benchmark.ps1 -Service grpc -Scenario stress -Headless

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("rest", "grpc")]
    [string]$Service,
    
    [Parameter(Mandatory=$true)]
    [ValidateSet("sanity", "normal", "stress", "stability")]
    [string]$Scenario,
    
    [switch]$Headless,
    
    [string]$ConfigFile = "config/test_scenarios.yaml"
)

# Import required modules
$ErrorActionPreference = "Stop"

# Function to parse YAML (simplified - requires PyYAML in Python)
function Get-ScenarioConfig {
    param(
        [string]$ConfigFile,
        [string]$ScenarioName
    )
    
    # Use Python to parse YAML
    $pythonScript = @"
import yaml
import sys
import json

with open('$ConfigFile', 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

scenario = config['scenarios']['$ScenarioName']
service = config['services']['$Service']
output = config['output']

result = {
    'scenario': scenario,
    'service': service,
    'output': output
}

print(json.dumps(result))
"@
    
    $json = python -c $pythonScript
    return $json | ConvertFrom-Json
}

# Function to check if service is running
function Test-ServiceHealth {
    param(
        [string]$ServiceType,
        [string]$ServiceHost
    )
    
    if ($ServiceType -eq "rest") {
        try {
            $response = Invoke-WebRequest -Uri "$ServiceHost/health" -Method GET -TimeoutSec 2 -UseBasicParsing
            return $response.StatusCode -eq 200
        } catch {
            return $false
        }
    } elseif ($ServiceType -eq "grpc") {
        # For gRPC, we'll just check if port is open (simplified)
        $hostParts = $ServiceHost -split ":"
        $hostname = $hostParts[0]
        $port = if ($hostParts.Length -gt 1) { [int]$hostParts[1] } else { 50051 }
        
        try {
            $tcpClient = New-Object System.Net.Sockets.TcpClient
            $tcpClient.Connect($hostname, $port)
            $tcpClient.Close()
            return $true
        } catch {
            return $false
        }
    }
    return $false
}

# Main script
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Locust Benchmark Test Runner" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is available
try {
    $pythonVersion = python --version
    Write-Host "Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Error: Python is not available. Please install Python." -ForegroundColor Red
    exit 1
}

# Check if Locust is installed
try {
    $locustVersion = python -m locust --version 2>&1
    Write-Host "Locust: $locustVersion" -ForegroundColor Green
} catch {
    Write-Host "Error: Locust is not installed. Run: pip install -r requirements_benchmark.txt" -ForegroundColor Red
    exit 1
}

# Check if PyYAML is available
try {
    python -c "import yaml" 2>&1 | Out-Null
} catch {
    Write-Host "Warning: PyYAML not found. Installing..." -ForegroundColor Yellow
    pip install pyyaml
}

# Load configuration
Write-Host "Loading configuration from $ConfigFile..." -ForegroundColor Yellow
try {
    $config = Get-ScenarioConfig -ConfigFile $ConfigFile -ScenarioName $Scenario
} catch {
    Write-Host "Error: Failed to load configuration. Using defaults." -ForegroundColor Red
    exit 1
}

$scenarioConfig = $config.scenario
$serviceConfig = $config.service
$outputConfig = $config.output

Write-Host ""
Write-Host "Test Configuration:" -ForegroundColor Cyan
Write-Host "  Service: $($serviceConfig.name)" -ForegroundColor White
Write-Host "  Scenario: $($scenarioConfig.name)" -ForegroundColor White
Write-Host "  Description: $($scenarioConfig.description)" -ForegroundColor White
Write-Host "  Users: $($scenarioConfig.users)" -ForegroundColor White
Write-Host "  Spawn Rate: $($scenarioConfig.spawn_rate) users/sec" -ForegroundColor White
Write-Host "  Duration: $($scenarioConfig.duration)" -ForegroundColor White
Write-Host ""

# Check service health
Write-Host "Checking service health..." -ForegroundColor Yellow
$isHealthy = Test-ServiceHealth -ServiceType $Service -ServiceHost $serviceConfig.host

if (-not $isHealthy) {
    Write-Host "Warning: Service at $($serviceConfig.host) appears to be unavailable." -ForegroundColor Yellow
    Write-Host "Please ensure the service is running before starting the test." -ForegroundColor Yellow
    $continue = Read-Host "Continue anyway? (y/N)"
    if ($continue -ne "y" -and $continue -ne "Y") {
        exit 1
    }
} else {
    Write-Host "Service is healthy!" -ForegroundColor Green
}

Write-Host ""

# Prepare output directory
$outputDir = Join-Path $outputConfig.base_dir $Service
$outputDir = Join-Path $outputDir $Scenario

if (-not (Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
    Write-Host "Created output directory: $outputDir" -ForegroundColor Green
}

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$csvPrefix = Join-Path $outputDir "${Service}_${Scenario}_${timestamp}"

# Build Locust command
$locustArgs = @(
    "-f", $serviceConfig.locustfile
)

if ($Service -eq "rest") {
    $locustArgs += @("-H", $serviceConfig.host)
}

if ($Headless) {
    $locustArgs += @(
        "--headless",
        "-u", $scenarioConfig.users.ToString(),
        "-r", $scenarioConfig.spawn_rate.ToString(),
        "-t", $scenarioConfig.duration
    )
}

if ($outputConfig.csv_prefix) {
    $locustArgs += @("--csv", $csvPrefix)
}

if ($outputConfig.html_report) {
    $htmlFile = Join-Path $outputDir "${Service}_${Scenario}_${timestamp}.html"
    $locustArgs += @("--html", $htmlFile)
}

if ($outputConfig.json_report) {
    $jsonFile = Join-Path $outputDir "${Service}_${Scenario}_${timestamp}.json"
    $locustArgs += @("--json-file", $jsonFile)
}

# Add user class if specified
if ($serviceConfig.user_class) {
    $locustArgs += $serviceConfig.user_class
}

Write-Host "Starting Locust test..." -ForegroundColor Cyan
Write-Host "Command: python -m locust $($locustArgs -join ' ')" -ForegroundColor Gray
Write-Host ""

# Run Locust
try {
    python -m locust @locustArgs
    $exitCode = $LASTEXITCODE
    
    if ($exitCode -eq 0) {
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Green
        Write-Host "Test completed successfully!" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "Results saved to: $outputDir" -ForegroundColor Cyan
        
        if ($outputConfig.csv_prefix) {
            Write-Host "CSV files:" -ForegroundColor Cyan
            Get-ChildItem -Path "$csvPrefix*.csv" | ForEach-Object {
                Write-Host "  - $($_.Name)" -ForegroundColor White
            }
        }
        
        if ($outputConfig.html_report) {
            Write-Host "HTML report: $htmlFile" -ForegroundColor Cyan
        }
    } else {
        Write-Host ""
        Write-Host "Test completed with exit code: $exitCode" -ForegroundColor Yellow
    }
    
    exit $exitCode
} catch {
    Write-Host ""
    Write-Host "Error running Locust: $_" -ForegroundColor Red
    exit 1
}

