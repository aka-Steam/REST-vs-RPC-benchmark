# PowerShell script to run all benchmark tests automatically
# Usage:
#   .\scripts\run_full_benchmark.ps1
#   .\scripts\run_full_benchmark.ps1 -Scenarios sanity,normal
#   .\scripts\run_full_benchmark.ps1 -Services rest,grpc -Scenarios sanity,normal,stress

param(
    [string[]]$Services = @("rest", "grpc"),
    [string[]]$Scenarios = @("sanity", "normal", "stress", "stability"),
    [switch]$Headless,
    [switch]$CleanupDB,
    [switch]$SetupData,
    [int]$TestDataCount = 100,
    [string]$ConfigFile = "config/test_scenarios.yaml"
)

$ErrorActionPreference = "Stop"

# Colors for output
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

Write-ColorOutput "========================================" "Cyan"
Write-ColorOutput "Full Benchmark Test Suite" "Cyan"
Write-ColorOutput "========================================" "Cyan"
Write-Host ""

# Validate services
$ValidServices = @("rest", "grpc")
foreach ($service in $Services) {
    if ($service -notin $ValidServices) {
        Write-ColorOutput "Error: Invalid service '$service'. Valid services: rest, grpc" "Red"
        exit 1
    }
}

# Validate scenarios
$ValidScenarios = @("sanity", "normal", "stress", "stability")
foreach ($scenario in $Scenarios) {
    if ($scenario -notin $ValidScenarios) {
        Write-ColorOutput "Error: Invalid scenario '$scenario'. Valid scenarios: sanity, normal, stress, stability" "Red"
        exit 1
    }
}

Write-ColorOutput "Configuration:" "Cyan"
Write-ColorOutput "  Services: $($Services -join ', ')" "White"
Write-ColorOutput "  Scenarios: $($Scenarios -join ', ')" "White"
Write-ColorOutput "  Headless: $Headless" "White"
Write-ColorOutput "  Cleanup DB: $CleanupDB" "White"
Write-ColorOutput "  Setup Data: $SetupData" "White"
Write-ColorOutput "  Test Data Count: $TestDataCount" "White"
Write-Host ""

# Step 1: Cleanup databases if requested
if ($CleanupDB) {
    Write-ColorOutput "Step 1: Cleaning up databases..." "Yellow"
    try {
        python scripts/cleanup_db.py --yes
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "  [OK] Databases cleaned" "Green"
        } else {
            Write-ColorOutput "  [FAIL] Database cleanup failed" "Red"
        }
    } catch {
        Write-ColorOutput "  [FAIL] Error cleaning databases: $_" "Red"
    }
    Write-Host ""
}

# Step 2: Setup test data if requested
if ($SetupData) {
    Write-ColorOutput "Step 2: Setting up test data..." "Yellow"
    try {
        $setupArgs = @("scripts/setup_test_data.py", "--count", $TestDataCount.ToString())
        
        if ($Services -contains "rest" -and $Services -contains "grpc") {
            # Setup both
        } elseif ($Services -contains "rest") {
            $setupArgs += @("--rest-only")
        } elseif ($Services -contains "grpc") {
            $setupArgs += @("--grpc-only")
        }
        
        python @setupArgs
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "  [OK] Test data setup completed" "Green"
        } else {
            Write-ColorOutput "  [FAIL] Test data setup failed" "Red"
        }
    } catch {
        Write-ColorOutput "  [FAIL] Error setting up test data: $_" "Red"
    }
    Write-Host ""
}

# Step 3: Run tests
Write-ColorOutput "Step 3: Running benchmark tests..." "Yellow"
Write-Host ""

$totalTests = $Services.Count * $Scenarios.Count
$currentTest = 0
$failedTests = @()
$passedTests = @()

$startTime = Get-Date

foreach ($service in $Services) {
    Write-ColorOutput "----------------------------------------" "Cyan"
    Write-ColorOutput "Service: $service" "Cyan"
    Write-ColorOutput "----------------------------------------" "Cyan"
    Write-Host ""
    
    foreach ($scenario in $Scenarios) {
        $currentTest++
        Write-ColorOutput "[$currentTest/$totalTests] Running $service - $scenario..." "Yellow"
        
        try {
            $scriptPath = ".\scripts\run_benchmark.ps1"
            $params = @{
                Service = $service
                Scenario = $scenario
                ConfigFile = $ConfigFile
            }
            
            if ($Headless) {
                $params.Headless = $true
            }
            
            & $scriptPath @params
            
            if ($LASTEXITCODE -eq 0) {
                Write-ColorOutput "  [OK] $service - $scenario completed successfully" "Green"
                $passedTests += "$service-$scenario"
            } else {
                Write-ColorOutput "  [FAIL] $service - $scenario failed with exit code $LASTEXITCODE" "Red"
                $failedTests += "$service-$scenario"
            }
        } catch {
            Write-ColorOutput "  [FAIL] $service - $scenario failed with error: $_" "Red"
            $failedTests += "$service-$scenario"
        }
        
        Write-Host ""
        
        # Small delay between tests
        Start-Sleep -Seconds 2
    }
    
    Write-Host ""
}

$endTime = Get-Date
$duration = $endTime - $startTime

# Step 4: Summary
Write-ColorOutput "========================================" "Cyan"
Write-ColorOutput "Benchmark Test Suite Summary" "Cyan"
Write-ColorOutput "========================================" "Cyan"
Write-Host ""

Write-ColorOutput "Total Duration: $($duration.ToString('hh\:mm\:ss'))" "White"
Write-ColorOutput "Total Tests: $totalTests" "White"
Write-ColorOutput "Passed: $($passedTests.Count)" "Green"
Write-ColorOutput "Failed: $($failedTests.Count)" "Red"
Write-Host ""

if ($failedTests.Count -gt 0) {
    Write-ColorOutput "Failed Tests:" "Red"
    foreach ($test in $failedTests) {
        Write-ColorOutput "  - $test" "Red"
    }
    Write-Host ""
}

# Generate summary report
$summaryFile = "results/benchmark_summary_$(Get-Date -Format 'yyyyMMdd_HHmmss').txt"
$timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
$servicesList = $Services -join ', '
$scenariosList = $Scenarios -join ', '
$durationStr = $duration.ToString('hh\:mm\:ss')

$passedTestsList = ""
if ($passedTests.Count -gt 0) {
    $passedTestsList = $passedTests | ForEach-Object { "  - $_" } | Out-String
} else {
    $passedTestsList = "  (none)"
}

$failedTestsList = ""
if ($failedTests.Count -gt 0) {
    $failedTestsList = $failedTests | ForEach-Object { "  - $_" } | Out-String
} else {
    $failedTestsList = "  (none)"
}

$summaryContent = "Benchmark Test Suite Summary`r`n" +
                  "Generated: $timestamp`r`n`r`n" +
                  "Configuration:`r`n" +
                  "  Services: $servicesList`r`n" +
                  "  Scenarios: $scenariosList`r`n" +
                  "  Headless: $Headless`r`n" +
                  "  Cleanup DB: $CleanupDB`r`n" +
                  "  Setup Data: $SetupData`r`n" +
                  "  Test Data Count: $TestDataCount`r`n`r`n" +
                  "Results:`r`n" +
                  "  Total Tests: $totalTests`r`n" +
                  "  Passed: $($passedTests.Count)`r`n" +
                  "  Failed: $($failedTests.Count)`r`n" +
                  "  Duration: $durationStr`r`n`r`n" +
                  "Passed Tests:`r`n$passedTestsList`r`n" +
                  "Failed Tests:`r`n$failedTestsList"

$summaryContent | Out-File -FilePath $summaryFile -Encoding UTF8
Write-ColorOutput "Summary report saved to: $summaryFile" "Cyan"
Write-Host ""

# Exit with error code if any tests failed
if ($failedTests.Count -gt 0) {
    Write-ColorOutput "Some tests failed. Check the summary report for details." "Yellow"
    exit 1
} else {
    Write-ColorOutput "All tests completed successfully!" "Green"
    exit 0
}
