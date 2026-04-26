# 10: Deployment Pipeline Maps

**Document**: Complete Deployment Pipeline Visualization  
**System**: End-to-End Deployment Flow Maps  
**Related Systems**: All 9 deployment systems

---


## Navigation

**Location**: `relationships\deployment\10_deployment_pipeline_maps.md`

**Parent**: [[relationships\deployment\README.md]]


## Complete Deployment Pipeline

```
┌────────────────────────────────────────────────────────────────────────────┐
│                      COMPLETE DEPLOYMENT PIPELINE                           │
│                     (Development → Production)                              │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Developer Commits Code                                                     │
│  └─→ git commit -m "feat: Add new feature"                                 │
│  └─→ git push origin develop                                               │
│           ↓                                                                 │
│  ┌──────────────────────────────────────────────────────────────┐          │
│  │  Phase 1: CI Pipeline (GitHub Actions)                       │          │
│  │  Trigger: push to develop                                    │          │
│  │                                                               │          │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐             │          │
│  │  │   Lint     │  │  Security  │  │    Test    │             │          │
│  │  │            │  │            │  │            │             │          │
│  │  │ • ruff     │  │ • bandit   │  │ • pytest   │             │          │
│  │  │ • mypy     │  │ • trivy    │  │ • coverage │             │          │
│  │  │ • black    │  │ • pip-audit│  │ • matrix   │             │          │
│  │  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘             │          │
│  │        └────────────────┼────────────────┘                   │          │
│  │                         ↓                                    │          │
│  │              All Checks Pass?                                │          │
│  │                  ├─→ No: Block merge, notify dev            │          │
│  │                  └─→ Yes: Continue to build                 │          │
│  └────────────────────────┬─────────────────────────────────────┘          │
│                           ↓                                                 │
│  ┌──────────────────────────────────────────────────────────────┐          │
│  │  Phase 2: Build Artifacts                                    │          │
│  │                                                               │          │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │          │
│  │  │ Docker Build    │  │ Desktop Build   │  │ Python Wheel │ │          │
│  │  │                 │  │                 │  │              │ │          │
│  │  │ • Multi-stage   │  │ • PyInstaller   │  │ • python -m  │ │          │
│  │  │ • Optimize      │  │ • NSIS (Win)    │  │   build      │ │          │
│  │  │ • Tag: staging  │  │ • DMG (macOS)   │  │ • .whl       │ │          │
│  │  │ • Push to ACR   │  │ • AppImage      │  │              │ │          │
│  │  └─────────┬───────┘  └─────────┬───────┘  └──────┬───────┘ │          │
│  │            └──────────────────────┼──────────────────┘        │          │
│  │                                   ↓                           │          │
│  │                    Upload Artifacts to GitHub                 │          │
│  └────────────────────────┬─────────────────────────────────────┘          │
│                           ↓                                                 │
│  ┌──────────────────────────────────────────────────────────────┐          │
│  │  Phase 3: Deploy to Staging (Auto)                           │          │
│  │  Environment: staging.projectai.com                          │          │
│  │                                                               │          │
│  │  1. Helm upgrade staging namespace                           │          │
│  │     └─→ helm upgrade project-ai ./helm/project-ai \          │          │
│  │         --namespace staging \                                │          │
│  │         --set image.tag=staging-abc123                       │          │
│  │                                                               │          │
│  │  2. Wait for rollout complete                                │          │
│  │     └─→ kubectl rollout status deployment/project-ai         │          │
│  │                                                               │          │
│  │  3. Run smoke tests                                          │          │
│  │     ├─→ Health check: GET /health (expect 200)              │          │
│  │     ├─→ Version check: GET /api/version (expect staging)    │          │
│  │     └─→ Basic flow: Login → Dashboard → API call            │          │
│  │                                                               │          │
│  │  4. Run integration tests                                    │          │
│  │     └─→ pytest tests/integration/ (against staging)          │          │
│  │                                                               │          │
│  │  5. Performance benchmarks                                   │          │
│  │     ├─→ Load test: 100 RPS for 5 minutes                    │          │
│  │     ├─→ Verify: p95 latency < 500ms                         │          │
│  │     └─→ Verify: Error rate < 1%                             │          │
│  └────────────────────────┬─────────────────────────────────────┘          │
│                           │                                                 │
│                           ↓                                                 │
│                 All Staging Tests Pass?                                     │
│                    ├─→ No: Rollback, notify team                           │
│                    └─→ Yes: Ready for production                           │
│                           ↓                                                 │
│  ┌──────────────────────────────────────────────────────────────┐          │
│  │  Phase 4: Manual Review & Approval                           │          │
│  │                                                               │          │
│  │  1. Developer creates PR (develop → main)                    │          │
│  │     └─→ gh pr create --base main --head develop              │          │
│  │                                                               │          │
│  │  2. Code review (requires 2 approvals)                       │          │
│  │     ├─→ Reviewer 1: Approve                                  │          │
│  │     └─→ Reviewer 2: Approve                                  │          │
│  │                                                               │          │
│  │  3. Security review (if needed)                              │          │
│  │     └─→ Review Trivy, Bandit reports                         │          │
│  │                                                               │          │
│  │  4. QA sign-off                                              │          │
│  │     └─→ User acceptance testing on staging                   │          │
│  │                                                               │          │
│  │  5. Merge to main                                            │          │
│  │     └─→ gh pr merge --squash                                 │          │
│  └────────────────────────┬─────────────────────────────────────┘          │
│                           ↓                                                 │
│  ┌──────────────────────────────────────────────────────────────┐          │
│  │  Phase 5: Production Deployment (Manual Approval + Auto)     │          │
│  │  Environment: projectai.com                                  │          │
│  │  Strategy: Blue-Green Deployment                             │          │
│  │                                                               │          │
│  │  1. Build production image                                   │          │
│  │     └─→ docker build -t projectai/backend:v1.0.2 .           │          │
│  │     └─→ docker push projectai/backend:v1.0.2                 │          │
│  │                                                               │          │
│  │  2. GitHub Environment approval                              │          │
│  │     └─→ Requires approval from CODEOWNERS                    │          │
│  │     └─→ PagerDuty on-call engineer notified                  │          │
│  │                                                               │          │
│  │  3. Create production backup                                 │          │
│  │     ├─→ Database snapshot                                    │          │
│  │     ├─→ K8s resource backup                                  │          │
│  │     └─→ ConfigMap/Secret backup                              │          │
│  │                                                               │          │
│  │  4. Deploy to Green environment                              │          │
│  │     └─→ helm upgrade project-ai ./helm/project-ai \          │          │
│  │         --namespace production \                             │          │
│  │         --set environment=green \                            │          │
│  │         --set image.tag=v1.0.2 \                             │          │
│  │         --wait --timeout=10m                                 │          │
│  │                                                               │          │
│  │  5. Run smoke tests on Green                                 │          │
│  │     └─→ ./scripts/smoke-tests.sh production-green            │          │
│  │                                                               │          │
│  │  6. Switch traffic to Green (zero downtime)                  │          │
│  │     └─→ kubectl patch service project-ai \                   │          │
│  │         -p '{"spec":{"selector":{"version":"green"}}}'       │          │
│  │                                                               │          │
│  │  7. Monitor Green for 10 minutes                             │          │
│  │     ├─→ Health checks every 30s                              │          │
│  │     ├─→ Error rate < 1%                                      │          │
│  │     ├─→ Latency p95 < 500ms                                 │          │
│  │     └─→ No alerts triggered                                  │          │
│  │                                                               │          │
│  │  8. Cleanup old Blue environment                             │          │
│  │     └─→ kubectl delete deployment project-ai-blue            │          │
│  └────────────────────────┬─────────────────────────────────────┘          │
│                           ↓                                                 │
│  ┌──────────────────────────────────────────────────────────────┐          │
│  │  Phase 6: Post-Deployment                                    │          │
│  │                                                               │          │
│  │  1. Create GitHub Release                                    │          │
│  │     ├─→ Tag: v1.0.2                                          │          │
│  │     ├─→ Release notes from CHANGELOG.md                      │          │
│  │     └─→ Upload desktop installers, APKs, wheels              │          │
│  │                                                               │          │
│  │  2. Publish to package managers                              │          │
│  │     ├─→ PyPI: twine upload dist/*.whl                        │          │
│  │     ├─→ Docker Hub: projectai/backend:v1.0.2                 │          │
│  │     └─→ Homebrew: Update formula                             │          │
│  │                                                               │          │
│  │  3. Update documentation                                     │          │
│  │     ├─→ API docs (if changes)                                │          │
│  │     ├─→ User guide (if new features)                         │          │
│  │     └─→ Deployment docs (if process changes)                 │          │
│  │                                                               │          │
│  │  4. Notify stakeholders                                      │          │
│  │     ├─→ Slack #releases channel                              │          │
│  │     ├─→ Email to users (if major release)                    │          │
│  │     └─→ Social media announcement                            │          │
│  │                                                               │          │
│  │  5. Post-deployment monitoring (24 hours)                    │          │
│  │     ├─→ Monitor error rates, latency                         │          │
│  │     ├─→ Review Sentry error reports                          │          │
│  │     └─→ On-call engineer standby                             │          │
│  └────────────────────────────────────────────────────────────────┘          │
│                                                                             │
│  Deployment Complete! 🎉                                                    │
│                                                                             │
└────────────────────────────────────────────────────────────────────────────┘
```

## Desktop Application Release Pipeline

```
Tag Release: v1.0.2
    ↓
GitHub Actions Trigger
    ↓
┌─────────────────────────────────────┐
│ Build Multi-Platform Installers    │
│                                     │
│ ┌─────────┐ ┌─────────┐ ┌────────┐ │
│ │Windows  │ │ macOS   │ │ Linux  │ │
│ │         │ │         │ │        │ │
│ │PyInstall│ │PyInstall│ │PyInst- │ │
│ │+ NSIS   │ │+ DMG    │ │aller + │ │
│ │         │ │+ Sign   │ │AppImage│ │
│ └────┬────┘ └────┬────┘ └───┬────┘ │
│      └───────────┼──────────┘      │
│                  ↓                  │
│        Artifacts Created:           │
│        • Project-AI-Setup.exe       │
│        • ProjectAI.dmg              │
│        • project-ai.AppImage        │
└──────────────────┬──────────────────┘
                   ↓
┌──────────────────────────────────────┐
│ Android APK Build                    │
│                                      │
│ ./gradlew :legion_mini:assembleRel  │
│ • Sign APK with release keystore    │
│ • Output: legion_mini-release.apk   │
└──────────────────┬───────────────────┘
                   ↓
┌──────────────────────────────────────┐
│ Generate Checksums (SHA256)          │
│                                      │
│ • Windows installer: abc123...       │
│ • macOS DMG: def456...               │
│ • Linux AppImage: ghi789...          │
│ • Android APK: jkl012...             │
└──────────────────┬───────────────────┘
                   ↓
┌──────────────────────────────────────┐
│ Create GitHub Release                │
│                                      │
│ • Title: "Project-AI v1.0.2"        │
│ • Attach all installers              │
│ • Attach checksums.txt               │
│ • Generate release notes             │
│ • Mark as latest release             │
└──────────────────────────────────────┘
```

## Hotfix Pipeline (Emergency)

```
Critical Bug in Production
    ↓
Create Hotfix Branch
    └─→ git checkout -b hotfix/v1.0.3 main
    └─→ Apply critical fix
    └─→ git commit -m "fix: Critical security patch"
        ↓
Fast-Track CI Pipeline
    ├─→ Lint (skip)
    ├─→ Security (critical only)
    └─→ Tests (affected modules)
        ↓ (within 5 minutes)
Merge to main (bypass PR review)
    └─→ git merge hotfix/v1.0.3
    └─→ git tag v1.0.3
    └─→ git push origin main v1.0.3
        ↓
Emergency Production Deploy
    ├─→ Skip staging
    ├─→ Direct to production
    ├─→ Use rolling update (not blue-green)
    └─→ Deploy within 10 minutes
        ↓
Post-Deploy Validation
    ├─→ Verify fix applied
    ├─→ No new errors introduced
    └─→ Rollback if issues
        ↓
Backport to develop
    └─→ git cherry-pick v1.0.3 develop
```

## Rollback Pipeline

```
Production Issue Detected
    ↓
Alert Triggered (PagerDuty)
    ↓
Incident Commander Assessment
    ├─→ Severity: Critical
    └─→ Decision: Immediate Rollback
        ↓
Execute Rollback
    ├─→ Blue-Green: Switch back to blue
    │   └─→ kubectl patch service (instant)
    │
    ├─→ K8s Rollout Undo
    │   └─→ kubectl rollout undo deployment
    │
    └─→ Database Rollback (if needed)
        └─→ alembic downgrade -1
            ↓
Verify Service Restored
    ├─→ Health checks pass
    ├─→ Error rate normal
    └─→ Latency acceptable
        ↓
Post-Incident Review
    ├─→ Root cause analysis
    ├─→ Document lessons learned
    └─→ Implement preventive measures
```

## Related Documents

All deployment relationship documents feed into this pipeline map:
- `01_deployment_system_overview.md` - Architecture
- `02_docker_relationships.md` - Docker builds
- `03_kubernetes_orchestration.md` - K8s deployments
- `04_desktop_packaging.md` - Desktop installers
- `05_cicd_pipelines.md` - GitHub Actions
- `06_release_automation.md` - Release creation
- `07_health_monitoring_hooks.md` - Health validation
- `08_rollback_procedures.md` - Rollback flows
- `09_environment_flows.md` - Environment promotion

---

**Status**: ✅ Complete  
**Coverage**: End-to-end deployment pipeline visualization for all deployment types
