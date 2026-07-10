# Watcher Matrix

Watchers observe the facility itself. They return findings; they never
repair, delete, kill, or mutate. They may recommend quarantine.

| Watcher lane | Watches | Trigger | Verdict |
|---|---|---|---|
| heartbeat | registry files, automation dirs, parseability | every 5 min | missing/invalid → BLACK |
| lock | locks/ | every 5 min | stale → medium; malformed/unknown-agent → BLACK |
| runaway | active locks vs task timeout | every 5 min | expired lock → high (report only, never kills) |
| phantom | evidence/reports/digests/patches trees | every 5 min | unaccounted artifact → BLACK; any patch file → critical |
| governance | writer output records, evidence hashes | every 6 h | missing citation / invalid hash / patch artifact → BLACK |
| permissions (in-code watcher) | registry grants | on demand | validation errors → high; broad `**` grants → medium |

Lock expiry authority belongs to the lock watcher lane + human review.
The executor denies on stale locks; it never removes them.
