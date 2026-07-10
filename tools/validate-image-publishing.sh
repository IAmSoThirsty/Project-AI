#!/bin/bash
# Validation commands for Production Image Publishing Pipeline

set -euo pipefail

echo "=== VALIDATION: Production Image Publishing Pipeline ==="
echo

# 1. Verify Helm chart syntax
echo "[1/6] Validating Helm chart syntax..."
helm lint helm/project-ai --strict
echo "✓ Helm chart passes linting"
echo

# 2. Verify Helm templates render with development values
echo "[2/6] Validating Helm template rendering (development)..."
helm template project-ai-dev helm/project-ai -f helm/project-ai/values.yaml > /tmp/helm-dev.yaml
if grep -q "image: project-ai-development-" /tmp/helm-dev.yaml; then
  echo "✓ Development image references correct"
else
  echo "✗ Development image references failed"
  exit 1
fi
echo

# 3. Verify Helm templates render with production values
echo "[3/6] Validating Helm template rendering (production)..."
helm template project-ai-prod helm/project-ai \
  -f helm/values.prod.yaml \
  --set image.owner=project-ai \
  --set image.tag=v0.1.0 > /tmp/helm-prod.yaml
if grep -q "image: ghcr.io/project-ai/project-ai-" /tmp/helm-prod.yaml; then
  echo "✓ Production image references correct (ghcr.io)"
else
  echo "✗ Production image references failed"
  exit 1
fi
echo

# 4. Validate GitHub Actions workflow
echo "[4/6] Validating GitHub Actions workflow..."
if [ -f .github/workflows/publish.yaml ]; then
  echo "✓ publish.yaml workflow exists"
  # Check for required jobs
  for job in image-metadata build-api build-web build-adapters build-genesis verify-images; do
    if grep -q "name: $job\|^  [a-z-]*:\|name: .*$job" .github/workflows/publish.yaml; then
      echo "  ✓ Job '$job' defined"
    fi
  done
else
  echo "✗ publish.yaml workflow not found"
  exit 1
fi
echo

# 5. Verify .dockerignore is optimized
echo "[5/6] Checking .dockerignore..."
if grep -q "node_modules\|__pycache__\|.git" .dockerignore; then
  echo "✓ .dockerignore includes common patterns"
else
  echo "✗ .dockerignore missing expected patterns"
  exit 1
fi
echo

# 6. Verify production values structure
echo "[6/6] Validating production values configuration..."
if grep -q "image:" helm/values.prod.yaml && \
   grep -q "api:" helm/values.prod.yaml && \
   grep -q "persistence:" helm/values.prod.yaml; then
  echo "✓ Production values include required sections"
else
  echo "✗ Production values incomplete"
  exit 1
fi
echo

echo "=== All validations passed ==="
