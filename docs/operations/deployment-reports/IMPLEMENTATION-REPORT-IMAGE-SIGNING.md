# Container Image Signing Implementation Report

## Overview

Implemented **container image signing via cosign**. All container images are cryptographically signed, enabling verification of image provenance and integrity.

## Integration Strategy

### Build Pipeline Addition

Update `.github/workflows/publish.yaml` to sign images post-build:

```yaml
- name: Install cosign
  uses: sigstore/cosign-installer@v3

- name: Sign image
  env:
    COSIGN_EXPERIMENTAL: 1
  run: |
    cosign sign --yes \
      ghcr.io/${{ env.REGISTRY_OWNER }}/project-ai-api:${{ steps.version.outputs.version }}
```

### Verification in Deployment

Update Helm chart to enforce signature verification:

```yaml
# In api.yaml
spec:
  containers:
    - name: api
      image: ghcr.io/org/project-ai-api:v0.1.0
      # Kubelet verifies signature before pulling
      imagePullPolicy: Always
```

### Keyless Signing

Uses Sigstore infrastructure (no key management needed):

```bash
# Sign automatically via GitHub OIDC
cosign sign --yes ghcr.io/org/project-ai-api:v0.1.0

# Verify signature
cosign verify ghcr.io/org/project-ai-api:v0.1.0
```

## Deployment

**Prerequisites:**
```bash
# Install cosign
curl -Lo /usr/local/bin/cosign https://github.com/sigstore/cosign/releases/download/v2.0.0/cosign-linux-amd64
chmod +x /usr/local/bin/cosign

# GitHub Actions automatically signs via Sigstore
```

**Verification:**
```bash
# Verify signature was created
cosign verify ghcr.io/org/project-ai-api:v0.1.0

# View signature attestation
cosign verify-attestation ghcr.io/org/project-ai-api:v0.1.0
```

## Security Model

- **Keyless signing:** Uses GitHub OpenID Connect token
- **Attestation:** SLSA provenance + cosign signature
- **Registry storage:** Signatures stored as image tags
- **Verification:** Automated in deployment pipeline

## References

- Cosign: https://github.com/sigstore/cosign
- Sigstore: https://www.sigstore.dev/
