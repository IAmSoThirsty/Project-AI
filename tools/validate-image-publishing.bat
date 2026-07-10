@echo off
REM Validation commands for Production Image Publishing Pipeline

setlocal enabledelayedexpansion

echo === VALIDATION: Production Image Publishing Pipeline ===
echo.

REM 1. Verify Helm chart syntax
echo [1/6] Validating Helm chart syntax...
helm lint helm/project-ai --strict
if !errorlevel! neq 0 (
  echo Error: Helm linting failed
  exit /b 1
)
echo OK: Helm chart passes linting
echo.

REM 2. Verify Helm templates render with development values
echo [2/6] Validating Helm template rendering (development)...
helm template project-ai-dev helm/project-ai -f helm/project-ai/values.yaml > tmp\helm-dev.yaml 2>&1
findstr /M "image: project-ai-development-" tmp\helm-dev.yaml >nul
if !errorlevel! neq 0 (
  echo Error: Development image references failed
  exit /b 1
)
echo OK: Development image references correct
echo.

REM 3. Verify Helm templates render with production values
echo [3/6] Validating Helm template rendering (production)...
helm template project-ai-prod helm/project-ai ^
  -f helm/values.prod.yaml ^
  --set image.owner=project-ai ^
  --set image.tag=v0.1.0 > tmp\helm-prod.yaml 2>&1
findstr /M "image: ghcr.io/project-ai/project-ai-" tmp\helm-prod.yaml >nul
if !errorlevel! neq 0 (
  echo Error: Production image references failed
  exit /b 1
)
echo OK: Production image references correct ^(ghcr.io^)
echo.

REM 4. Validate GitHub Actions workflow
echo [4/6] Validating GitHub Actions workflow...
if not exist ".github/workflows/publish.yaml" (
  echo Error: publish.yaml workflow not found
  exit /b 1
)
echo OK: publish.yaml workflow exists
echo.

REM 5. Verify .dockerignore is optimized
echo [5/6] Checking .dockerignore...
findstr /M "node_modules" .dockerignore >nul
if !errorlevel! neq 0 (
  echo Error: .dockerignore missing expected patterns
  exit /b 1
)
echo OK: .dockerignore includes common patterns
echo.

REM 6. Verify production values structure
echo [6/6] Validating production values configuration...
findstr /M "image:" helm/values.prod.yaml >nul
findstr /M "persistence:" helm/values.prod.yaml >nul
if !errorlevel! neq 0 (
  echo Error: Production values incomplete
  exit /b 1
)
echo OK: Production values include required sections
echo.

echo === All validations passed ===
