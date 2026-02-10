# Docker & WSL Setup Guide for Project-AI

## Overview

This guide walks you through the proper installation of WSL 2, Docker Desktop, and Codacy CLI for Project-AI development.

## Current Status

✅ WSL 2.6.1 installation started
🔄 VirtualMachinePlatform component installing
⏳ Waiting for installation completion

## Step-by-Step Installation Process

### Phase 1: WSL Installation (IN PROGRESS)

1. **Current**: WSL 2.6.1 is installing
1. **Next**: System will require a restart
1. **After restart**: Ubuntu will be set up

### Phase 2: Complete WSL Setup (After Restart)

Run these commands as Administrator:

```powershell
# Run the setup script
.\setup-docker-wsl.ps1
```

Or manually:

```powershell
# Verify WSL installation
wsl --status

# Install Ubuntu (if not already installed)
wsl --install -d Ubuntu

# Set WSL 2 as default
wsl --set-default-version 2

# Verify Ubuntu is running
wsl -l -v
```

### Phase 3: Docker Desktop Installation

After WSL is ready:

```powershell
# Download Docker Desktop
$url = "https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe"
$installer = "$env:TEMP\DockerDesktopInstaller.exe"
Invoke-WebRequest -Uri $url -OutFile $installer

# Install Docker Desktop
Start-Process -FilePath $installer -ArgumentList "install --quiet --accept-license" -Wait

# Start Docker Desktop (will launch automatically after install)
```

### Phase 4: Configure Docker for WSL 2

1. Launch Docker Desktop
1. Go to Settings → General
1. Ensure "Use WSL 2 based engine" is checked
1. Go to Settings → Resources → WSL Integration
1. Enable integration with Ubuntu distribution
1. Click "Apply & Restart"

### Phase 5: Install Codacy CLI

Run the Codacy setup script:

```powershell
.\setup-codacy-cli.ps1
```

Or manually:

```powershell
# Pull Codacy CLI image
docker pull codacy/codacy-analysis-cli:latest

# Test Codacy CLI
docker run --rm codacy/codacy-analysis-cli:latest --help

# Analyze project
docker run --rm `
  -v "${PWD}:/src" `
  codacy/codacy-analysis-cli:latest analyze `
  --directory /src
```

## Quick Reference

### Verify Installations

```powershell
# Check WSL
wsl --version

# Check Docker
docker --version
docker ps

# Check Codacy CLI
docker images | Select-String codacy
```

### Analyze Files with Codacy

#### Analyze entire project

```powershell
docker run --rm -v "${PWD}:/src" codacy/codacy-analysis-cli:latest analyze --directory /src
```

#### Analyze specific file

```powershell
docker run --rm `
  -v "${PWD}:/src" `
  codacy/codacy-analysis-cli:latest analyze `
  --directory /src `
  --file src/app/core/image_generator.py
```

#### Analyze with specific tool (e.g., ruff for Python)

```powershell
docker run --rm `
  -v "${PWD}:/src" `
  codacy/codacy-analysis-cli:latest analyze `
  --directory /src `
  --tool ruff
```

#### Security scan with Trivy

```powershell
docker run --rm `
  -v "${PWD}:/src" `
  codacy/codacy-analysis-cli:latest analyze `
  --directory /src `
  --tool trivy
```

## Troubleshooting

### WSL Issues

**Problem**: WSL command not found
**Solution**: Restart computer after WSL installation

**Problem**: Ubuntu not starting
**Solution**: 
```powershell
wsl --update
wsl --shutdown
wsl -d Ubuntu
```

### Docker Issues

**Problem**: Docker daemon not running
**Solution**: Start Docker Desktop from Start Menu

**Problem**: WSL 2 integration not working
**Solution**: 

1. Open Docker Desktop
1. Settings → Resources → WSL Integration
1. Enable Ubuntu
1. Apply & Restart

### Codacy CLI Issues

**Problem**: Permission denied errors
**Solution**: Ensure you're running PowerShell as Administrator

**Problem**: Cannot pull Docker image
**Solution**: Check internet connection and Docker Hub access

## Helper Functions

Add this to your PowerShell profile (`$PROFILE`):

```powershell
# Codacy Analysis Helper
function Invoke-CodacyAnalysis {
    param(
        [string]$Directory = ".",
        [string]$Tool = "",
        [string]$File = ""
    )
    
    $absolutePath = (Resolve-Path $Directory).Path
    $dockerArgs = @(
        "run", "--rm",
        "-v", "${absolutePath}:/src",
        "codacy/codacy-analysis-cli:latest",
        "analyze", "--directory", "/src"
    )
    
    if ($Tool) { $dockerArgs += "--tool", $Tool }
    if ($File) { $dockerArgs += "--file", $File }
    
    docker @dockerArgs
}

Set-Alias -Name codacy-analyze -Value Invoke-CodacyAnalysis
```

Then use simply:
```powershell
codacy-analyze
codacy-analyze -Tool ruff
codacy-analyze -File src/app/core/image_generator.py
```

## Timeline Estimate

- WSL Installation: 5-10 minutes + restart
- Docker Desktop Installation: 10-15 minutes
- Codacy CLI Setup: 5 minutes
- **Total**: ~30-40 minutes including restart

## Next Steps After Setup

1. Run full project analysis:

   ```powershell
   codacy-analyze
   ```

1. Fix any issues found

1. Run tests:

   ```powershell
   pytest -v
   ```

1. Commit changes:

   ```powershell
   git add .
   git commit -m "Setup Docker and Codacy CLI for code quality"
   ```

## Resources

- WSL Documentation: https://docs.microsoft.com/en-us/windows/wsl/
- Docker Desktop: https://docs.docker.com/desktop/windows/wsl/
- Codacy CLI: https://docs.codacy.com/codacy-analysis-cli/
