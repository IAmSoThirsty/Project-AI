# Quick verification script for JDK 21 and Gradle setup
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Gradle + JavaScript Setup Verification" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Java
Write-Host "[1/4] Checking Java installation..." -ForegroundColor Yellow
try {
    $javaVersion = java -version 2>&1 | Select-Object -First 3
    Write-Host "✓ Java is installed:" -ForegroundColor Green
    $javaVersion | ForEach-Object { Write-Host "  $_" -ForegroundColor Cyan }
}
catch {
    Write-Host "✗ Java not found. Please restart your terminal!" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Check JAVA_HOME
Write-Host "[2/4] Checking JAVA_HOME..." -ForegroundColor Yellow
if ($env:JAVA_HOME) {
    Write-Host "✓ JAVA_HOME is set to: $env:JAVA_HOME" -ForegroundColor Green
}
else {
    Write-Host "⚠ JAVA_HOME not set. Please restart your terminal!" -ForegroundColor Yellow
}

Write-Host ""

# Test Gradle
Write-Host "[3/4] Testing Gradle..." -ForegroundColor Yellow
try {
    $gradleOutput = .\gradlew.bat --version 2>&1 | Select-String "Gradle"
    Write-Host "✓ Gradle is working:" -ForegroundColor Green
    Write-Host "  $gradleOutput" -ForegroundColor Cyan
}
catch {
    Write-Host "✗ Gradle test failed" -ForegroundColor Red
    Write-Host "  Error: $_" -ForegroundColor Red
}

Write-Host ""

# Show available npm tasks
Write-Host "[4/4] Available Gradle tasks for JavaScript:" -ForegroundColor Yellow
Write-Host "  .\gradlew.bat npmInstall   - Install Node.js dependencies" -ForegroundColor Cyan
Write-Host "  .\gradlew.bat npmTest      - Run JavaScript tests" -ForegroundColor Cyan
Write-Host "  .\gradlew.bat npmBuild     - Build JavaScript/TypeScript" -ForegroundColor Cyan
Write-Host "  .\gradlew.bat npmDev       - Run development server" -ForegroundColor Cyan
Write-Host "  .\gradlew.bat npmLint      - Lint markdown files" -ForegroundColor Cyan

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✓ Setup verification complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Try running: .\gradlew.bat npmInstall" -ForegroundColor Yellow
Write-Host ""
