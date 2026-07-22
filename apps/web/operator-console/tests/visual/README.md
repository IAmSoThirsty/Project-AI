# Operator Console Visual Regression

This suite compares the production-built operator console against reviewed Chromium
screenshots. It currently covers:

- desktop Command Center;
- mobile Command Center;
- partial-evidence, unavailable, stale, and mobile-offline Command Center states;
- open mobile navigation modal;
- permission-filtered Viewer navigation;
- collapsed and expanded desktop audit explorer;
- expanded mobile audit filters;
- privileged desktop record detail; and
- permission-filtered mobile record detail.

The same real-browser suite also verifies skip-link bypass, mobile navigation focus
containment/restoration, record-detail focus movement/restoration, mobile detail reflow,
the audit filter control sequence, focus transfer across three workspaces, and the
administration form's reading/tab order without adding snapshot maintenance. The suite
contains thirteen reviewed screenshots and five functional browser checks.

The tests intercept `/api/**` with fixed non-secret fixtures, use UTC and `en-US`,
disable motion/carets, bundle the Inter variable font with the application, and fail on
unregistered API requests. This keeps the images independent of local databases,
credentials, clocks, external networks, and production services.

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
