<#
.SYNOPSIS
    Installs and Launches the Project-AI Sovereign Stack (Production Mode).
    Requires Docker Desktop.
#>

Write-Host ">>> PROJECT-AI SOVEREIGN DEPLOYMENT <<<" -ForegroundColor Cyan

# 1. Check Docker
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "[!] Docker not found. Please install Docker Desktop." -ForegroundColor Red
    exit 1
}

# 2. Check Composition
if (-not (Test-Path "docker-compose.yml")) {
    Write-Host "[!] docker-compose.yml not found in current directory." -ForegroundColor Red
    exit 1
}

# 3. Launch
Write-Host "Initializing Sovereign Network..." -ForegroundColor Yellow
docker-compose up -d --build

if ($LASTEXITCODE -eq 0) {
    Write-Host ">>> DEPLOYMENT SUCCESSFUL <<<" -ForegroundColor Green
    Write-Host "Cerberus Omega is running in isolated sovereign network."
    Write-Host "Spine Data is persisted in volume 'spine_data'."
}
else {
    Write-Host "[!] Deployment Failed." -ForegroundColor Red
    exit 1
}
