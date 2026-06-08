# T: Drive (Dev Drive) - Complete Command Reference
**Complete Feature Activation & Command List**

---

## 🚀 Quick Navigation to T: Drive

```powershell
# Change to T: drive
cd T:

# Or set as default location
Set-Location T:\

# Open in File Explorer
explorer T:\

# Open in Windows Terminal
wt -d T:\
```

---

## 📁 T: Drive Directory Structure Commands

### Navigate Key Directories
```powershell
# Source code repositories
cd T:\Source

# Build tools and caches
cd T:\Tools

# Active development workspace
cd T:\Dev

# Configuration files
cd T:\Config

# Development tooling
cd T:\DevTools

# DevOps configs (.aws, .azure, .docker, .kube)
cd T:\DevOps

# IDE configurations
cd T:\IDEs
```

### Create New Project Structure
```powershell
# Create new project in Source
mkdir T:\Source\my-project
cd T:\Source\my-project

# Create standard project structure
mkdir src, tests, docs, config

# Initialize git repository
git init
```

---

## 🔧 Development Tools Commands

### Node.js / JavaScript / TypeScript

```bash
# Check version
node --version
npm --version

# Create new Node project on T: drive
cd T:\Source
mkdir my-node-app && cd my-node-app
npm init -y

# Install dependencies (stored on T: for performance)
npm install express
npm install --save-dev typescript @types/node

# Install global packages to T: drive
npm config set prefix "T:\DevTools\npm-global"
npm install -g typescript ts-node nodemon

# Run development server
npm run dev
node app.js
nodemon server.js

# TypeScript compilation
tsc --init
tsc
npx ts-node src/index.ts

# Package management
npm ci                    # Clean install
npm update               # Update packages
npm outdated             # Check for updates
npm audit fix            # Fix vulnerabilities
```

### Python

```bash
# Check version
python --version
pip --version

# Create project on T: drive
cd T:\Source
mkdir my-python-app && cd my-python-app

# Create virtual environment on T: (faster I/O)
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1    # PowerShell
.\venv\Scripts\activate.bat     # CMD

# Install packages
pip install -r requirements.txt
pip install flask django fastapi
pip install requests pandas numpy

# Freeze dependencies
pip freeze > requirements.txt

# Run Python app
python app.py
python -m flask run
uvicorn main:app --reload

# Package management
pip list                  # List installed packages
pip show package-name     # Package details
pip install --upgrade pip # Update pip
```

### Go

```bash
# Check version
go version

# Set GOPATH to T: drive (already configured)
echo $env:GOPATH          # T:\DevTools\go

# Create new Go project
cd T:\Source
mkdir my-go-app && cd my-go-app
go mod init github.com/IAmSoThirsty/my-go-app

# Add dependencies
go get github.com/gin-gonic/gin
go get -u all                    # Update all

# Build and run
go build
go run main.go
go run .

# Testing
go test
go test -v
go test ./...

# Install binaries to T:\DevTools\go\bin
go install

# Cross-compile
GOOS=linux GOARCH=amd64 go build
GOOS=windows GOARCH=amd64 go build

# Module management
go mod tidy              # Clean up dependencies
go mod vendor            # Vendor dependencies
go mod download          # Download dependencies
```

### Rust / Cargo

```bash
# Check version
rustc --version
cargo --version

# Cargo home on T: drive
echo $env:CARGO_HOME     # T:\DevTools\.cargo

# Create new Rust project on T: drive
cd T:\Source
cargo new my-rust-app
cd my-rust-app

# Or create library
cargo new --lib my-rust-lib

# Build and run
cargo build              # Debug build
cargo build --release    # Optimized build
cargo run               # Build and run
cargo run --release     # Run optimized

# Testing
cargo test
cargo test --release
cargo test -- --nocapture  # Show println output

# Documentation
cargo doc --open

# Add dependencies (edit Cargo.toml or use cargo-edit)
# Example Cargo.toml:
# [dependencies]
# serde = { version = "1.0", features = ["derive"] }
# tokio = { version = "1", features = ["full"] }

# Update dependencies
cargo update

# Check for issues
cargo check
cargo clippy            # Linter
cargo fmt               # Format code

# Install cargo tools
cargo install cargo-edit
cargo install cargo-watch
cargo add package-name   # With cargo-edit
```

### .NET / C#

```bash
# Check version
dotnet --version

# Create new project on T: drive
cd T:\Source
dotnet new console -n MyApp
dotnet new webapi -n MyApi
dotnet new blazorwasm -n MyBlazorApp
dotnet new classlib -n MyLibrary

# Restore and build
dotnet restore
dotnet build
dotnet build --configuration Release

# Run
dotnet run
dotnet run --configuration Release

# Testing
dotnet test
dotnet test --logger "console;verbosity=detailed"

# Add packages
dotnet add package Newtonsoft.Json
dotnet add package Microsoft.EntityFrameworkCore

# Publish
dotnet publish -c Release -o T:\publish

# Solution management
dotnet new sln -n MySolution
dotnet sln add Project/Project.csproj
```

### Java / Gradle

```bash
# Check version
java -version
gradle --version

# Gradle home
echo $env:GRADLE_USER_HOME  # C:\Users\Quencher\.gradle

# Create new Gradle project on T: drive
cd T:\Source
mkdir my-java-app && cd my-java-app
gradle init

# Build
gradle build
gradle build --no-daemon   # Without daemon
gradle build --scan        # With build scan

# Run
gradle run

# Testing
gradle test
gradle test --tests "com.example.MyTest"

# Clean
gradle clean

# Gradle wrapper (recommended)
gradle wrapper
.\gradlew build           # Use wrapper
.\gradlew run
.\gradlew test

# Dependency management
gradle dependencies       # Show dependency tree
gradle dependencyInsight --dependency package-name
```

### Git (All Projects)

```bash
# Already configured for IAmSoThirsty
git config --global --list

# Initialize repository on T: drive
cd T:\Source\my-project
git init
git add .
git commit -m "Initial commit"

# Connect to GitHub with SSH
git remote add origin git@github.com:IAmSoThirsty/my-project.git
git push -u origin main

# Clone to T: drive
cd T:\Source
git clone git@github.com:IAmSoThirsty/repository.git

# Branches
git branch feature-name
git checkout feature-name
git checkout -b new-feature
git merge feature-name

# Status and history
git status
git log --oneline --graph --all
git diff
git show HEAD

# Stash changes
git stash
git stash pop
git stash list

# Pull/Push
git pull origin main
git push origin main
git push --force-with-lease

# Undo changes
git reset --hard HEAD
git reset --soft HEAD~1
git revert commit-hash

# SSH connection test
ssh -T git@github.com
```

---

## 🐳 Docker Commands

```bash
# Start Docker service
Start-Service com.docker.service

# Check status
docker version
docker info

# Images
docker images
docker pull image:tag
docker build -t myapp:latest .
docker rmi image:tag

# Containers
docker ps                    # Running containers
docker ps -a                 # All containers
docker run -d -p 8080:80 nginx
docker run -it ubuntu bash   # Interactive
docker stop container-id
docker rm container-id
docker logs container-id
docker exec -it container-id bash

# Docker Compose
docker-compose up -d
docker-compose down
docker-compose logs -f
docker-compose ps

# Cleanup
docker system prune
docker volume prune
docker network prune

# Save data to T: drive
docker run -v T:\Dev\data:/data myimage
```

---

## 🐧 WSL2 / Ubuntu Commands

```bash
# Enter WSL
wsl

# Or specific distro
wsl -d Ubuntu

# Run command from Windows
wsl ls -la
wsl python3 script.py

# Access T: drive from WSL
cd /mnt/t

# Update Ubuntu
sudo apt update
sudo apt upgrade

# Install development tools
sudo apt install build-essential
sudo apt install git curl wget
sudo apt install python3-pip
sudo apt install nodejs npm

# Exit WSL
exit

# Stop WSL
wsl --shutdown

# List distributions
wsl --list --verbose
```

---

## 🎨 Windows Terminal Commands

```powershell
# Open new tab in specific profile
wt -p "PowerShell"
wt -p "Ubuntu"
wt -p "Admin Dev Drive (T:\)"

# Open in specific directory
wt -d T:\Source

# Split panes
wt ; split-pane -p "Ubuntu"
wt ; split-pane -H -p "PowerShell"

# Multiple tabs
wt -p PowerShell ; new-tab -p Ubuntu
```

---

## 💾 Dev Drive Specific Features

### ReFS Performance Features

```powershell
# Check Dev Drive info
Get-Volume -DriveLetter T

# View ReFS features
fsutil fsinfo volumeinfo T:

# Check integrity
Get-FileIntegrity T:\

# Enable/disable integrity for specific files (optional)
Set-FileIntegrity -FileName "T:\file.txt" -Enable $true

# Compact mode (ReFS automatic)
compact /c /s:T:\folder    # Compression if needed
```

### Dev Drive Performance Optimization

```powershell
# Verify Dev Drive is recognized
Get-Volume T | Select-Object FileSystemType, DriveType

# Dev Drive automatically excludes from Defender
# Verify exclusion
Get-MpPreference | Select-Object -ExpandProperty ExclusionPath | Where-Object { $_ -like "T:\*" }

# Check if running on Dev Drive (ReFS indicator)
fsutil fsinfo driveType T:

# Performance mode is automatic on Dev Drive
# No manual activation needed - benefits include:
# - Automatic Defender exclusion
# - Optimized file system operations
# - Better build performance
# - Faster I/O operations
```

### Monitor Dev Drive Performance

```powershell
# Watch disk I/O
Get-Counter "\PhysicalDisk(*T:*)\Disk Bytes/sec"

# Check disk queue
Get-Counter "\PhysicalDisk(*T:*)\Avg. Disk Queue Length"

# Monitor specific folder size
Get-ChildItem T:\Source -Recurse | Measure-Object -Property Length -Sum

# Find large files
Get-ChildItem T:\ -Recurse -File | 
    Where-Object { $_.Length -gt 100MB } | 
    Sort-Object Length -Descending | 
    Select-Object FullName, @{N="SizeMB";E={[math]::Round($_.Length/1MB, 2)}}
```

---

## 🔐 Security & Access Control

```powershell
# View permissions on T: drive
Get-Acl T:\ | Format-List

# Set permissions for folder
$acl = Get-Acl "T:\Source"
$permission = "BUILTIN\Users","FullControl","ContainerInherit,ObjectInherit","None","Allow"
$accessRule = New-Object System.Security.AccessControl.FileSystemAccessRule $permission
$acl.SetAccessRule($accessRule)
Set-Acl "T:\Source" $acl

# Verify SSH key
ssh -T git@github.com

# Add new SSH key to agent
ssh-add C:\Users\Quencher\.ssh\id_ed25519

# List SSH keys
ssh-add -l
```

---

## 📊 System Monitoring & Optimization

```powershell
# Check overall disk space
Get-PSDrive -PSProvider FileSystem | 
    Select-Object Name, 
        @{N="Used(GB)";E={[math]::Round($_.Used/1GB,2)}}, 
        @{N="Free(GB)";E={[math]::Round($_.Free/1GB,2)}}

# Monitor memory usage
Get-Process | Sort-Object -Property WS -Descending | Select-Object -First 10

# Check CPU usage
Get-Process | Sort-Object CPU -Descending | Select-Object -First 10 -Property Name, CPU

# System uptime
(Get-Date) - (Get-CimInstance Win32_OperatingSystem).LastBootUpTime

# Clean temp files (maintain performance)
Remove-Item $env:TEMP\* -Recurse -Force -ErrorAction SilentlyContinue
```

---

## 🛠️ Build & Compilation Shortcuts

### Fast Build Commands (Using T: Drive Performance)

```powershell
# Node.js
cd T:\Source\my-app
npm ci && npm run build

# Python
cd T:\Source\my-app
pip install -r requirements.txt && python setup.py build

# Go
cd T:\Source\my-app
go build -o T:\Dev\bin\app.exe

# Rust (release mode on T: for speed)
cd T:\Source\my-app
cargo build --release --target-dir T:\Dev\target

# .NET
cd T:\Source\my-app
dotnet build -c Release -o T:\Dev\bin

# Gradle
cd T:\Source\my-app
.\gradlew build --build-cache
```

---

## 🔄 Backup & Sync Commands

```powershell
# Backup T:\Source to OneDrive
robocopy T:\Source "$env:OneDrive\Dev-Backup\Source" /MIR /Z /R:3

# Sync specific project
robocopy T:\Source\my-project E:\Backup\my-project /MIR

# Create archive
Compress-Archive -Path T:\Source\my-project -DestinationPath T:\Backups\my-project.zip

# Extract archive
Expand-Archive -Path T:\Backups\my-project.zip -DestinationPath T:\Source\

# Git backup all repos
cd T:\Source
Get-ChildItem -Directory | ForEach-Object {
    cd $_.FullName
    if (Test-Path .git) {
        Write-Host "Backing up $($_.Name)"
        git push --all
    }
    cd ..
}
```

---

## 🎯 IDE & Editor Commands

### Visual Studio Code

```bash
# Open T: drive in VS Code
code T:\

# Open specific project
code T:\Source\my-project

# Open with specific workspace
code T:\Source\my-project\workspace.code-workspace

# Install extensions
code --install-extension ms-python.python
code --install-extension golang.go
code --install-extension rust-lang.rust-analyzer

# List extensions
code --list-extensions
```

### Cursor IDE

```bash
# Open in Cursor (similar to VS Code)
cursor T:\Source\my-project

# Or launch from Start Menu
# "Cursor" application
```

---

## 📦 Package Manager Shortcuts

```powershell
# Update all Node.js global packages
npm update -g

# Update all Python packages
pip list --outdated
pip install --upgrade pip setuptools wheel

# Update Rust toolchain
rustup update

# Update all Cargo packages
cargo install-update -a

# Update .NET tools
dotnet tool list -g
dotnet tool update -g <tool-name>

# Update WSL
wsl --update
```

---

## 🚀 Quick Project Starters

### Full-Stack Web Application

```bash
# Frontend (React)
cd T:\Source
npx create-react-app my-frontend
cd my-frontend
npm start

# Backend (Node.js/Express)
mkdir T:\Source\my-backend && cd T:\Source\my-backend
npm init -y
npm install express cors dotenv
```

### Python FastAPI

```bash
cd T:\Source
mkdir my-api && cd my-api
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install fastapi uvicorn
# Create main.py
uvicorn main:app --reload
```

### Go Web Server

```bash
cd T:\Source
mkdir my-go-server && cd my-go-server
go mod init myserver
go get github.com/gin-gonic/gin
# Create main.go
go run main.go
```

### Rust CLI Tool

```bash
cd T:\Source
cargo new my-cli-tool
cd my-cli-tool
cargo add clap --features derive
cargo run
```

---

## 💡 Pro Tips for T: Drive Development

### 1. Always Use T: for Active Development
```powershell
# Benefits:
# - 68% faster compilation (ReFS + Defender exclusion)
# - Better I/O performance
# - Automatic Defender bypass
# - Optimized for development workloads
```

### 2. Leverage the Directory Structure
```powershell
T:\Source       # Active projects
T:\Dev          # Build outputs, binaries
T:\Tools        # Shared build tools
T:\DevTools     # Language toolchains
T:\Config       # Shared configs
```

### 3. Use Environment Variables
```powershell
$env:PROJECT_ROOT = "T:\Source\my-project"
$env:BUILD_OUTPUT = "T:\Dev\build"
```

### 4. Automated Workflows
```powershell
# Create build script: build.ps1
cd T:\Source\my-project
npm ci
npm run build
Copy-Item -Path dist\* -Destination T:\Dev\my-project\ -Recurse
```

---

## 🔧 Troubleshooting Commands

```powershell
# Check if T: drive is mounted
Test-Path T:\

# Remount Dev Drive
.\Mount-DevDrive.ps1

# Check ReFS health
Repair-Volume -DriveLetter T -Scan

# Verify permissions
Get-Acl T:\ | Format-List

# Clear build caches
Remove-Item T:\cache\* -Recurse -Force
Remove-Item T:\Tools\.gradle\caches -Recurse -Force
Remove-Item T:\DevTools\.cargo\registry\cache -Recurse -Force

# Restart development services
Restart-Service com.docker.service
wsl --shutdown && wsl
```

---

## 📚 Quick Reference Card

```
NAVIGATE:    cd T:\Source
CREATE:      mkdir T:\Source\project && cd T:\Source\project
GIT INIT:    git init && git remote add origin git@github.com:IAmSoThirsty/repo.git
NODE:        npm init -y && npm install
PYTHON:      python -m venv venv && .\venv\Scripts\Activate.ps1
GO:          go mod init && go get
RUST:        cargo new project && cd project
BUILD:       npm run build / cargo build --release / go build
RUN:         npm start / cargo run / go run . / python app.py
TEST:        npm test / cargo test / go test / pytest
DOCKER:      docker-compose up -d
WSL:         wsl
VSCODE:      code T:\Source\project
MONITOR:     Get-Volume T | Select FileSystem, Size, SizeRemaining
```

---

**All features on T: Drive are automatically activated due to:**
1. ✅ ReFS file system (performance optimized)
2. ✅ Windows Defender auto-exclusion (faster builds)
3. ✅ Proper tool configuration (GOPATH, CARGO_HOME, etc.)
4. ✅ All development tools installed and configured
5. ✅ Git & SSH ready for GitHub

**Ready to use immediately - no additional activation needed!** 🚀
