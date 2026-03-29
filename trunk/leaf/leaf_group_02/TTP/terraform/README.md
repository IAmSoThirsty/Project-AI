<!-- # ============================================================================ # -->
<!-- # STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59 # -->
<!-- # COMPLIANCE: Sovereign Substrate / README.md # -->
<!-- # ============================================================================ # -->
<div align="right">
  <img src="https://img.shields.io/badge/DATE-2026-03-18-blueviolet?style=for-the-badge" alt="Date" />
  <img src="https://img.shields.io/badge/PRODUCTIVITY-ACTIVE-success?style=for-the-badge" alt="Productivity" />
</div>
<!-- # ============================================================================ #


<!-- # COMPLIANCE: Sovereign Substrate / README.md # -->
<!-- # ============================================================================ #

<!-- # Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master -->
# TTP Infrastructure as Code

This directory contains Terraform modules for deploying the TTP application infrastructure on AWS.

## Architecture

The infrastructure includes:
- VPC with public/private subnets across 3 AZs
- EKS cluster for Kubernetes workloads
- RDS PostgreSQL 16 with Multi-AZ
- ElastiCache Redis cluster
- S3 buckets for texture assets
- CloudFront CDN for asset delivery
- Application Load Balancer
- Route53 DNS management
- IAM roles and policies
- CloudWatch logging and monitoring

## Prerequisites

- Terraform >= 1.6.0
- AWS CLI configured with appropriate credentials
- kubectl for Kubernetes management
- Sufficient AWS account limits for resources

## Directory Structure

```
terraform/
├── environments/
│   ├── dev/           # Development environment
│   ├── staging/       # Staging environment
│   └── prod/          # Production environment
├── modules/
│   ├── vpc/           # VPC and networking
│   ├── eks/           # EKS cluster
│   ├── rds/           # PostgreSQL database
│   ├── redis/         # ElastiCache Redis
│   ├── s3/            # S3 buckets and CloudFront
│   └── monitoring/    # CloudWatch and observability
└── README.md
```

## Usage

### Initialize Terraform

```bash
cd terraform/environments/dev
terraform init
```

### Plan Changes

```bash
terraform plan -var-file=terraform.tfvars
```

### Apply Infrastructure

```bash
terraform apply -var-file=terraform.tfvars
```

### Destroy Infrastructure

```bash
terraform destroy -var-file=terraform.tfvars
```

## Environments

### Development
- Smaller instance types
- Single-AZ database
- Reduced redundancy
- Lower costs

### Staging
- Production-like configuration
- Multi-AZ for testing
- Full monitoring enabled

### Production
- High availability across 3 AZs
- Multi-AZ database with read replicas
- Enhanced monitoring and alerting
- Auto-scaling enabled
- Backup and disaster recovery

## Security

- All databases in private subnets
- Encryption at rest and in transit
- Secrets stored in AWS Secrets Manager
- IAM roles with least privilege
- Security groups with minimal access
- VPC Flow Logs enabled
- GuardDuty for threat detection

## Monitoring

- CloudWatch Logs for centralized logging
- CloudWatch Metrics for infrastructure metrics
- CloudWatch Alarms for critical events
- X-Ray for distributed tracing
- Container Insights for EKS

## Cost Optimization

- Use spot instances for non-critical workloads
- Enable S3 Intelligent Tiering
- Use RDS Reserved Instances for production
- Enable auto-scaling to match demand
- Set up cost allocation tags

## Disaster Recovery

- RDS automated backups (35-day retention)
- S3 versioning and lifecycle policies
- Multi-region replication option
- Infrastructure as Code for quick rebuild
- Documented recovery procedures

## License

MIT License - See LICENSE file for details.
