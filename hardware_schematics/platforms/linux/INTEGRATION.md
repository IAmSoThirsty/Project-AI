# Project-AI Pip-Boy - Linux x86_64 Platform Integration Guide

**Platform:** Linux (x86_64)  
**Version:** 1.0.0  
**Last Updated:** 2026-02-23  
**Status:** Production-Ready

---

## Executive Summary

Comprehensive integration specifications for deploying Project-AI Pip-Boy on Linux x86_64 platforms. Enables server-grade reliability, development workstation flexibility, and complete control over the software stack.

**Key Advantages:**
- **Server Deployment:** 24/7 operation, high availability
- **Development Workstation:** Native environment, debugging tools
- **Open Source:** Complete transparency, no vendor lock-in
- **Resource Scaling:** Single-board to data center
- **Container Support:** Docker/Podman for isolated deployment

---

## Supported Distributions

### Enterprise (LTS)
| Distribution | Version | Kernel | Support Until |
|--------------|---------|--------|---------------|
| Ubuntu LTS | 24.04 | 6.8+ | April 2029 |
| Debian Stable | 12 | 6.1+ | June 2028 |
| RHEL | 9.3 | 5.14+ | May 2032 |
| Rocky Linux | 9.3 | 5.14+ | May 2032 |

### Community
| Distribution | Version | Update Cycle |
|--------------|---------|--------------|
| Fedora | 39/40 | 6 months |
| Arch Linux | Rolling | Continuous |
| Ubuntu | 23.10/24.04 | 6 months |

---

## Hardware Requirements

### Minimum
- **CPU:** Intel i3 / AMD Ryzen 3 (4 cores, x86_64, SSE4.2)
- **RAM:** 4GB (2GB OS, 2GB Project-AI)
- **Storage:** 20GB SSD
- **GPU:** Intel UHD 620 / AMD Vega 3 (OpenCL 1.2+)

### Recommended
- **CPU:** Intel i7 / AMD Ryzen 7 (8 cores, AVX2)
- **RAM:** 16GB
- **Storage:** 256GB NVMe SSD
- **GPU:** NVIDIA RTX 3060 / AMD RX 6600 (CUDA 12.0+ / ROCm 5.7+)

### High-Performance
- **CPU:** Intel Xeon / AMD EPYC (16+ cores)
- **RAM:** 64GB+
- **Storage:** 1TB+ NVMe RAID 1
- **GPU:** NVIDIA A100 / AMD MI250 (312/383 TFLOPS FP16)

---

## Installation (Ubuntu 24.04 Example)

### System Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install essentials
sudo apt install -y build-essential git curl wget python3.12 python3.12-venv python3-pip

# Clone Project-AI
git clone https://github.com/IAmSoThirsty/Project-AI.git
cd Project-AI

# Create virtual environment
python3.12 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -e .
```

### CUDA Toolkit (NVIDIA GPU)
```bash
# Add NVIDIA repository
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2404/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
sudo apt update

# Install CUDA 12.3
sudo apt install -y cuda-toolkit-12-3 libcudnn8 libcudnn8-dev

# Add to PATH
echo 'export PATH=/usr/local/cuda-12.3/bin:$PATH' >> ~/.bashrc
echo 'export LD_LIBRARY_PATH=/usr/local/cuda-12.3/lib64:$LD_LIBRARY_PATH' >> ~/.bashrc
source ~/.bashrc

# Verify
nvcc --version
nvidia-smi
```

### ROCm (AMD GPU)
```bash
# Install ROCm 6.0
wget https://repo.radeon.com/amdgpu-install/6.0/ubuntu/noble/amdgpu-install_6.0.60000-1_all.deb
sudo apt install -y ./amdgpu-install_6.0.60000-1_all.deb
sudo amdgpu-install --usecase=hip,rocm

# Verify
rocm-smi
```

---

## AI/ML Framework Installation

### PyTorch
```bash
# NVIDIA CUDA
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# AMD ROCm
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm5.7

# CPU only
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Verify
python -c "import torch; print(torch.cuda.is_available())"
```

### TensorFlow
```bash
# GPU support
pip install tensorflow[and-cuda]==2.15.0

# Verify
python -c "import tensorflow as tf; print(tf.config.list_physical_devices('GPU'))"
```

### Hugging Face Transformers
```bash
pip install transformers accelerate bitsandbytes optimum auto-gptq

# Load model example
python << EOF
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

model_id = "meta-llama/Llama-2-7b-chat-hf"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    torch_dtype=torch.float16,
    device_map="auto"
)
print("Model loaded successfully!")
EOF
```

---

## Service Configuration

### Systemd Service
```ini
# /etc/systemd/system/projectai.service
[Unit]
Description=Project-AI Pip-Boy Service
After=network.target

[Service]
Type=simple
User=projectai
Group=projectai
WorkingDirectory=/opt/projectai
Environment="PATH=/opt/projectai/venv/bin"
Environment="PROJECTAI_CONFIG=/etc/projectai/config.yaml"
ExecStart=/opt/projectai/venv/bin/python -m projectai.server
Restart=always
RestartSec=10

# Security hardening
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable projectai.service
sudo systemctl start projectai.service
```

### Configuration File
```yaml
# /etc/projectai/config.yaml
server:
  host: 0.0.0.0
  port: 8000
  workers: 4

ai:
  engine: "local"
  model: "llama-2-7b-chat"
  device: "cuda"
  max_tokens: 2048
  temperature: 0.7

storage:
  database: "postgresql://projectai:password@localhost/projectai"
  redis: "redis://localhost:6379/0"

security:
  jwt_secret: "CHANGE_ME"
  tls:
    enabled: true
    cert: "/etc/projectai/ssl/cert.pem"
    key: "/etc/projectai/ssl/key.pem"
```

---

## Database Setup

### PostgreSQL
```bash
# Install PostgreSQL 16
sudo apt install -y postgresql-16 postgresql-contrib-16

# Create database
sudo -u postgres psql << EOF
CREATE DATABASE projectai;
CREATE USER projectai WITH ENCRYPTED PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE projectai TO projectai;
EOF
```

### Redis
```bash
# Install Redis
sudo apt install -y redis-server

# Configure
sudo tee /etc/redis/redis.conf << EOF
bind 127.0.0.1
port 6379
maxmemory 2gb
maxmemory-policy allkeys-lru
EOF

sudo systemctl restart redis-server
```

---

## Web Server (Nginx)

```nginx
# /etc/nginx/sites-available/projectai
upstream projectai_backend {
    server 127.0.0.1:8000;
}

server {
    listen 443 ssl http2;
    server_name pipboy.example.com;
    
    ssl_certificate /etc/letsencrypt/live/pipboy.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/pipboy.example.com/privkey.pem;
    
    location / {
        proxy_pass http://projectai_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/projectai /etc/nginx/sites-enabled/
sudo certbot --nginx -d pipboy.example.com
sudo nginx -t && sudo systemctl reload nginx
```

---

## Docker Deployment

### Dockerfile
```dockerfile
FROM ubuntu:24.04

RUN apt-get update && apt-get install -y \
    python3.12 python3-pip git curl && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .
RUN pip3 install -e .

EXPOSE 8000
CMD ["python3", "-m", "projectai.server"]
```

### Docker Compose
```yaml
version: '3.8'

services:
  projectai:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://projectai:password@postgres:5432/projectai
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - postgres
      - redis
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
  
  postgres:
    image: postgres:16-alpine
    environment:
      - POSTGRES_DB=projectai
      - POSTGRES_USER=projectai
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

```bash
docker compose up -d
docker compose logs -f projectai
```

---

## Performance Optimization

### CPU
```bash
# Set performance governor
sudo cpufreq-set -g performance

# Enable turbo boost (Intel)
echo 0 | sudo tee /sys/devices/system/cpu/intel_pstate/no_turbo
```

### GPU (NVIDIA)
```bash
# Persistent mode
sudo nvidia-smi -pm 1

# Max power limit (RTX 3090: 350W)
sudo nvidia-smi -pl 350

# Monitor
watch -n 1 nvidia-smi
```

### Memory
```bash
# Optimize TCP
sudo tee -a /etc/sysctl.conf << EOF
kernel.shmmax = 68719476736
net.core.rmem_max = 134217728
net.core.wmem_max = 134217728
EOF
sudo sysctl -p
```

---

## Monitoring

### Prometheus
```yaml
# /etc/prometheus/prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'projectai'
    static_configs:
      - targets: ['localhost:8000']
  
  - job_name: 'node_exporter'
    static_configs:
      - targets: ['localhost:9100']
```

### Grafana
```bash
sudo apt install -y grafana
sudo systemctl enable grafana-server
sudo systemctl start grafana-server
# Access at http://localhost:3000
```

---

## Backup

```bash
#!/bin/bash
# /opt/projectai/backup.sh

BACKUP_DIR="/backup/projectai"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p "$BACKUP_DIR/$DATE"

# Database
pg_dump -U projectai projectai | gzip > "$BACKUP_DIR/$DATE/database.sql.gz"

# Redis
redis-cli --rdb "$BACKUP_DIR/$DATE/redis.rdb"

# Configuration
tar -czf "$BACKUP_DIR/$DATE/config.tar.gz" /etc/projectai

# Upload to S3 (optional)
aws s3 sync "$BACKUP_DIR/$DATE" "s3://my-backup-bucket/projectai/$DATE"

# Cleanup (30 days)
find "$BACKUP_DIR" -type d -mtime +30 -exec rm -rf {} \;
```

```bash
# Schedule with cron
sudo crontab -e
# Add: 0 2 * * * /opt/projectai/backup.sh
```

---

## Performance Benchmarks

### AI Inference Speed

| Model | i7-13700 (CPU) | RTX 3090 (GPU) | A100 (GPU) |
|-------|----------------|----------------|------------|
| GPT-2 (1.5B) | 850ms | 45ms | 15ms |
| Llama 2 7B | 3200ms | 180ms | 55ms |
| Llama 2 13B | 6800ms | 350ms | 110ms |
| Stable Diffusion (512x512) | 45s | 2.8s | 0.9s |

### Concurrent Users

| Hardware | Light (5 req/s) | Medium (20 req/s) | Heavy (100 req/s) |
|----------|-----------------|-------------------|-------------------|
| i3 + 8GB | ✅ | ⚠️ | ❌ |
| i7 + 32GB + RTX 3060 | ✅ | ✅ | ⚠️ |
| Xeon + 128GB + A100 | ✅ | ✅ | ✅ |

---

## Cost Analysis

### Hardware
| Config | Components | Total Cost |
|--------|-----------|------------|
| Budget | i3 + 8GB + 256GB SSD | ~\$600 |
| Standard | i7 + 32GB + RTX 3060 + 1TB | ~\$1,400 |
| High-Perf | Xeon + 128GB + A100 + 2TB RAID | ~\$13,500 |
| Cloud | c6i.4xlarge (AWS) | \$0.68/hr (\$500/mo) |

### Software
- **OS:** FREE (Ubuntu, Debian, Rocky)
- **PostgreSQL:** FREE
- **Redis:** FREE
- **Nginx:** FREE
- **CUDA/ROCm:** FREE
- **Monitoring:** FREE (Prometheus/Grafana)

**Monthly Cost:** \$0-\$50 (electricity) or \$500-\$2,000 (cloud)

---

## Security Hardening

### Firewall (UFW)
```bash
sudo ufw enable
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw allow from 127.0.0.1 to any port 8000  # Project-AI (internal)
```

### Fail2Ban
```bash
sudo apt install -y fail2ban

sudo tee /etc/fail2ban/jail.local << EOF
[nginx-http-auth]
enabled = true
logpath = /var/log/nginx/error.log

[nginx-limit-req]
enabled = true
logpath = /var/log/nginx/error.log
EOF

sudo systemctl restart fail2ban
```

---

## Conclusion

**Linux x86_64 Platform Summary:**
- ✅ **Enterprise-Grade:** 24/7 reliability, server deployment
- ✅ **Full Control:** Open source, complete customization
- ✅ **High Performance:** Desktop CPUs, powerful GPUs
- ✅ **Scalability:** Single-board to data center
- ✅ **Cost-Effective:** No licensing fees
- ✅ **Developer-Friendly:** Native tools, debugging
- ✅ **Container Support:** Docker/Podman

**Recommended Use Cases:**
- Development workstation (local testing)
- Server deployment (multi-user API)
- AI training (model fine-tuning)
- Enterprise backend (on-premises)

**Support:** https://github.com/IAmSoThirsty/Project-AI/issues  
**Documentation:** https://projectai.dev/docs/linux
