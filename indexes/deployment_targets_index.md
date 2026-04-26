# Deployment Targets Index

> **📍 Location**: `indexes/deployment_targets_index.md`  
> **🎯 Purpose**: Index of all deployment platforms and topologies  
> **👥 Audience**: DevOps, platform engineers  
> **🔄 Status**: Production-Ready ✓

---

## 🚀 Deployment Platforms

| Platform | Topology | Resources | Time to Deploy | Use Case | Documentation |
|----------|----------|-----------|----------------|----------|---------------|
| **Local Desktop** | Single machine | 2GB RAM, 1 CPU | 5 min | Development/PoC | [[DESKTOP_APP_QUICKSTART.md|Guide]] |
| **Docker** | Containers | 4GB RAM, 2 CPU | 10 min | Testing/Staging | [[docker-compose.yml|Compose]] |
| **Kubernetes** | Orchestrated cluster | 8GB+ RAM, 4+ CPU | 30 min | Production | [[docs/developer/KUBERNETES_MONITORING_GUIDE.md|K8s Guide]] |
| **AWS** | Cloud platform | Variable | 60 min | Enterprise | [[web/DEPLOYMENT.md|Web Deployment]] |
| **Azure** | Cloud platform | Variable | 60 min | Enterprise | [[web/DEPLOYMENT.md|Web Deployment]] |
| **GCP** | Cloud platform | Variable | 60 min | Enterprise | [[web/DEPLOYMENT.md|Web Deployment]] |

---

## 🏗️ Platform Tiers

| Tier | Components | Infrastructure | Documentation |
|------|------------|----------------|---------------|
| **God Tier** | Temporal, MCP, Agents, Monitoring | Kubernetes cluster | [[docs/PLATFORM_TIERS.md|Platform Tiers]] |
| **Situational Tier** | Flask API, Authentication, Rate Limiting | Server/containers | [[docs/TIER2_TIER3_INTEGRATION.md|Integration]] |
| **Local Tier** | PyQt6 Desktop, Core AI, JSON persistence | Laptop/desktop | [[DESKTOP_APP_QUICKSTART.md|Quickstart]] |

---

## 📋 Metadata

```yaml
---
title: "Deployment Targets Index"
type: index
category: deployment
audience: [devops, platform-engineers]
status: production
version: 1.0.0
created: 2025-01-20
tags:
  - index
  - deployment
  - platforms
  - infrastructure
---
```

---

**Status**: Production-Ready ✓
