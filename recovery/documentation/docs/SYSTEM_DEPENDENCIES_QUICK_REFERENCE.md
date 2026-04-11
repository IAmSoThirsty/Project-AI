# System Dependencies - Quick Reference

**For**: Developers, DevOps, System Administrators  
**Last Updated**: 2026-04-09

---



## 📚 Documentation Map

| Document | Purpose | Audience |
|----------|---------|----------|
| **[SYSTEM_REQUIREMENTS.md](SYSTEM_REQUIREMENTS.md)** | User-facing installation guide with platform-specific instructions | End users, developers |
| **[SYSTEM_DEPENDENCIES_REPORT.md](SYSTEM_DEPENDENCIES_REPORT.md)** | Technical analysis of all dependencies, Docker optimization, platform compatibility | Engineers, architects |
| **[SYSTEM_DEPENDENCY_INTEGRATION_SUMMARY.md](SYSTEM_DEPENDENCY_INTEGRATION_SUMMARY.md)** | Integration report, changes made, verification steps | Project managers, QA |
| **[INSTALL.md](INSTALL.md)** | General installation guide with multiple methods | All users |

---



## 🚀 Quick Start



### I just want to install the dependencies

**Ubuntu/Debian**:
```bash
curl -fsSL https://raw.githubusercontent.com/IAmSoThirsty/Project-AI/main/scripts/install-system-deps-ubuntu.sh | bash
```

**Other platforms**: See [SYSTEM_REQUIREMENTS.md](SYSTEM_REQUIREMENTS.md)



### I want to build with Docker

```bash

# Main application

docker build -t project-ai:latest -f Dockerfile .



# Sovereign edition with eBPF

docker build -t project-ai:sovereign -f Dockerfile.sovereign .



# Test suite

docker build -t project-ai:test -f Dockerfile.test .
```



### I need to know what packages are required

See [SYSTEM_REQUIREMENTS.md](SYSTEM_REQUIREMENTS.md) for:

- Platform-specific package lists
- Hardware requirements
- Verification steps
- Troubleshooting



### I need technical details about dependencies

See [SYSTEM_DEPENDENCIES_REPORT.md](SYSTEM_DEPENDENCIES_REPORT.md) for:

- Python package → system library mapping
- Docker multi-stage build patterns
- Platform compatibility matrix
- Security hardening recommendations

---



## 📋 Common Scenarios



### Scenario 1: Fresh Ubuntu Server Install

```bash

# 1. Install system dependencies

curl -fsSL https://raw.githubusercontent.com/IAmSoThirsty/Project-AI/main/scripts/install-system-deps-ubuntu.sh | bash



# 2. Clone repository

git clone https://github.com/IAmSoThirsty/Project-AI.git
cd Project-AI



# 3. Create virtual environment

python3.11 -m venv .venv
source .venv/bin/activate



# 4. Install Python dependencies

pip install --upgrade pip
pip install -r requirements.txt



# 5. Run

python launcher.py
```



### Scenario 2: Docker Production Deployment

```bash

# 1. Build production image

docker build -t project-ai:prod -f Dockerfile .



# 2. Run with docker-compose

docker-compose up -d



# 3. Verify

docker-compose ps
docker logs project-ai-dev
```



### Scenario 3: Development on macOS

```bash

# 1. Install Homebrew (if not installed)

/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"



# 2. Install dependencies

brew install python@3.11 openssl@3 libffi jpeg zlib libtiff freetype lcms2 libwebp



# 3. Set environment variables (add to ~/.zshrc)

export PATH="/usr/local/opt/python@3.11/bin:$PATH"
export LDFLAGS="-L/usr/local/opt/openssl@3/lib -L/usr/local/opt/libffi/lib"
export CPPFLAGS="-I/usr/local/opt/openssl@3/include -I/usr/local/opt/libffi/include"



# 4. Clone and install

git clone https://github.com/IAmSoThirsty/Project-AI.git
cd Project-AI
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```



### Scenario 4: Windows Development

```powershell

# 1. Install Chocolatey (as Administrator)

Set-ExecutionPolicy Bypass -Scope Process -Force
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))



# 2. Install dependencies

choco install python311 git visualstudio2022buildtools -y
choco install visualstudio2022-workload-vctools -y



# 3. Clone and install

git clone https://github.com/IAmSoThirsty/Project-AI.git
cd Project-AI
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```



### Scenario 5: CI/CD with GitHub Actions

```yaml
name: Build and Test

on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:

      - uses: actions/checkout@v3
      
      - name: Install system dependencies
        run: |
          sudo apt-get update
          sudo apt-get install -y \
            build-essential libssl-dev libffi-dev \
            libpq-dev libjpeg-dev zlib1g-dev
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install Python dependencies
        run: |
          pip install --upgrade pip
          pip install -r requirements.txt
          pip install -r requirements-test.txt
      
      - name: Run tests
        run: pytest tests/ -v
      
      - name: Build Docker image
        run: docker build -t project-ai:${{ github.sha }} .

```

---



## 🔍 Dependency Lookup



### By Python Package

| Package | System Dependencies | See |
|---------|-------------------|-----|
| cryptography | libssl-dev, libffi-dev | [SYSTEM_DEPENDENCIES_REPORT.md](SYSTEM_DEPENDENCIES_REPORT.md#11-cryptography--security) |
| Pillow | libjpeg-dev, zlib1g-dev, etc. | [SYSTEM_DEPENDENCIES_REPORT.md](SYSTEM_DEPENDENCIES_REPORT.md#13-image--media-processing) |
| numpy/scipy | libopenblas-dev, liblapack-dev | [SYSTEM_DEPENDENCIES_REPORT.md](SYSTEM_DEPENDENCIES_REPORT.md#14-scientific--data-analysis) |
| PyQt6 | libgl1, libxkbcommon0, etc. | [SYSTEM_DEPENDENCIES_REPORT.md](SYSTEM_DEPENDENCIES_REPORT.md#15-gui--desktop) |
| psycopg2 | libpq-dev | [SYSTEM_DEPENDENCIES_REPORT.md](SYSTEM_DEPENDENCIES_REPORT.md#12-database--storage) |



### By Platform

| Platform | Package Manager | Documentation |
|----------|----------------|---------------|
| Ubuntu/Debian | apt-get | [SYSTEM_REQUIREMENTS.md § Linux (Ubuntu/Debian)](SYSTEM_REQUIREMENTS.md#linux-ubuntudebian) |
| RHEL/Fedora | dnf/yum | [SYSTEM_REQUIREMENTS.md § Linux (RHEL/Fedora)](SYSTEM_REQUIREMENTS.md#linux-rhelfedoracentos) |
| Alpine | apk | [SYSTEM_REQUIREMENTS.md § Linux (Alpine)](SYSTEM_REQUIREMENTS.md#linux-alpine) |
| macOS | brew | [SYSTEM_REQUIREMENTS.md § macOS](SYSTEM_REQUIREMENTS.md#macos) |
| Windows | choco | [SYSTEM_REQUIREMENTS.md § Windows](SYSTEM_REQUIREMENTS.md#windows) |



### By Feature

| Feature | Required Dependencies | Documentation |
|---------|---------------------|---------------|
| Core System | Python 3.11, OpenSSL, libffi | [SYSTEM_REQUIREMENTS.md](SYSTEM_REQUIREMENTS.md) |
| Database (PostgreSQL) | libpq-dev, libpq5 | [SYSTEM_DEPENDENCIES_REPORT.md § 1.2](SYSTEM_DEPENDENCIES_REPORT.md#12-database--storage) |
| Image Processing | libjpeg, zlib, libtiff, etc. | [SYSTEM_DEPENDENCIES_REPORT.md § 1.3](SYSTEM_DEPENDENCIES_REPORT.md#13-image--media-processing) |
| Machine Learning | openblas, lapack, numpy, scipy | [SYSTEM_DEPENDENCIES_REPORT.md § 1.4](SYSTEM_DEPENDENCIES_REPORT.md#14-scientific--data-analysis) |
| Desktop GUI | PyQt6, libgl1, X11 libraries | [SYSTEM_DEPENDENCIES_REPORT.md § 1.5](SYSTEM_DEPENDENCIES_REPORT.md#15-gui--desktop) |
| eBPF (OctoReflex) | clang, libbpf-dev, kernel 5.15+ | [SYSTEM_DEPENDENCIES_REPORT.md § 3.1](SYSTEM_DEPENDENCIES_REPORT.md#31-octoreflex-ebpf-security-system) |

---



## 🐛 Troubleshooting



### "error: command 'gcc' failed"

**Solution**: Install build tools
```bash

# Ubuntu/Debian

sudo apt-get install build-essential



# macOS

xcode-select --install



# Windows

choco install visualstudio2022buildtools
```



### "ImportError: libssl.so.3: cannot open shared object file"

**Solution**: Install OpenSSL runtime
```bash

# Ubuntu/Debian

sudo apt-get install libssl3



# Fedora

sudo dnf install openssl-libs
```



### "Python.h: No such file or directory"

**Solution**: Install Python development headers
```bash

# Ubuntu/Debian

sudo apt-get install python3.11-dev



# Fedora

sudo dnf install python3-devel
```



### Docker build fails with "no space left on device"

**Solution**: Clean Docker cache
```bash
docker system prune -a
docker volume prune
```



### More troubleshooting: [SYSTEM_REQUIREMENTS.md § Troubleshooting](SYSTEM_REQUIREMENTS.md#troubleshooting)

---



## 🔐 Security



### Docker Image Security

All updated Dockerfiles include:

- ✅ Multi-stage builds (smaller attack surface)
- ✅ Non-root users
- ✅ Minimal base images (python:3.11-slim)
- ✅ Pinned base images (SHA256 digests)
- ✅ No build tools in runtime images
- ✅ Health checks



### Supply Chain Security

- Base images pinned to SHA256 digests
- Wheel-based installation (verifiable builds)
- No external package repositories in runtime
- Recommend: Add Trivy security scanning to CI/CD

See [SYSTEM_DEPENDENCIES_REPORT.md § 6.3](SYSTEM_DEPENDENCIES_REPORT.md#63-security-hardening)

---



## 📊 Metrics

| Metric | Value |
|--------|-------|
| Platforms documented | 8 |
| System packages documented | 60+ |
| Python packages analyzed | 18+ |
| Dockerfiles reviewed | 17 |
| Dockerfiles updated | 3 |
| Documentation pages | 4 |
| Total documentation | ~52 KB |
| Installation scripts | 1 |

---



## 🎯 Next Steps



### For Users

1. Choose your platform
2. Follow installation guide in [SYSTEM_REQUIREMENTS.md](SYSTEM_REQUIREMENTS.md)
3. Verify installation
4. Run the application



### For Developers

1. Review [SYSTEM_DEPENDENCIES_REPORT.md](SYSTEM_DEPENDENCIES_REPORT.md) for technical details
2. Set up development environment per [SYSTEM_REQUIREMENTS.md](SYSTEM_REQUIREMENTS.md)
3. Install pre-commit hooks
4. Start developing!



### For DevOps

1. Review Docker multi-stage build patterns in [SYSTEM_DEPENDENCIES_REPORT.md § 6](SYSTEM_DEPENDENCIES_REPORT.md#6-build-optimization-recommendations)
2. Integrate Docker builds into CI/CD
3. Add security scanning (Trivy recommended)
4. Set up monitoring and alerting



### For System Administrators

1. Use automated installation script for Ubuntu/Debian
2. Customize for your infrastructure
3. Document any platform-specific modifications
4. Set up production monitoring

---



## 📞 Support

- **Documentation**: This file, [SYSTEM_REQUIREMENTS.md](SYSTEM_REQUIREMENTS.md), [SYSTEM_DEPENDENCIES_REPORT.md](SYSTEM_DEPENDENCIES_REPORT.md)
- **GitHub Issues**: https://github.com/IAmSoThirsty/Project-AI/issues
- **Installation Guide**: [INSTALL.md](INSTALL.md)

---

**Last Updated**: 2026-04-09  
**Maintained By**: System Dependency Architect  
**Version**: 1.0.0
