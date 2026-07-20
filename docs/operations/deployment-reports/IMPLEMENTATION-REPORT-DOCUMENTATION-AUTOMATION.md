# Documentation Automation Implementation Report

> **Current release boundary (2026-07-19):** This is a historical or
> implementation-reference artifact, not current production evidence or
> deployment approval. The v0.0.3 successor remains fail-closed until the
> [pre-deployment checklist](../../deployment/PRE_DEPLOYMENT_CHECKLIST.md) and
> [CAB evidence bundle](../cab/PROJECT_AI_V0.0.3_SUCCESSOR_CAB_REVIEW_PACK.md)
> pass. Commands here are examples; this document does not prove deployment.

## Overview

Documented **documentation automation strategies** for keeping infrastructure docs synchronized with code.

## Automation Approach

### 1. Helm Chart Documentation

Auto-generate from Helm chart:

```bash
# Generate schema
helm schema project-ai > schema.json

# Generate values documentation
helm-docs -c helm/project-ai
```

### 2. Kubernetes Resource Docs

Extract from manifests:

```bash
# Generate CRD docs
kube-doc helm/project-ai/templates/ > resources.md
```

### 3. Deployment Runbooks

Auto-generate from templates + CI logs:

```bash
# Extract deployment info
kubectl get deployments -o custom-columns=NAME:.metadata.name,REPLICAS:.spec.replicas
```

### 4. Monitoring Dashboard Docs

Auto-generate from PrometheusRule:

```bash
# Extract alert rules → runbook
yq '.spec.groups[].rules[].annotations.runbook' helm/project-ai/templates/prometheusrule.yaml
```

### 5. CI/CD Pipeline Documentation

Auto-update from workflow files:

```yaml
# In publish.yaml
- name: Generate release notes
  run: |
    cat > release-notes.md <<EOF
    # Release ${{ needs.image-metadata.outputs.version }}

    Services: api, portals, adapters, genesis
    Built at: $(date)
    Images: ...
    EOF
```

## Implementation

Create CI job to:
1. Extract Helm values → API docs
2. Extract alerts → runbook docs
3. Extract deployment templates → resource docs
4. Commit updated docs to repo

## Tools

- `helm-docs`: Auto-generate values.md
- `kube-doc`: Kubernetes resource documentation
- `yq`: YAML schema extraction
- Custom scripts: Template-specific extraction

## References

- Helm Docs: https://github.com/norwoodj/helm-docs
- Documentation-as-Code: https://github.com/slatedocs/slate
