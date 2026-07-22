# Operator Console Visual Regression

This suite compares the production-built operator console against reviewed Chromium
screenshots. It currently covers:

- desktop Command Center;
- mobile Command Center;
- partial-evidence, unavailable, stale, and mobile-offline Command Center states;
- open mobile navigation modal;
- permission-filtered Viewer navigation;
- viewer Atlas access restriction;
- viewer SWR view-only state;
- viewer Atlas Projections access restriction;
- reviewer TAAR view-only state;
- reviewer Inbox human-review boundary;
- administrator account-management surface;
- viewer request-submission restriction;
- viewer account-administration access restriction;
- successful TAAR run with sealed evidence and report-only boundary;
- successful SWR execution receipt without browser capability exposure;
- successful Atlas projection receipt with analysis-only boundary;
- successful Atlas replay verification with no-authority boundary;
- security fail-closed initial state;
- temporary-password security redirect;
- degraded System Health evidence;
- module-catalog fail-closed state;
- partial replay/DOI evidence state;
- sign-in session-boundary and failed-credential state;
- local recovery completion state;
- account-service fail-closed state;
- first-run Owner setup and recovery-code acknowledgement;
- collapsed and expanded desktop audit explorer;
- expanded mobile audit filters;
- privileged desktop record detail; and
- permission-filtered mobile record detail.

The same real-browser suite also verifies skip-link bypass, mobile navigation focus
containment/restoration, record-detail focus movement/restoration, mobile detail reflow,
the audit filter control sequence, focus transfer across three workspaces, and the
administration form's reading/tab order, work-notification dialog focus transfer and
restoration, the SWR/Atlas role boundaries, security redirect/fail-closed behavior,
degraded System Health evidence, module/evidence failure states, sign-in failure
handling, local recovery completion, account-service failure, and first-run setup
without adding snapshot maintenance. The suite contains thirteen reviewed screenshots
and twenty-seven functional browser checks.

The tests intercept `/api/**` with fixed non-secret fixtures, use UTC and `en-US`,
disable motion/carets, bundle the Inter variable font with the application, and fail on
unregistered API requests. This keeps the images independent of local databases,
credentials, clocks, external networks, and production services.

The current tracked Linux baselines match the separately preserved candidate set
byte-for-byte (13/13 SHA-256 matches). The digest-pinned Linux run passes the full
40-test suite, including all 13 screenshot comparisons and 27 functional checks,
without snapshot-update mode.

## Compare reviewed baselines

```powershell
pnpm --filter @project-ai/operator-console exec playwright install chromium
pnpm web:visual
```

Failure traces, actual screenshots, and diffs are written to ignored
`output/playwright/`. CI uploads that directory for seven days only when the visual job
fails.

## Update after an intentional UI change

Start Docker Desktop, inspect the rendered change, then generate both Windows and Linux
baseline sets:

```powershell
powershell -ExecutionPolicy Bypass -File tools/update_operator_console_visual_baselines.ps1
pnpm web:visual
```

Review every changed PNG before committing it. Never run snapshot update mode in CI and
never accept a baseline solely to make a failed comparison green.
