---
title: Docker Build System
type: technical-guide
audience: [devops, developers]
classification: P0-Core
tags: [docker, containers, deployment]
created: 2024-01-20
status: current
---

# Docker Build System

**Containerized build and deployment with Docker Compose.**

## Docker Images

Build Project-AI Docker image:
```bash
docker build -t project-ai:latest .
```

## Docker Compose

Start all services:
```bash
docker-compose up -d
```

Services defined:
- cerberus - Orchestrator service
- monolith - Guardian service

## Multi-Stage Builds

Dockerfile uses multi-stage builds for optimization:
1. Builder stage - Install dependencies
2. Runtime stage - Minimal production image

## Health Checks

Built-in health checks every 30s:
```bash
docker-compose ps
```

---

**AGENT-038: CLI & Automation Documentation Specialist**
