# Docker & WSL Installation Script for Project-AI
# Run this script as Administrator

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Docker & WSL Setup for Project-AI" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "ERROR: This script must be run as Administrator!" -ForegroundColor Red
    Write-Host "Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    exit 1
}

Write-Host "Step 1: Installing WSL (Windows Subsystem for Linux)" -ForegroundColor Green
Write-Host "This will install WSL 2 with Ubuntu..." -ForegroundColor Yellow

# Install WSL
wsl --install --no-distribution
if ($LASTEXITCODE -ne 0) {
    Write-Host "WSL installation initiated. You may need to restart your computer." -ForegroundColor Yellow
}

# Enable required Windows features
Write-Host "`nStep 2: Enabling Windows Features..." -ForegroundColor Green
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

# Set WSL 2 as default
Write-Host "`nStep 3: Setting WSL 2 as default version..." -ForegroundColor Green
wsl --set-default-version 2

# Download and install Ubuntu
Write-Host "`nStep 4: Installing Ubuntu distribution..." -ForegroundColor Green
wsl --install -d Ubuntu

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "WSL Installation Phase Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "IMPORTANT NEXT STEPS:" -ForegroundColor Yellow
Write-Host "1. RESTART your computer now" -ForegroundColor Yellow
Write-Host "2. After restart, Ubuntu will automatically launch" -ForegroundColor Yellow
Write-Host "3. Create a username and password for Ubuntu" -ForegroundColor Yellow
Write-Host "4. Run this script again to continue with Docker installation" -ForegroundColor Yellow
Write-Host ""

# Check if WSL is already functional
$wslStatus = wsl --status 2>&1
if ($wslStatus -match "running") {
    Write-Host "WSL appears to be functional. Continuing with Docker installation..." -ForegroundColor Green
    
    # Download Docker Desktop
    Write-Host "`nStep 5: Downloading Docker Desktop..." -ForegroundColor Green
    $dockerUrl = "https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe"
    $installerPath = "$env:TEMP\DockerDesktopInstaller.exe"
    
    try {
        Invoke-WebRequest -Uri $dockerUrl -OutFile $installerPath -UseBasicParsing
        Write-Host "Download complete!" -ForegroundColor Green
        
        # Install Docker Desktop
        Write-Host "`nStep 6: Installing Docker Desktop..." -ForegroundColor Green
        Write-Host "This will take several minutes..." -ForegroundColor Yellow
        
        Start-Process -FilePath $installerPath -ArgumentList "install --quiet --accept-license" -Wait
        
        Write-Host "`n========================================" -ForegroundColor Cyan
        Write-Host "Docker Desktop Installation Complete!" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "FINAL STEPS:" -ForegroundColor Yellow
        Write-Host "1. Docker Desktop should launch automatically" -ForegroundColor Yellow
        Write-Host "2. Sign in to Docker Desktop (or skip)" -ForegroundColor Yellow
        Write-Host "3. Ensure WSL 2 backend is enabled in Docker settings" -ForegroundColor Yellow
        Write-Host "4. Test with: docker --version" -ForegroundColor Yellow
        Write-Host ""
        
    } catch {
        Write-Host "Error downloading Docker Desktop: $_" -ForegroundColor Red
        Write-Host "You can manually download from: https://www.docker.com/products/docker-desktop/" -ForegroundColor Yellow
    }
} else {
    Write-Host "Please restart your computer and run this script again." -ForegroundColor Yellow
}

Write-Host "`nPress any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
