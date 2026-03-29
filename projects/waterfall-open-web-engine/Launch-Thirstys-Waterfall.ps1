# Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master
# Thirstys-Waterfall Desktop Launcher
# ====================================
# Ensures the server is running and opens the web interface in your default browser

param(
    [switch]$StartServer = $true
)

# Set the project directory
$ProjectDir = "c:\Users\Quencher\.gemini\antigravity\scratch\sovereign-repos\Thirstys-waterfall"
$WebUrl = "http://localhost:8080"

Write-Host "🌊 Thirstys-Waterfall Launcher" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Change to project directory
Set-Location $ProjectDir

# Check if Docker is running
Write-Host "Checking Docker status..." -ForegroundColor Yellow
$dockerRunning = docker info 2>$null
if (-not $dockerRunning) {
    Write-Host "❌ Docker is not running. Please start Docker Desktop first." -ForegroundColor Red
    pause
    exit 1
}

# Check if container is running
Write-Host "Checking Thirstys-Waterfall container..." -ForegroundColor Yellow
$containerStatus = docker ps --filter "name=thirstys-waterfall" --format "{{.Status}}"

if ($containerStatus) {
    Write-Host "✅ Container is already running: $containerStatus" -ForegroundColor Green
} else {
    # Check if container exists but is stopped
    $containerExists = docker ps -a --filter "name=thirstys-waterfall" --format "{{.Names}}"
    
    if ($containerExists) {
        Write-Host "🔄 Starting stopped container..." -ForegroundColor Yellow
        docker start thirstys-waterfall
        Start-Sleep -Seconds 5
    } else {
        Write-Host "🚀 Starting Thirstys-Waterfall for the first time..." -ForegroundColor Yellow
        docker-compose up -d
        Start-Sleep -Seconds 10
    }
}

# Wait for server to be ready
Write-Host "Waiting for server to be ready..." -ForegroundColor Yellow
$maxAttempts = 30
$attempt = 0
$serverReady = $false

while ($attempt -lt $maxAttempts -and -not $serverReady) {
    try {
        $response = Invoke-WebRequest -Uri "$WebUrl/health" -TimeoutSec 2 -UseBasicParsing -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            $serverReady = $true
        }
    } catch {
        # Server not ready yet
    }
    
    if (-not $serverReady) {
        $attempt++
        Start-Sleep -Seconds 1
        Write-Host "." -NoNewline
    }
}

Write-Host ""

if ($serverReady) {
    Write-Host "✅ Server is ready!" -ForegroundColor Green
    Write-Host "🌐 Opening Thirstys-Waterfall in your browser..." -ForegroundColor Cyan
    Start-Process $WebUrl
    Write-Host ""
    Write-Host "🎉 Thirstys-Waterfall is now running at $WebUrl" -ForegroundColor Cyan
    Write-Host "   To stop: Run 'docker-compose down' in the project directory" -ForegroundColor Gray
} else {
    Write-Host "❌ Server failed to start within 30 seconds." -ForegroundColor Red
    Write-Host "   Check logs with: docker logs thirstys-waterfall" -ForegroundColor Yellow
    pause
    exit 1
}
