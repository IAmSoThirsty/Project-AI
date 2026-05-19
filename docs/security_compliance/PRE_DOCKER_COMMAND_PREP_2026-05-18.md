# Pre-Docker Command Preparation (2026-05-18)

## Safe local-first command (approved after freeze is lifted)

docker build --file api/Dockerfile --tag project-ai-api:preprod-local .

## DO NOT RUN YET (explicitly blocked)

## DO NOT RUN: Docker Build Cloud / remote builder / push

docker buildx build --builder cloud-org-builder --platform linux/amd64 --file api/Dockerfile --tag ghcr.io/iamsothirsty/project-ai:preprod --push .

## Preconditions before any Docker Build Cloud usage

1. `.env` containment complete (tracking verified and denylist in place)
2. CI/CD fail-closed repair complete and passing
3. Release/deploy freeze explicitly lifted
4. Explicit human approval for cloud build/push/deploy
