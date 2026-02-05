# Uninstall JDK 17 and Install JDK 21
# Run as Administrator

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "JDK 21 Installation" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "ERROR: This script must be run as Administrator!" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Step 1: Uninstall existing JDK 17
Write-Host "[1/3] Removing JDK 17..." -ForegroundColor Yellow
$jdk17Path = "C:\Program Files\Eclipse Adoptium\jdk-17.0.17.10-hotspot"
if (Test-Path $jdk17Path) {
    Write-Host "  Found JDK 17 at: $jdk17Path" -ForegroundColor Yellow
    Remove-Item -Path $jdk17Path -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "  ✓ JDK 17 removed" -ForegroundColor Green
}
else {
    Write-Host "  No JDK 17 found to remove" -ForegroundColor Gray
}

Write-Host ""

# Step 2: Download JDK 21
Write-Host "[2/3] Downloading OpenJDK 21..." -ForegroundColor Yellow
$jdk21Url = "https://download.oracle.com/java/21/latest/jdk-21_windows-x64_bin.msi"
$jdk21Installer = "$env:TEMP\jdk-21-installer.msi"

try {
    Invoke-WebRequest -Uri $jdk21Url -OutFile $jdk21Installer -UseBasicParsing
    Write-Host "  ✓ Download complete" -ForegroundColor Green
}
catch {
    Write-Host "  ✗ Download failed: $_" -ForegroundColor Red
    Write-Host "  Trying alternative source (Adoptium)..." -ForegroundColor Yellow
    
    # Alternative: Use Adoptium (Eclipse Temurin)
    $jdk21Url = "https://api.adoptium.net/v3/binary/latest/21/ga/windows/x64/jdk/hotspot/normal/eclipse?project=jdk"
    try {
        Invoke-WebRequest -Uri $jdk21Url -OutFile $jdk21Installer -UseBasicParsing
        Write-Host "  ✓ Download complete from Adoptium" -ForegroundColor Green
    }
    catch {
        Write-Host "  ✗ All download attempts failed" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

Write-Host ""

# Step 3: Install JDK 21
Write-Host "[3/3] Installing OpenJDK 21..." -ForegroundColor Yellow
$installArgs = @(
    "/i"
    $jdk21Installer
    "/quiet"
    "ADDLOCAL=FeatureMain,FeatureEnvironment,FeatureJarFileRunWith,FeatureJavaHome"
    "INSTALLDIR=C:\Program Files\Eclipse Adoptium\jdk-21"
)

try {
    Start-Process msiexec.exe -ArgumentList $installArgs -Wait -NoNewWindow
    Write-Host "  ✓ JDK 21 installed successfully!" -ForegroundColor Green
}
catch {
    Write-Host "  ✗ Installation failed: $_" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Clean up installer
Remove-Item $jdk21Installer -Force -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Configuration" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Find JDK 21 installation
$jdk21Path = Get-ChildItem "C:\Program Files\Eclipse Adoptium" -Directory -ErrorAction SilentlyContinue | 
Where-Object { $_.Name -like "*jdk-21*" } | 
Select-Object -First 1 -ExpandProperty FullName

if ($jdk21Path) {
    Write-Host "✓ Found JDK 21 at: $jdk21Path" -ForegroundColor Green
    
    # Set JAVA_HOME
    [System.Environment]::SetEnvironmentVariable('JAVA_HOME', $jdk21Path, 'Machine')
    Write-Host "✓ JAVA_HOME set to: $jdk21Path" -ForegroundColor Green
    
    # Update PATH
    $machinePath = [System.Environment]::GetEnvironmentVariable('Path', 'Machine')
    $javaBin = "$jdk21Path\bin"
    
    # Remove old Java paths
    $machinePath = $machinePath -replace '[^;]*jdk-17[^;]*;?', ''
    
    if ($machinePath -notlike "*$javaBin*") {
        [System.Environment]::SetEnvironmentVariable('Path', "$javaBin;$machinePath", 'Machine')
        Write-Host "✓ PATH updated" -ForegroundColor Green
    }
}
else {
    Write-Host "⚠ Could not locate JDK 21 installation" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✓ Installation Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "IMPORTANT: Restart your terminal and run:" -ForegroundColor Yellow
Write-Host "  java -version" -ForegroundColor White
Write-Host ""

Read-Host "Press Enter to exit"
