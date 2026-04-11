# Docker Operations Runbook

## Purpose

Operational procedures for Docker-based deployments using Docker Compose, including container management, build workflows, registry operations, and troubleshooting.

## Prerequisites

### Required Tools

- Docker Engine 20.10+
- Docker Compose 2.x
- docker-compose CLI
- jq (for JSON parsing)

### Docker Setup Verification

```bash

# Verify Docker installation

docker --version
docker-compose --version

# Check Docker daemon status

docker info

# Test Docker functionality

docker run hello-world
```

---

## Container Management

### Starting Services

#### Start All Services

```bash

# Start all services in detached mode

docker-compose up -d

# Start with fresh build

docker-compose up -d --build

# Start specific services

docker-compose up -d project-ai prometheus grafana

# Start with logs visible

docker-compose up
```

#### Start Services in Stages

```bash

# Stage 1: Start databases

docker-compose up -d temporal-postgresql

# Wait for database

timeout 60 bash -c 'until docker-compose exec temporal-postgresql pg_isready -U temporal; do sleep 2; done'

# Stage 2: Start core infrastructure

docker-compose up -d temporal prometheus alertmanager grafana

# Stage 3: Start application

docker-compose up -d project-ai temporal-worker

# Stage 4: Start microservices

docker-compose up -d \
  mutation-firewall \
  incident-reflex \
  trust-graph \
  data-vault \
  negotiation-agent \
  compliance-engine \
  verifiable-reality \
  i-believe-in-you

# Stage 5: Start monitoring exporters

docker-compose up -d \
  node-exporter \
  cadvisor \
  postgres-exporter
```

### Stopping Services

#### Stop All Services

```bash

# Stop all services gracefully

docker-compose stop

# Stop all services immediately

docker-compose kill

# Stop and remove containers

docker-compose down

# Stop and remove containers, networks, volumes

docker-compose down -v

# Stop specific services

docker-compose stop project-ai temporal-worker
```

#### Graceful Shutdown

```bash

# Stop services with timeout

docker-compose stop -t 30

# Stop specific service with timeout

docker-compose stop -t 60 project-ai
```

### Restarting Services

#### Restart All Services

```bash

# Restart all services

docker-compose restart

# Restart specific service

docker-compose restart project-ai

# Restart microservices only

docker-compose restart \
  mutation-firewall \
  incident-reflex \
  trust-graph \
  data-vault \
  negotiation-agent \
  compliance-engine \
  verifiable-reality
```

#### Restart with New Configuration

```bash

# Rebuild and restart

docker-compose up -d --build

# Force recreate containers

docker-compose up -d --force-recreate

# Rebuild specific service

docker-compose up -d --build project-ai
```

---

## Container Monitoring

### Service Status

#### Check Service Status

```bash

# List all containers

docker-compose ps

# List containers with resource usage

docker stats

# List containers in JSON format

docker-compose ps --format json | jq .

# Check specific service

docker-compose ps project-ai
```

#### View Service Health

```bash

# Check health status of all containers

docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Check health of specific service

docker inspect project-ai-dev --format='{{.State.Health.Status}}'

# View health check logs

docker inspect project-ai-dev | jq '.[0].State.Health.Log'
```

### Logging

#### View Container Logs

```bash

# View logs from all services

docker-compose logs

# Follow logs in real-time

docker-compose logs -f

# View logs from specific service

docker-compose logs project-ai

# Follow logs from multiple services

docker-compose logs -f project-ai mutation-firewall incident-reflex

# Tail last 100 lines

docker-compose logs --tail=100 project-ai

# Show timestamps

docker-compose logs -t project-ai

# Filter logs by time

docker-compose logs --since 2024-01-01T10:00:00 project-ai
docker-compose logs --since 1h project-ai
```

#### Export Logs

```bash

# Export logs to file

docker-compose logs > logs/docker-compose-$(date +%Y%m%d).log

# Export specific service logs

docker-compose logs project-ai > logs/project-ai-$(date +%Y%m%d).log

# Export logs with timestamps

docker-compose logs -t > logs/docker-compose-timestamped.log
```

### Resource Usage

#### Monitor Resource Consumption

```bash

# Real-time resource stats

docker stats

# Stats for specific containers

docker stats project-ai-dev incident-reflex-system

# Stats in JSON format

docker stats --no-stream --format "{{json .}}" | jq .

# Monitor CPU usage

docker stats --format "table {{.Container}}\t{{.CPUPerc}}" --no-stream

# Monitor memory usage

docker stats --format "table {{.Container}}\t{{.MemUsage}}\t{{.MemPerc}}" --no-stream
```

#### Check Disk Usage

```bash

# Disk usage by images

docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"

# Disk usage by containers

docker ps -a --format "table {{.Names}}\t{{.Size}}"

# Overall disk usage

docker system df

# Detailed disk usage

docker system df -v

# Volume usage

docker volume ls
docker volume inspect project-ai_prometheus-data
```

---

## Build Operations

### Building Images

#### Build All Images

```bash

# Build all services

docker-compose build

# Build with no cache

docker-compose build --no-cache

# Parallel build

docker-compose build --parallel

# Build with build arguments

docker-compose build --build-arg BUILD_VERSION=2.0.0
```

#### Build Specific Images

```bash

# Build main application

docker-compose build project-ai

# Build microservices

docker-compose build \
  mutation-firewall \
  incident-reflex \
  trust-graph \
  data-vault

# Build with progress output

docker-compose build --progress=plain project-ai
```

#### Production Builds

```bash

# Build production image with optimizations

docker build \
  --file Dockerfile.production \
  --tag project-ai:production \
  --build-arg SOURCE_COMMIT_SHA=$(git rev-parse HEAD) \
  --build-arg BUILD_VERSION=$(cat VERSION) \
  --build-arg BUILD_TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ") \
  --build-arg SOURCE_DATE_EPOCH=$(git log -1 --format=%ct) \
  .

# Build sovereign image

docker build \
  --file Dockerfile.sovereign \
  --tag project-ai:sovereign \
  --build-arg SOURCE_COMMIT_SHA=$(git rev-parse HEAD) \
  .

# Multi-stage build for optimization

docker build \
  --target builder \
  --tag project-ai:builder \
  .

docker build \
  --tag project-ai:optimized \
  --file Dockerfile.optimized \
  .
```

#### Build Verification

```bash

# Inspect built image

docker inspect project-ai:latest | jq '.[0].Config.Labels'

# Check image layers

docker history project-ai:latest

# Verify image size

docker images project-ai --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"

# Scan for vulnerabilities

docker scan project-ai:latest

# Run security scan (if Trivy installed)

trivy image project-ai:latest
```

---

## Registry Operations

### Image Tagging

#### Tag Images for Registry

```bash

# Tag for Docker Hub

docker tag project-ai:latest username/project-ai:latest
docker tag project-ai:latest username/project-ai:v2.0.0

# Tag for private registry

docker tag project-ai:latest registry.example.com/project-ai:latest
docker tag project-ai:latest registry.example.com/project-ai:v2.0.0

# Tag for AWS ECR

docker tag project-ai:latest 123456789012.dkr.ecr.us-east-1.amazonaws.com/project-ai:latest

# Tag for Azure ACR

docker tag project-ai:latest myregistry.azurecr.io/project-ai:latest

# Tag for Google GCR

docker tag project-ai:latest gcr.io/my-project/project-ai:latest
```

### Pushing Images

#### Push to Docker Hub

```bash

# Login to Docker Hub

docker login -u username -p password

# Push image

docker push username/project-ai:latest
docker push username/project-ai:v2.0.0

# Push all tags

docker push --all-tags username/project-ai
```

#### Push to Private Registry

```bash

# Login to private registry

docker login registry.example.com -u admin -p password

# Push image

docker push registry.example.com/project-ai:latest

# Logout

docker logout registry.example.com
```

#### Push to AWS ECR

```bash

# Login to ECR

aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  123456789012.dkr.ecr.us-east-1.amazonaws.com

# Create repository (if not exists)

aws ecr create-repository --repository-name project-ai --region us-east-1

# Push image

docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/project-ai:latest

# Verify

aws ecr list-images --repository-name project-ai --region us-east-1
```

#### Push to Azure ACR

```bash

# Login to ACR

az acr login --name myregistry

# Push image

docker push myregistry.azurecr.io/project-ai:latest

# Verify

az acr repository list --name myregistry
az acr repository show-tags --name myregistry --repository project-ai
```

### Pulling Images

#### Pull from Registry

```bash

# Pull latest version

docker pull registry.example.com/project-ai:latest

# Pull specific version

docker pull registry.example.com/project-ai:v2.0.0

# Pull all tags

docker pull --all-tags registry.example.com/project-ai

# Pull with retry on failure

for i in {1..3}; do
  docker pull registry.example.com/project-ai:latest && break
  sleep 5
done
```

---

## Volume Management

### Creating Volumes

#### Create Persistent Volumes

```bash

# Create volume for data

docker volume create project-ai-data

# Create volume with specific driver

docker volume create \
  --driver local \
  --opt type=nfs \
  --opt o=addr=nfs-server,rw \
  --opt device=:/path/to/data \
  project-ai-nfs-data

# List volumes

docker volume ls
```

### Volume Operations

#### Inspect Volumes

```bash

# Inspect volume

docker volume inspect project-ai_prometheus-data

# Check volume size

docker system df -v | grep project-ai

# List files in volume

docker run --rm -v project-ai_prometheus-data:/data alpine ls -lah /data
```

#### Backup Volumes

```bash

# Backup volume to tar

docker run --rm \
  -v project-ai_prometheus-data:/data \
  -v $(pwd)/backups:/backup \
  alpine tar czf /backup/prometheus-data-$(date +%Y%m%d).tar.gz -C /data .

# Backup database volume

docker run --rm \
  -v project-ai_temporal-postgresql-data:/data \
  -v $(pwd)/backups:/backup \
  alpine tar czf /backup/postgres-data-$(date +%Y%m%d).tar.gz -C /data .
```

#### Restore Volumes

```bash

# Restore volume from tar

docker run --rm \
  -v project-ai_prometheus-data:/data \
  -v $(pwd)/backups:/backup \
  alpine sh -c "cd /data && tar xzf /backup/prometheus-data-20260409.tar.gz"

# Verify restore

docker run --rm -v project-ai_prometheus-data:/data alpine ls -lah /data
```

#### Clean Up Volumes

```bash

# Remove unused volumes

docker volume prune

# Remove specific volume

docker volume rm project-ai_old-data

# Remove all volumes (CAUTION!)

docker volume rm $(docker volume ls -q)
```

---

## Network Management

### Network Operations

#### List Networks

```bash

# List all networks

docker network ls

# Inspect network

docker network inspect project-ai-network

# List containers in network

docker network inspect project-ai-network | \
  jq '.[0].Containers | keys'
```

#### Test Network Connectivity

```bash

# Test connectivity between services

docker-compose exec project-ai ping -c 3 postgres

# Test DNS resolution

docker-compose exec project-ai nslookup temporal

# Test HTTP connectivity

docker-compose exec project-ai curl http://prometheus:9090/-/healthy

# Test microservice connectivity

docker-compose exec project-ai \
  curl http://incident-reflex:8000/api/v1/health/liveness
```

---

## Troubleshooting

### Container Issues

#### Container Won't Start

```bash

# Check container status

docker-compose ps

# View container logs

docker-compose logs project-ai

# Check last exit code

docker-compose ps -a --format json | jq -r '.[] | select(.Name=="project-ai-dev") | .ExitCode'

# Inspect container

docker inspect project-ai-dev

# Common issues:

# 1. Port already in use

sudo netstat -tulpn | grep :8000

# 2. Missing environment variables

docker-compose config | grep -A 10 environment

# 3. Volume mount issues

docker-compose config | grep -A 5 volumes
```

#### Container Keeps Restarting

```bash

# Check restart count

docker inspect project-ai-dev | jq '.[0].RestartCount'

# View logs for crash reason

docker-compose logs --tail=100 project-ai

# Check resource limits

docker inspect project-ai-dev | jq '.[0].HostConfig | {Memory, MemorySwap, CpuShares}'

# Check health check status

docker inspect project-ai-dev | jq '.[0].State.Health'

# Disable restart to troubleshoot

docker update --restart=no project-ai-dev
```

#### Out of Memory Issues

```bash

# Check container memory usage

docker stats --no-stream project-ai-dev

# Increase memory limit

docker-compose stop project-ai

# Edit docker-compose.yml to increase mem_limit

docker-compose up -d project-ai

# Check for memory leaks

docker stats project-ai-dev

# View OOM events

dmesg | grep -i "out of memory"
```

### Build Issues

#### Build Failures

```bash

# Build with verbose output

docker-compose build --progress=plain project-ai

# Build without cache

docker-compose build --no-cache project-ai

# Check Dockerfile syntax

docker build --check -f Dockerfile .

# Test build step by step

docker build --target builder -t project-ai:builder .
docker run -it project-ai:builder /bin/bash
```

#### Slow Builds

```bash

# Use BuildKit for faster builds

export DOCKER_BUILDKIT=1
docker-compose build

# Use build cache

docker-compose build --build-arg BUILDKIT_INLINE_CACHE=1

# Build with parallel execution

docker-compose build --parallel

# Check .dockerignore

cat .dockerignore
```

### Network Issues

#### Service Communication Failures

```bash

# Check if services are in same network

docker-compose ps
docker network inspect project-ai-network

# Test DNS resolution

docker-compose exec project-ai nslookup incident-reflex

# Test port connectivity

docker-compose exec project-ai nc -zv incident-reflex 8000

# Check firewall rules

sudo iptables -L DOCKER-USER

# Check Docker network settings

docker network inspect bridge
```

#### Port Conflicts

```bash

# Find process using port

sudo lsof -i :8000
sudo netstat -tulpn | grep :8000

# Kill process

sudo kill -9 <pid>

# Change port in docker-compose.yml

# ports:

#   - "8001:8000"  # Use different host port

```

---

## Maintenance Tasks

### Cleaning Up

#### Remove Stopped Containers

```bash

# Remove all stopped containers

docker container prune

# Remove specific stopped container

docker rm project-ai-dev

# Remove container and volumes

docker rm -v project-ai-dev

# Force remove running container

docker rm -f project-ai-dev
```

#### Clean Up Images

```bash

# Remove unused images

docker image prune

# Remove all unused images

docker image prune -a

# Remove specific image

docker rmi project-ai:old

# Remove dangling images

docker rmi $(docker images -f "dangling=true" -q)
```

#### Full System Cleanup

```bash

# Remove all unused resources

docker system prune

# Remove all unused resources including volumes

docker system prune -a --volumes

# Check space reclaimed

docker system df
```

### Performance Optimization

#### Optimize Builds

```bash

# Use multi-stage builds (see Dockerfile)

# Use .dockerignore to exclude unnecessary files

# Layer caching optimization

# Minimize image size

docker images | sort -k7 -h

# Analyze layers

dive project-ai:latest  # requires dive tool
```

#### Optimize Runtime

```bash

# Adjust worker count based on CPU

export API_WORKERS=$(($(nproc) * 2 + 1))
docker-compose up -d

# Enable resource limits

# Edit docker-compose.yml:

# deploy:

#   resources:

#     limits:

#       cpus: '2.0'

#       memory: 4G

# Use host network for performance (dev only)

# network_mode: "host"

```

---

## Backup and Recovery

### Backup Strategy

#### Backup All Services

```bash

# Stop services

docker-compose stop

# Backup volumes

mkdir -p backups/$(date +%Y%m%d)
for volume in $(docker volume ls --format '{{.Name}}' | grep project-ai); do
  echo "Backing up $volume..."
  docker run --rm \
    -v $volume:/data \
    -v $(pwd)/backups/$(date +%Y%m%d):/backup \
    alpine tar czf /backup/$volume.tar.gz -C /data .
done

# Backup configuration

cp .env backups/$(date +%Y%m%d)/
cp docker-compose.yml backups/$(date +%Y%m%d)/

# Restart services

docker-compose up -d
```

### Restore from Backup

#### Restore All Services

```bash

# Stop services

docker-compose down -v

# Restore volumes

BACKUP_DATE="20260409"
for volume in $(ls backups/$BACKUP_DATE/*.tar.gz); do
  volume_name=$(basename $volume .tar.gz)
  echo "Restoring $volume_name..."
  docker volume create $volume_name
  docker run --rm \
    -v $volume_name:/data \
    -v $(pwd)/backups/$BACKUP_DATE:/backup \
    alpine tar xzf /backup/$(basename $volume) -C /data
done

# Restore configuration

cp backups/$BACKUP_DATE/.env .
cp backups/$BACKUP_DATE/docker-compose.yml .

# Start services

docker-compose up -d
```

---

## Security Operations

### Security Scanning

#### Scan Images for Vulnerabilities

```bash

# Docker Scout (built-in)

docker scout quickview project-ai:latest
docker scout cves project-ai:latest

# Trivy scanner

trivy image project-ai:latest

# Grype scanner

grype project-ai:latest
```

#### Audit Container Configuration

```bash

# Check running containers for security issues

docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/docker-bench-security

# Check specific container

docker inspect project-ai-dev | jq '.[0].HostConfig.SecurityOpt'
```

### Secret Management

#### Rotate Secrets

```bash

# Update .env file with new secrets

# Recreate containers

docker-compose up -d --force-recreate
```

---

## Emergency Procedures

### Emergency Stop

```bash

# Stop all services immediately

docker-compose kill

# Stop Docker daemon

sudo systemctl stop docker
```

### Emergency Recovery

```bash

# Restore from backup

./restore_backup.sh

# Or rebuild from scratch

docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

---

**Last Updated**: 2026-04-09  
**Maintained By**: SRE Team  
**Review Frequency**: Quarterly
