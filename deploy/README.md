<!--                                        [2026-03-04 14:24]  -->
<!--                                       Productivity: Active  -->

# `deploy/` — Deployment Scripts & Configurations

> **Everything needed to deploy Project-AI to any environment.** Docker, Kubernetes, bare metal, desktop, and USB — all deployment paths documented here.

## Contents

| Component | Purpose |
|---|---|
| **Docker** | Dockerfiles, docker-compose configs for containerized deployment |
| **Kubernetes** | K8s manifests, Helm chart references (see `/k8s/` and `/helm/`) |
| **Desktop** | Desktop application deployment (Windows, Linux, macOS) |
| **USB** | Portable USB installer creation (see `scripts/create_*_usb.ps1`) |
| **Python scripts** | Deployment automation, health verification, rollback |

## Deployment Paths

### 1. Development

```bash
python scripts/quickstart.py
python scripts/start_api.py
```

### 2. Docker

```bash
docker-compose up -d
```

### 3. Kubernetes

```bash
kubectl apply -f k8s/
# or
helm install project-ai helm/project-ai/
```

### 4. Desktop

```powershell
powershell scripts/install_desktop.ps1
```

### 5. USB Portable

```powershell
powershell scripts/create_universal_usb.ps1 -Drive E:
```

## Pre-Deployment Checklist

Every deployment runs the Iron Path:

1. `python scripts/validate_all_code.py`
2. `python scripts/validate_production_claims.py`
3. `python scripts/healthcheck.py`
4. `python scripts/validate_release.py`
