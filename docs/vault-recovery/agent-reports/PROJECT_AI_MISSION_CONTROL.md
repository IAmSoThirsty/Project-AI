# Project-AI Mission Control

Your live operations dashboard for Project-AI work inside Obsidian.

---

## Health Score

```dataviewjs
const DAY_MS = 1000 * 60 * 60 * 24;
const now = Date.now();

const files = app.vault.getMarkdownFiles();

// 1) Open checklist items across vault
let openChecklistCount = 0;
for (const f of files) {
   const text = await app.vault.cachedRead(f);
   const matches = text.match(/- \[ \]/g);
   if (matches) openChecklistCount += matches.length;
}

// 2) Stale reports (older than 14 days) under docs/reports paths
const reportFiles = files.filter(f =>
   f.path.includes("Project-AI/docs/reports/") || f.path.includes("docs/reports/")
);
const staleReports = reportFiles.filter(f => (now - f.stat.mtime) / DAY_MS > 14).length;

// 3) Critical governance docs freshness (older than 30 days)
const criticalDocNeedles = [
   "COPILOT_MANDATORY_GUIDE.md",
   "VERIFIED_SYSTEMS_INVENTORY.md",
   "copilot_workspace_profile.md",
   "THIRST_BRANCH_ACCEPTANCE_CRITERIA.md"
];

const criticalDocs = criticalDocNeedles.map(needle =>
   files.find(f => f.path.endsWith(needle))
);

const missingCritical = criticalDocs.filter(x => !x).length;
const staleCritical = criticalDocs.filter(x => x && (now - x.stat.mtime) / DAY_MS > 30).length;

// Weighted score (bounded penalties)
const penaltyOpen = Math.min(35, Math.floor(openChecklistCount / 10));
const penaltyStaleReports = Math.min(30, staleReports * 2);
const penaltyCritical = Math.min(35, (missingCritical * 10) + (staleCritical * 5));
const healthScore = Math.max(0, 100 - penaltyOpen - penaltyStaleReports - penaltyCritical);

const grade = healthScore >= 90 ? "A" : healthScore >= 80 ? "B" : healthScore >= 70 ? "C" : healthScore >= 60 ? "D" : "F";
const status = healthScore >= 85 ? "🟢 Healthy" : healthScore >= 70 ? "🟡 Watch" : "🔴 Needs attention";

dv.paragraph(`> [!summary] Vault Health Score\n> **${healthScore}/100** (Grade **${grade}**) — ${status}`);
dv.table(
   ["Metric", "Value", "Rule"],
   [
      ["Open checklist items", openChecklistCount, "Penalty: up to 35"],
      ["Stale reports (>14d)", staleReports, "Penalty: 2 each (max 30)"],
      ["Missing critical governance docs", missingCritical, "Penalty: 10 each"],
      ["Stale critical governance docs (>30d)", staleCritical, "Penalty: 5 each"],
      ["Total penalties", penaltyOpen + penaltyStaleReports + penaltyCritical, "Bounded composite"],
   ]
);
```

---

## Quick Launch

- Command center: `[[PROJECT_AI_COMMAND_CENTER]]`
- Quick actions: `[[PROJECT_AI_REPO_QUICK_ACTIONS]]`
- Handoff template: `[[templates/AI_AGENT_HANDOFF_TEMPLATE]]`
- Curator prompt: `[[copilot/system-prompts/Obsidian Vault Curator - Project-AI]]`

---

## Today

```dataview
TABLE file.mtime as "Last Updated"
FROM ""
WHERE file.name = dateformat(date(today), "yyyy-MM-dd")
SORT file.mtime DESC
```

---

## Recent Reports (last 14 days)

```dataview
TABLE file.mtime as "Modified", file.folder as "Folder"
FROM "Project-AI/docs/reports" OR "docs/reports"
WHERE date(today) - file.mtime <= dur(14 days)
SORT file.mtime DESC
LIMIT 25
```

---

## Agent / Completion Notes (recent)

```dataview
TABLE file.mtime as "Modified", file.folder as "Folder"
FROM ""
WHERE contains(upper(file.name), "AGENT") OR contains(upper(file.name), "COMPLETION") OR contains(upper(file.name), "MISSION")
SORT file.mtime DESC
LIMIT 40
```

---

## Governance & Architecture Hotspots

```dataview
TABLE file.folder as "Folder", file.mtime as "Modified"
FROM "Project-AI/.github" OR "Project-AI/src/app/core"
WHERE contains(file.path, "copilot_workspace_profile")
   OR contains(file.path, "COPILOT_MANDATORY_GUIDE")
   OR contains(file.path, "VERIFIED_SYSTEMS_INVENTORY")
   OR contains(file.path, "pipeline.py")
   OR contains(file.path, "constitutional_model.py")
   OR contains(file.path, "octoreflex.py")
   OR contains(file.path, "tscg_codec.py")
   OR contains(file.path, "state_register.py")
SORT file.mtime DESC
```

---

## Open TODO Checklists (simple scan)

```dataview
TABLE file.folder as "Folder", file.mtime as "Modified"
FROM ""
WHERE contains(file.content, "- [ ]")
SORT file.mtime DESC
LIMIT 30
```

---

## Recently Changed in Cloned Repo

```dataview
TABLE file.mtime as "Modified"
FROM "Project-AI"
SORT file.mtime DESC
LIMIT 50
```

---

## Local AI Runtime Check (manual)

- LM Studio endpoint: `http://127.0.0.1:1234/v1`
- Chat model key: `obsidian-agent|lm-studio`
- Embedding key: `text-embedding-nomic-embed-text-v1.5|lm-studio`

If Copilot behaves oddly, reopen Obsidian and confirm the model picker still shows `obsidian-agent`.

---

## Notes

- If a query returns nothing, verify folder path prefixes in your vault (some notes may live under root vs `Project-AI/...`).
- If Dataview is disabled, enable the Dataview community plugin to activate dashboard blocks.

<!-- sovereign-vault-index-link -->
Central Index: [[Sovereign Vault Index]]
