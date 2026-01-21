# PowerShell script to start gRPC service
# Usage: .\scripts\start_grpc_service.ps1

$ErrorActionPreference = "Stop"

Write-Host "Starting gRPC service..." -ForegroundColor Cyan
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

# Change to gRPC service directory
$grpcServiceDir = Join-Path $projectRoot "glossary_RPCservice"
$grpcServiceDir = Resolve-Path $grpcServiceDir

if (-not (Test-Path $grpcServiceDir)) {
    Write-Host "Error: gRPC service directory not found: $grpcServiceDir" -ForegroundColor Red
    exit 1
}

Set-Location $grpcServiceDir

# Check if protobuf files exist
$pb2File = Join-Path $grpcServiceDir "glossary_pb2.py"
$pb2GrpcFile = Join-Path $grpcServiceDir "glossary_pb2_grpc.py"

if (-not (Test-Path $pb2File) -or -not (Test-Path $pb2GrpcFile)) {
    Write-Host "Protobuf files not found. Generating..." -ForegroundColor Yellow
    $protoFile = Join-Path $grpcServiceDir "proto" "glossary.proto"
    
    if (-not (Test-Path $protoFile)) {
        Write-Host "Error: proto file not found: $protoFile" -ForegroundColor Red
        exit 1
    }
    
    & $pythonCmd -m grpc_tools.protoc -I proto --python_out=. --grpc_python_out=. proto\glossary.proto
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error: Failed to generate protobuf files" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "Protobuf files generated successfully" -ForegroundColor Green
}

Write-Host ""
Write-Host "Starting gRPC service on localhost:50051" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop the service" -ForegroundColor Yellow
Write-Host ""

# Start gRPC server
& $pythonCmd -m server.server

