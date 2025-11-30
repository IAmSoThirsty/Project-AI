# Codacy CLI Docker Setup Script
# Run this AFTER Docker Desktop is installed and running

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Codacy CLI Docker Configuration" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is running
Write-Host "Checking Docker installation..." -ForegroundColor Green
try {
    $dockerVersion = docker --version
    Write-Host "✓ Docker is installed: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker is not installed or not running!" -ForegroundColor Red
    Write-Host "Please install Docker Desktop first using setup-docker-wsl.ps1" -ForegroundColor Yellow
    exit 1
}

# Test Docker with hello-world
Write-Host "`nTesting Docker..." -ForegroundColor Green
docker run --rm hello-world
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Docker is working correctly!" -ForegroundColor Green
} else {
    Write-Host "✗ Docker test failed. Please ensure Docker Desktop is running." -ForegroundColor Red
    exit 1
}

# Pull Codacy Analysis CLI image
Write-Host "`nPulling Codacy Analysis CLI Docker image..." -ForegroundColor Green
Write-Host "This may take a few minutes..." -ForegroundColor Yellow
docker pull codacy/codacy-analysis-cli:latest

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Codacy CLI image pulled successfully!" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to pull Codacy CLI image" -ForegroundColor Red
    exit 1
}

# Create helper function/alias
Write-Host "`nCreating Codacy CLI wrapper function..." -ForegroundColor Green

$functionScript = @'
function Invoke-CodacyAnalysis {
    param(
        [string]$Directory = ".",
        [string]$Tool = "",
        [string]$File = ""
    )
    
    $absolutePath = (Resolve-Path $Directory).Path
    
    $dockerArgs = @(
        "run",
        "--rm",
        "-v", "${absolutePath}:/src",
        "codacy/codacy-analysis-cli:latest",
        "analyze",
        "--directory", "/src"
    )
    
    if ($Tool) {
        $dockerArgs += "--tool"
        $dockerArgs += $Tool
    }
    
    if ($File) {
        $dockerArgs += "--file"
        $dockerArgs += $File
    }
    
    docker @dockerArgs
}

Set-Alias -Name codacy-analyze -Value Invoke-CodacyAnalysis
'@

$profilePath = $PROFILE
if (-not (Test-Path $profilePath)) {
    New-Item -ItemType File -Path $profilePath -Force | Out-Null
}

# Check if function already exists in profile
$profileContent = Get-Content $profilePath -Raw -ErrorAction SilentlyContinue
if ($profileContent -notmatch "Invoke-CodacyAnalysis") {
    Add-Content -Path $profilePath -Value "`n# Codacy CLI Helper Function`n$functionScript"
    Write-Host "✓ Codacy CLI function added to PowerShell profile" -ForegroundColor Green
} else {
    Write-Host "✓ Codacy CLI function already exists in profile" -ForegroundColor Yellow
}

# Test Codacy CLI
Write-Host "`nTesting Codacy CLI..." -ForegroundColor Green
docker run --rm codacy/codacy-analysis-cli:latest --help | Select-Object -First 10

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Codacy CLI Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "USAGE:" -ForegroundColor Yellow
Write-Host "1. Restart PowerShell to load the new function" -ForegroundColor White
Write-Host "2. Run: codacy-analyze -Directory . -Tool trivy" -ForegroundColor White
Write-Host "3. Or use Docker directly:" -ForegroundColor White
Write-Host "   docker run --rm -v ${PWD}:/src codacy/codacy-analysis-cli analyze --directory /src" -ForegroundColor Gray
Write-Host ""
Write-Host "Example: Analyze current project with all tools" -ForegroundColor Yellow
Write-Host "   codacy-analyze -Directory ." -ForegroundColor White
Write-Host ""
Write-Host "Example: Analyze specific file with specific tool" -ForegroundColor Yellow
Write-Host "   codacy-analyze -Directory . -Tool ruff -File src/app/core/image_generator.py" -ForegroundColor White
Write-Host ""

Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
