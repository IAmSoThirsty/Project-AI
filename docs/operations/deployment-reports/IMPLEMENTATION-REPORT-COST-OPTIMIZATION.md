# Cost Optimization Implementation Report

> **Current release boundary (2026-07-19):** This is a historical or
> implementation-reference artifact, not current production evidence or
> deployment approval. The v0.0.3 successor remains fail-closed until the
> [pre-deployment checklist](../../deployment/PRE_DEPLOYMENT_CHECKLIST.md) and
> [CAB evidence bundle](../cab/PROJECT_AI_V0.0.3_SUCCESSOR_CAB_REVIEW_PACK.md)
> pass. Commands here are examples; this document does not prove deployment.

## Overview

Documented **cost optimization strategies** for production deployments. Focus on resource efficiency, reserved capacity, and waste reduction.

## Cost Drivers

### Compute

Current allocation:
- API: 2 replicas × 200m CPU = 400m total
- Portals: 2 replicas × 50m CPU = 100m total
- Adapters: 3 × 100m = 300m total
- Genesis: 1 × 50m = 50m total
- **Total: 850m CPU (~1 small node)**

Optimization:
- Use `requests` for fair-share scheduling
- Bin-pack on fewer larger nodes (cheaper than many small)
- Use spot instances for adapters (stateless, can restart)

### Storage

Current allocation:
- Audit PVC: 10Gi ($0.10/GB/month) = $1/month
- Backup PVC: 5Gi = $0.50/month
- **Total: $1.50/month**

Optimization:
- Use cold storage for backups (S3 Glacier = -90% cost)
- Archive old audit data quarterly
- Delete local backups after S3 upload

### Network

Egress: Major cost driver

Optimization:
- Minimize external API calls (cache responses)
- Use private registries (no egress for pull)
- Regional deployment (no cross-region traffic)

## Cost Reduction Roadmap

### Month 1: Immediate Savings (10-15%)
- Right-size resource requests
- Enable cluster autoscaling
- Use spot instances for adapters

### Month 2: Infrastructure Optimization (20-30%)
- Archive old data
- Optimize backup storage (Glacier)
- DNS optimization

### Month 3: Application-Level (15-25%)
- Caching improvements
- API call reduction
- Batch operations

**Potential total savings: 40-50% YoY**

## References

- Cloud Cost Optimization: https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/
