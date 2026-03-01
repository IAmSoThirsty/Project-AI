# Installation Guide - Project-AI

## 📦 Installation Methods

Project-AI can be installed using multiple methods depending on your platform and preferences:

1. **[Quick Install (Recommended)](#quick-install)** - One-command installation
2. **[Pre-built Binaries](#pre-built-binaries)** - Download and run
3. **[Package Managers](#package-managers)** - System package managers
4. **[Docker](#docker)** - Containerized deployment
5. **[From Source](#from-source)** - Build yourself
6. **[Python Package](#python-package)** - Install via pip

---

## 🚀 Quick Install

### Windows

**Option 1: PowerShell (Recommended)**

```powershell

# Run as Administrator

irm https://raw.githubusercontent.com/IAmSoThirsty/Project-AI/main/scripts/install-windows.ps1 | iex
```

**Option 2: Download Installer**

1. Download the latest [Windows Installer (.exe)](https://github.com/IAmSoThirsty/Project-AI/releases/latest)
2. Run the installer
3. Follow the setup wizard

### macOS

**Option 1: Homebrew (Recommended)**

```bash
brew tap iamsothirsty/project-ai
brew install project-ai
```

**Option 2: Download DMG**

1. Download the latest [macOS DMG](https://github.com/IAmSoThirsty/Project-AI/releases/latest)
2. Open the DMG file
3. Drag Project-AI to Applications folder

**Option 3: One-line Install**

```bash
curl -fsSL https://raw.githubusercontent.com/IAmSoThirsty/Project-AI/main/scripts/install-macos.sh | bash
```

### Linux

**Option 1: Universal Script**

```bash
curl -fsSL https://raw.githubusercontent.com/IAmSoThirsty/Project-AI/main/scripts/install-linux.sh | bash
```

**Option 2: Distribution Packages**

**Ubuntu/Debian:**

```bash
wget https://github.com/IAmSoThirsty/Project-AI/releases/latest/download/project-ai_1.0.0_amd64.deb
sudo dpkg -i project-ai_1.0.0_amd64.deb
```

**Fedora/RHEL/CentOS:**

```bash
sudo dnf install https://github.com/IAmSoThirsty/Project-AI/releases/latest/download/project-ai-1.0.0.x86_64.rpm
```

**Arch Linux:**

```bash
yay -S project-ai

# or

paru -S project-ai
```

**Option 3: AppImage (Universal)**

```bash
wget https://github.com/IAmSoThirsty/Project-AI/releases/latest/download/ProjectAI-x86_64.AppImage
chmod +x ProjectAI-x86_64.AppImage
./ProjectAI-x86_64.AppImage
```

**Option 4: Snap**

```bash
sudo snap install project-ai
```

**Option 5: Flatpak**

```bash
flatpak install flathub com.projectai.ProjectAI
```

### Android

1. Download the latest [Android APK](https://github.com/IAmSoThirsty/Project-AI/releases/latest)
2. Enable "Install from Unknown Sources" in Settings
3. Install the APK
4. Grant necessary permissions

Or install from Google Play Store (coming soon).

---

## 📥 Pre-built Binaries

Download pre-built binaries from the [GitHub Releases page](https://github.com/IAmSoThirsty/Project-AI/releases/latest):

### Windows

- `ProjectAI-1.0.0-windows-x86_64.zip` - Portable ZIP archive
- `ProjectAI-1.0.0-windows-x86_64.exe` - Installer executable
- `ProjectAI-1.0.0-windows-x86_64.msi` - MSI installer

### macOS

- `ProjectAI-1.0.0-macos.dmg` - DMG disk image
- `ProjectAI-1.0.0-macos-universal.tar.gz` - Universal binary (Intel + Apple Silicon)

### Linux

- `ProjectAI-1.0.0-linux-x86_64.tar.gz` - Tarball
- `project-ai_1.0.0_amd64.deb` - Debian/Ubuntu package
- `project-ai-1.0.0.x86_64.rpm` - Fedora/RHEL package
- `ProjectAI-x86_64.AppImage` - AppImage (universal)
- `project-ai-1.0.0.tar.xz` - Source archive

### Verification

All releases include checksums and GPG signatures:

```bash

# Verify checksum

sha256sum -c ProjectAI-1.0.0-linux-x86_64.tar.gz.sha256

# Verify GPG signature

gpg --verify ProjectAI-1.0.0-linux-x86_64.tar.gz.asc
```

---

## 📦 Package Managers

### Windows

**Chocolatey:**

```powershell
choco install project-ai
```

**Scoop:**

```powershell
scoop bucket add project-ai https://github.com/IAmSoThirsty/scoop-project-ai
scoop install project-ai
```

**WinGet:**

```powershell
winget install IAmSoThirsty.ProjectAI
```

### macOS

**Homebrew:**

```bash
brew install project-ai
```

**MacPorts:**

```bash
sudo port install project-ai
```

### Linux

**Ubuntu/Debian (APT):**

```bash

# Add repository

curl -fsSL https://repo.projectai.dev/gpg | sudo apt-key add -
echo "deb https://repo.projectai.dev/apt stable main" | sudo tee /etc/apt/sources.list.d/project-ai.list

# Install

sudo apt update
sudo apt install project-ai
```

**Fedora/RHEL (DNF):**

```bash

# Add repository

sudo dnf config-manager --add-repo https://repo.projectai.dev/rpm/project-ai.repo

# Install

sudo dnf install project-ai
```

**Arch Linux (AUR):**

```bash
yay -S project-ai

# or

paru -S project-ai

# or

makepkg -si  # from AUR directory
```

**Snap:**

```bash
sudo snap install project-ai
```

**Flatpak:**

```bash
flatpak install flathub com.projectai.ProjectAI
flatpak run com.projectai.ProjectAI
```

---

## 🐳 Docker

### Quick Start

```bash

# Pull the image

docker pull ghcr.io/iamsothirsty/project-ai:latest

# Run with defaults

docker run -d -p 5000:5000 ghcr.io/iamsothirsty/project-ai:latest

# Run with custom configuration

docker run -d \
  -p 5000:5000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/.env:/app/.env \
  ghcr.io/iamsothirsty/project-ai:latest
```

### Docker Compose

```bash

# Clone repository

git clone https://github.com/IAmSoThirsty/Project-AI.git
cd Project-AI

# Start all services

docker-compose up -d

# Access at http://localhost:5000

```

See [Docker Documentation](docker/README.md) for advanced configuration.

---

## 🔧 From Source (Sovereign Build)

### Prerequisites

- **Python**: 3.11+ (Hardened toolchain)
- **Node.js**: 18+ (LTS recommended)
- **Git**: 2.40+ (Signed commits supported)
- **Kernel**: 5.15+ with eBPF support (Required for Tier 0 OctoReflex)
- **HSM/TPM**: Optional but recommended for Sovereign Master Key

### Installation Steps

```bash

# 1. Clone repository

git clone https://github.com/IAmSoThirsty/Project-AI.git
cd Project-AI

# 2. Create virtual environment

python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install dependencies

pip install -e .

# 4. Configure environment

cp .env.example .env

# Edit .env with your settings

# 5. Run application

python -m src.app.main
```

### Building Executable

To create a standalone executable:

```bash

# Linux/macOS

./build-installer.sh

# Windows

.\build-installer.ps1
```

The executable will be in the `dist/` directory.

---

## 🐍 Python Package

### Install from PyPI

```bash
pip install project-ai
```

### Install development version

```bash
pip install git+https://github.com/IAmSoThirsty/Project-AI.git
```

### Usage

```python

# In Python

from project_ai import ProjectAI

app = ProjectAI()
app.run()
```

Or via command line:

```bash
project-ai
```

---

## ⚙️ Configuration

### First Run Setup

On first run, Project-AI will:

1. Create data directory: `~/.project-ai/data`
2. Generate default configuration
3. Prompt for API keys (optional)

### Required API Keys (Optional)

For full functionality, configure:

```bash

# .env file

OPENAI_API_KEY=sk-...        # For AI features
HUGGINGFACE_API_KEY=hf_...   # For image generation
```

### Configuration File

Edit `~/.project-ai/config.json`:

```json
{
  "app_env": "production",
  "log_level": "INFO",
  "api_port": 5000,
  "enable_web_ui": true
}
```

---

## 🔧 Troubleshooting

### Windows

**Issue: "Python not found"**

```powershell

# Install Python from Microsoft Store

winget install Python.Python.3.11
```

**Issue: "Permission denied"**

```powershell

# Run PowerShell as Administrator

Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### macOS

**Issue: "Developer cannot be verified"**

```bash

# Remove quarantine attribute

xattr -d com.apple.quarantine /Applications/ProjectAI.app
```

**Issue: "Command not found"**

```bash

# Add to PATH

echo 'export PATH="/usr/local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### Linux

**Issue: "Permission denied"**

```bash

# Make executable

chmod +x ProjectAI-x86_64.AppImage
```

**Issue: "Missing dependencies"**

```bash

# Ubuntu/Debian

sudo apt install python3-pyqt6 python3-pip

# Fedora

sudo dnf install python3-qt6 python3-pip
```

### Common Issues

**Issue: "Module not found"**

```bash

# Reinstall dependencies

pip install --force-reinstall -e .
```

**Issue: "Database error"**

```bash

# Reset database

rm -rf ~/.project-ai/data/*.db
```

**Issue: "Port already in use"**

```bash

# Change port in config

export API_PORT=5001
```

---

## 🆘 Getting Help

- **Documentation**: <https://docs.projectai.dev>
- **GitHub Issues**: <https://github.com/IAmSoThirsty/Project-AI/issues>
- **Discord**: <https://discord.gg/projectai>
- **Email**: <support@projectai.dev>

---

## 📄 License

Project-AI is released under the MIT License. See [LICENSE](../LICENSE) for details.

---

## 🔄 Updating

### Package Manager

```bash

# Windows

choco upgrade project-ai

# macOS

brew upgrade project-ai

# Linux

sudo apt update && sudo apt upgrade project-ai
```

### Manual Update

```bash

# Download latest release

# Extract and replace files

# Or run install script again

```

### Docker

```bash
docker pull ghcr.io/iamsothirsty/project-ai:latest
docker-compose pull
docker-compose up -d
```

---

## 🗑️ Uninstallation

### Windows

```powershell

# Via Control Panel > Add/Remove Programs

# Or via package manager

choco uninstall project-ai
```

### macOS

```bash

# Drag from Applications to Trash

# Or via package manager

brew uninstall project-ai
```

### Linux

```bash

# Ubuntu/Debian

sudo apt remove project-ai

# Fedora

sudo dnf remove project-ai

# Remove data (optional)

rm -rf ~/.project-ai
```

---

**Next Steps**: See [Quick Start Guide](QUICKSTART.md) for usage instructions.
