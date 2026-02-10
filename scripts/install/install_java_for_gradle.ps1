# Install Java JDK for Gradle - Project-AI
# This script must be run as Administrator

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Java JDK Installation for Gradle" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "ERROR: This script must be run as Administrator!" -ForegroundColor Red
    Write-Host "Right-click PowerShell and select 'Run as Administrator', then run this script again." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Step 1: Install Chocolatey if not present
Write-Host "[1/4] Checking for Chocolatey..." -ForegroundColor Yellow
try {
    $chocoVersion = choco --version 2>$null
    Write-Host "✓ Chocolatey is already installed (version $chocoVersion)" -ForegroundColor Green
}
catch {
    Write-Host "⚠ Chocolatey not found. Installing..." -ForegroundColor Yellow
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
    
    # Refresh environment
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
    
    Write-Host "✓ Chocolatey installed successfully!" -ForegroundColor Green
}

Write-Host ""

# Step 2: Install OpenJDK 21
Write-Host "[2/4] Installing OpenJDK 21..." -ForegroundColor Yellow
choco install openjdk21 -y

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ OpenJDK 21 installed successfully!" -ForegroundColor Green
}
else {
    Write-Host "✗ Failed to install OpenJDK 21" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""

# Step 3: Refresh environment and set JAVA_HOME
Write-Host "[3/4] Configuring JAVA_HOME..." -ForegroundColor Yellow

# Refresh environment variables
$env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
refreshenv 2>$null

# Find Java installation
$javaPath = $null
$possiblePaths = @(
    "C:\Program Files\Eclipse Adoptium\jdk-21*",
    "C:\Program Files\OpenJDK\jdk-21*",
    "C:\Program Files\Java\jdk-21*",
    "C:\Program Files (x86)\Eclipse Adoptium\jdk-21*",
    "C:\Program Files (x86)\OpenJDK\jdk-21*"
)

foreach ($pattern in $possiblePaths) {
    $found = Get-Item $pattern -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($found) {
        $javaPath = $found.FullName
        break
    }
}

if ($javaPath) {
    Write-Host "✓ Found Java at: $javaPath" -ForegroundColor Green
    
    # Set JAVA_HOME system-wide
    [System.Environment]::SetEnvironmentVariable('JAVA_HOME', $javaPath, 'Machine')
    $env:JAVA_HOME = $javaPath
    
    # Add to PATH if not already there
    $machinePath = [System.Environment]::GetEnvironmentVariable('Path', 'Machine')
    $javaBin = "$javaPath\bin"
    if ($machinePath -notlike "*$javaBin*") {
        [System.Environment]::SetEnvironmentVariable('Path', "$machinePath;$javaBin", 'Machine')
        Write-Host "✓ Added Java to system PATH" -ForegroundColor Green
    }
    
    Write-Host "✓ JAVA_HOME set to: $javaPath" -ForegroundColor Green
}
else {
    Write-Host "⚠ Warning: Could not automatically locate Java installation" -ForegroundColor Yellow
    Write-Host "You may need to set JAVA_HOME manually" -ForegroundColor Yellow
}

Write-Host ""

# Step 4: Verify installation
Write-Host "[4/4] Verifying installation..." -ForegroundColor Yellow

# Refresh environment one more time
$env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")

try {
    $javaVersion = java -version 2>&1 | Select-Object -First 1
    Write-Host "✓ Java installation verified!" -ForegroundColor Green
    Write-Host "  Version: $javaVersion" -ForegroundColor Cyan
}
catch {
    Write-Host "✗ Could not verify Java installation" -ForegroundColor Red
    Write-Host "  You may need to restart your computer and run this script again" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Installation Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✓ Chocolatey: Installed" -ForegroundColor Green
Write-Host "✓ OpenJDK 21: Installed" -ForegroundColor Green
Write-Host "✓ JAVA_HOME: Configured" -ForegroundColor Green
Write-Host ""
Write-Host "IMPORTANT: You must restart your terminal/PowerShell" -ForegroundColor Yellow
Write-Host "for the environment variables to take effect!" -ForegroundColor Yellow
Write-Host ""
Write-Host "After restarting, test with:" -ForegroundColor Cyan
Write-Host "  java -version" -ForegroundColor White
Write-Host "  .\gradlew.bat tasks --all" -ForegroundColor White
Write-Host ""

Read-Host "Press Enter to exit"
