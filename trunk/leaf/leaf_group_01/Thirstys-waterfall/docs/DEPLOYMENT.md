<!-- # ============================================================================ # -->
<!-- # STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59 # -->
<!-- # COMPLIANCE: Sovereign Substrate / DEPLOYMENT.md # -->
<!-- # ============================================================================ # -->
<!-- # ============================================================================ #


<!-- # COMPLIANCE: Sovereign Substrate / DEPLOYMENT.md # -->
<!-- # ============================================================================ #

<!-- # Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master -->
<div align="right">
  <img src="https://img.shields.io/badge/DATE-2026-03-18-blueviolet?style=for-the-badge" alt="Date" />
  <img src="https://img.shields.io/badge/PRODUCTIVITY-ACTIVE-success?style=for-the-badge" alt="Productivity" />
</div>

# Deployment Guide

Complete guide for deploying Thirstys Waterfall in production environments.

## Table of Contents

- [Quick Start](#quick-start)
- [Installation Methods](#installation-methods)
- [Docker Deployment](#docker-deployment)
- [PyPI Installation](#pypi-installation)
- [Configuration](#configuration)
- [Production Deployment](#production-deployment)
- [Monitoring & Maintenance](#monitoring--maintenance)
- [Troubleshooting](#troubleshooting)

## Quick Start

### Linux/macOS

```bash

# Clone repository

git clone https://github.com/IAmSoThirsty/Thirstys-waterfall.git
cd Thirstys-waterfall

# Run installer

bash install.sh

# Start the system

thirstys-waterfall --start
```

### Windows

```batch

# Clone repository

git clone https://github.com/IAmSoThirsty/Thirstys-waterfall.git
cd Thirstys-waterfall

# Run installer

install.bat

# Start the system

thirstys-waterfall --start
```

### Docker

```bash

# Using Docker Compose (recommended)

docker-compose up -d

# Or build and run directly

docker build -t thirstys-waterfall .
docker run -d --name thirstys-waterfall \
  --cap-add NET_ADMIN \
  --cap-add NET_RAW \
  -v thirstys_data:/home/thirsty/.thirstys_waterfall \
  thirstys-waterfall
```

## Installation Methods

### Method 1: From PyPI (Recommended for Users)

```bash

# Install from PyPI

pip install thirstys-waterfall

# Verify installation

thirstys-waterfall --help
```

### Method 2: From Source (Recommended for Development)

```bash

# Clone repository

git clone https://github.com/IAmSoThirsty/Thirstys-waterfall.git
cd Thirstys-waterfall

# Install in development mode

pip install -e .

# Or use the installer script

bash install.sh  # Linux/macOS
install.bat      # Windows
```

### Method 3: From Release Archive

```bash

# Download latest release

wget https://github.com/IAmSoThirsty/Thirstys-waterfall/archive/refs/tags/v1.0.0.tar.gz

# Extract

tar -xzf v1.0.0.tar.gz
cd Thirstys-waterfall-1.0.0

# Install

pip install .
```

## Docker Deployment

### Prerequisites

- Docker 20.10+
- Docker Compose 2.0+ (optional, but recommended)

### Using Docker Compose (Recommended)

1. **Create configuration directory:**

```bash
mkdir -p config
cp .env.example .env
```

2. **Edit `.env` file with your configuration**

3. **Start services:**

```bash
docker-compose up -d
```

4. **Check status:**

```bash
docker-compose ps
docker-compose logs -f thirstys-waterfall
```

5. **Stop services:**

```bash
docker-compose down
```

### Using Docker Directly

1. **Build image:**

```bash
docker build -t thirstys-waterfall:latest .
```

2. **Run container:**

```bash
docker run -d \
  --name thirstys-waterfall \
  --restart unless-stopped \
  --cap-add NET_ADMIN \
  --cap-add NET_RAW \
  -e THIRSTYS_ENV=production \
  -v thirstys_data:/home/thirsty/.thirstys_waterfall \
  -v $(pwd)/config:/app/config:ro \
  -p 8080:8080 \
  thirstys-waterfall:latest
```

3. **Check status:**

```bash
docker ps
docker logs thirstys-waterfall
```

### Docker Security Best Practices

The Docker image includes several security features:

- **Non-root user**: Container runs as user `thirsty` (UID 1000)
- **Minimal base image**: Uses `python:3.11-slim`
- **Multi-stage build**: Reduces image size and attack surface
- **Security options**: `no-new-privileges` enabled
- **Resource limits**: CPU and memory limits defined
- **Health checks**: Automatic health monitoring

## PyPI Installation

### For End Users

```bash

# Install latest stable version

pip install thirstys-waterfall

# Install with development dependencies

pip install thirstys-waterfall[dev]

# Install specific version

pip install thirstys-waterfall==1.0.0

# Upgrade to latest version

pip install --upgrade thirstys-waterfall
```

### For Developers

```bash

# Clone repository

git clone https://github.com/IAmSoThirsty/Thirstys-waterfall.git
cd Thirstys-waterfall

# Install in editable mode with dev dependencies

pip install -e ".[dev]"
```

## Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Key configuration variables:

```bash

# Environment

THIRSTYS_ENV=production

# Privacy Settings

THIRSTYS_PRIVACY_MODE=maximum
THIRSTYS_KILL_SWITCH=true

# VPN Settings

THIRSTYS_VPN_ENABLED=true
THIRSTYS_VPN_MULTI_HOP=true
THIRSTYS_VPN_HOP_COUNT=3

# Browser Settings

THIRSTYS_BROWSER_INCOGNITO=true
THIRSTYS_BROWSER_NO_HISTORY=true
THIRSTYS_BROWSER_NO_CACHE=true
THIRSTYS_BROWSER_NO_COOKIES=true
```

### Configuration File

Create `config/production.json`:

```json
{
  "global": {
    "privacy_mode": "maximum",
    "kill_switch_enabled": true
  },
  "vpn": {
    "enabled": true,
    "multi_hop": true,
    "hop_count": 3,
    "kill_switch": true
  },
  "browser": {
    "incognito_mode": true,
    "no_history": true,
    "no_cache": true,
    "no_cookies": true
  },
  "firewalls": {
    "enabled": true,
    "types": ["packet_filter", "stateful", "proxy", "ngfw"]
  }
}
```

## Production Deployment

### System Requirements

**Minimum:**

- CPU: 2 cores
- RAM: 2 GB
- Disk: 10 GB
- OS: Linux, Windows 10+, macOS 11+
- Python: 3.8+

**Recommended:**

- CPU: 4 cores
- RAM: 4 GB
- Disk: 20 GB
- Python: 3.11+

### Platform-Specific Requirements

#### Linux

```bash

# Install system dependencies

sudo apt-get update
sudo apt-get install -y \
  wireguard-tools \
  openvpn \
  nftables \
  strongswan \
  ca-certificates
```

#### Windows

- Download [WireGuard for Windows](https://www.wireguard.com/install/)
- Download [OpenVPN for Windows](https://openvpn.net/community-downloads/)
- Windows Firewall is built-in

#### macOS

```bash

# Install dependencies via Homebrew

brew install wireguard-tools openvpn

# macOS PF (Packet Filter) is built-in

```

### Systemd Service (Linux)

Create `/etc/systemd/system/thirstys-waterfall.service`:

```ini
[Unit]
Description=Thirstys Waterfall Privacy System
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=thirsty
Group=thirsty
WorkingDirectory=/opt/thirstys-waterfall
Environment="THIRSTYS_ENV=production"
EnvironmentFile=/opt/thirstys-waterfall/.env
ExecStart=/usr/local/bin/thirstys-waterfall --start
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

# Security hardening

NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/thirstys-waterfall

# Capabilities for VPN and firewall

AmbientCapabilities=CAP_NET_ADMIN CAP_NET_RAW

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable thirstys-waterfall
sudo systemctl start thirstys-waterfall
sudo systemctl status thirstys-waterfall
```

### Windows Service

Use [NSSM](https://nssm.cc/) (Non-Sucking Service Manager):

```batch

# Install NSSM

choco install nssm

# Install service

nssm install ThirstysWaterfall "C:\Python311\Scripts\thirstys-waterfall.exe" "--start"
nssm set ThirstysWaterfall AppDirectory "C:\ThirstysWaterfall"
nssm set ThirstysWaterfall AppEnvironmentExtra THIRSTYS_ENV=production

# Start service

nssm start ThirstysWaterfall
```

### Kubernetes Deployment

Example `deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: thirstys-waterfall
spec:
  replicas: 1
  selector:
    matchLabels:
      app: thirstys-waterfall
  template:
    metadata:
      labels:
        app: thirstys-waterfall
    spec:
      containers:

      - name: thirstys-waterfall

        image: thirstys-waterfall:latest
        env:

        - name: THIRSTYS_ENV

          value: "production"
        securityContext:
          capabilities:
            add:

            - NET_ADMIN
            - NET_RAW

          runAsNonRoot: true
          runAsUser: 1000
        volumeMounts:

        - name: config

          mountPath: /app/config
          readOnly: true

        - name: data

          mountPath: /home/thirsty/.thirstys_waterfall
      volumes:

      - name: config

        configMap:
          name: thirstys-config

      - name: data

        persistentVolumeClaim:
          claimName: thirstys-data-pvc
```

## Monitoring & Maintenance

### Health Checks

```bash

# Check system status

thirstys-waterfall --status

# Check VPN status

python -c "from thirstys_waterfall import ThirstysWaterfall; w = ThirstysWaterfall(); print(w.get_status())"

# Docker health check

docker inspect --format='{{.State.Health.Status}}' thirstys-waterfall
```

### Logging

**Application logs:**

```bash

# Docker logs

docker logs -f thirstys-waterfall

# Systemd logs

journalctl -u thirstys-waterfall -f

# File logs

tail -f /var/log/thirstys-waterfall.log
```

### Metrics

Monitor these metrics:

- VPN connection status
- Firewall rule counts
- Active browser sessions
- Memory usage
- CPU usage
- Network throughput

### Backup

**Important files to backup:**

```bash

# Configuration

/opt/thirstys-waterfall/.env
/opt/thirstys-waterfall/config/

# Data (if persistent storage is used)

/home/thirsty/.thirstys_waterfall/

# Docker volumes

docker run --rm -v thirstys_data:/data -v $(pwd):/backup \
  alpine tar czf /backup/thirstys-backup.tar.gz -C /data .
```

### Updates

**PyPI installation:**

```bash
pip install --upgrade thirstys-waterfall
```

**Docker:**

```bash
docker-compose pull
docker-compose up -d
```

**From source:**

```bash
cd Thirstys-waterfall
git pull
pip install --upgrade -e .
```

## Troubleshooting

### Common Issues

#### 1. VPN not connecting

```bash

# Check VPN backends

python -c "from thirstys_waterfall.vpn.backends import VPNBackendFactory; print(VPNBackendFactory.get_available_backends())"

# Check logs

journalctl -u thirstys-waterfall | grep VPN
```

#### 2. Firewall rules not applying

```bash

# Check firewall backends

python -c "from thirstys_waterfall.firewalls.backends import FirewallBackendFactory; print(FirewallBackendFactory.get_available_backends())"

# Verify permissions

sudo -v  # Should have sudo access for firewall operations
```

#### 3. Docker container not starting

```bash

# Check logs

docker logs thirstys-waterfall

# Check capabilities

docker inspect thirstys-waterfall | grep -A 10 CapAdd

# Verify volumes

docker volume ls | grep thirstys
```

#### 4. Import errors

```bash

# Verify installation

pip show thirstys-waterfall

# Reinstall

pip uninstall thirstys-waterfall
pip install thirstys-waterfall
```

### Getting Help

- **Documentation**: [README.md](../README.md)
- **Issues**: [GitHub Issues](https://github.com/IAmSoThirsty/Thirstys-waterfall/issues)
- **Security**: [SECURITY.md](../SECURITY.md)
- **Examples**: [examples/](../examples/)

## Production Checklist

Before deploying to production:

- [ ] Configuration file reviewed and secured
- [ ] Environment variables set correctly
- [ ] Platform-specific dependencies installed
- [ ] VPN backends available and tested
- [ ] Firewall backends available and tested
- [ ] Health checks configured
- [ ] Logging configured
- [ ] Monitoring configured
- [ ] Backup strategy implemented
- [ ] Update procedure documented
- [ ] Security hardening applied
- [ ] Resource limits configured
- [ ] High availability considered
- [ ] Disaster recovery plan in place

## Security Considerations

1. **Never commit secrets**: Use environment variables or secret managers
2. **Run as non-root**: Always use unprivileged users
3. **Update regularly**: Keep dependencies up to date
4. **Monitor logs**: Watch for suspicious activity
5. **Use HTTPS**: For any web interfaces
6. **Firewall rules**: Restrict access to management ports
7. **Audit regularly**: Review security settings periodically

## Performance Tuning

### Docker

```yaml

# docker-compose.yml optimizations

deploy:
  resources:
    limits:
      cpus: '4.0'
      memory: 4G
    reservations:
      cpus: '2.0'
      memory: 2G
```

### System

```bash

# Increase file descriptors

ulimit -n 65536

# Tune network parameters

sysctl -w net.core.rmem_max=26214400
sysctl -w net.core.wmem_max=26214400
```

## License

MIT License - See [LICENSE](../LICENSE) file

---

**Built with 🔒 by the Thirsty Security Team**
