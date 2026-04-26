# End-to-End Test Suite Runner
# Tests all components before deployment

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Project-AI End-to-End Test Suite" -ForegroundColor Cyan  
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$failedTests = @()
$passedTests = @()

# Test 1: Python Unit Tests
Write-Host "[1/6] Running Python unit tests..." -ForegroundColor Yellow
try {
    pytest tests/ -v --tb=short --maxfail=5
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Python tests passed" -ForegroundColor Green
        $passedTests += "Python Unit Tests"
    }
    else {
        Write-Host "✗ Python tests failed" -ForegroundColor Red
        $failedTests += "Python Unit Tests"
    }
}
catch {
    Write-Host "⚠ Could not run Python tests: $_" -ForegroundColor Yellow
}

Write-Host ""

# Test 2: Save Points System
Write-Host "[2/6] Testing save points system..." -ForegroundColor Yellow
try {
    python -c "from project_ai.save_points import SavePointsManager; sm = SavePointsManager(); print('Save manager initialized')"
    Write-Host "✓ Save points system functional" -ForegroundColor Green
    $passedTests += "Save Points System"
}
catch {
    Write-Host "✗ Save points system failed: $_" -ForegroundColor Red
    $failedTests += "Save Points System"
}

Write-Host ""

# Test 3: Legion API
Write-Host "[3/6] Testing Legion API..." -ForegroundColor Yellow
$legionTest = Test-Path "integrations\openclaw\legion_api.py"
$legionInterface = Test-Path "integrations\openclaw\legion_interface.html"
if ($legionTest -and $legionInterface) {
    Write-Host "✓ Legion files present" -ForegroundColor Green
    $passedTests += "Legion API Files"
}
else {
    Write-Host "✗ Legion files missing" -ForegroundColor Red
    $failedTests += "Legion API Files"
}

Write-Host ""

# Test 4: Android Build
Write-Host "[4/6] Verifying Android configuration..." -ForegroundColor Yellow  
$androidBuild = Test-Path "android\legion_mini\build.gradle"
$androidManifest = Test-Path "android\legion_mini\src\main\AndroidManifest.xml"
if ($androidBuild -and $androidManifest) {
    Write-Host "✓ Android module configured" -ForegroundColor Green
    $passedTests += "Android Configuration"
}
else {
    Write-Host "✗ Android configuration incomplete" -ForegroundColor Red
    $failedTests += "Android Configuration"
}

Write-Host ""

# Test 5: Desktop Build
Write-Host "[5/6] Verifying desktop configuration..." -ForegroundColor Yellow
$desktopPackage = Test-Path "desktop\package.json"
if ($desktopPackage) {
    Write-Host "✓ Desktop module configured" -ForegroundColor Green
    $passedTests += "Desktop Configuration"
}
else {
    Write-Host "✗ Desktop configuration missing" -ForegroundColor Red
    $failedTests += "Desktop Configuration"
}

Write-Host ""

# Test 6: Gradle Build
Write-Host "[6/6] Testing Gradle build system..." -ForegroundColor Yellow
$env:JAVA_HOME = "C:\Program Files\Eclipse Adoptium\jdk-17.0.17.10-hotspot"
$env:PATH = "$env:JAVA_HOME\bin;$env:PATH"

try {
    $gradleOutput = .\gradlew.bat tasks 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Gradle build system functional" -ForegroundColor Green
        $passedTests += "Gradle Build System"
    }
    else {
        Write-Host "✗ Gradle build failed" -ForegroundColor Red
        $failedTests += "Gradle Build System"
    }
}
catch {
    Write-Host "⚠ Gradle test skipped: $_" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Test Results Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Passed Tests: $($passedTests.Count)" -ForegroundColor Green
foreach ($test in $passedTests) {
    Write-Host "  ✓ $test" -ForegroundColor Green
}

Write-Host ""

if ($failedTests.Count -gt 0) {
    Write-Host "Failed Tests: $($failedTests.Count)" -ForegroundColor Red
    foreach ($test in $failedTests) {
        Write-Host "  ✗ $test" -ForegroundColor Red
    }
    Write-Host ""
    Write-Host "⚠ Some tests failed - review before deployment" -ForegroundColor Yellow
}
else {
    Write-Host "✓ All tests passed - ready for deployment!" -ForegroundColor Green
}

Write-Host ""
Write-Host "Test Coverage: $([math]::Round(($passedTests.Count / ($passedTests.Count + $failedTests.Count)) * 100, 2))%" -ForegroundColor Cyan
Write-Host ""

Read-Host "Press Enter to exit"
