/* ── Storm Desk — Incident Store ─────────────────────────────────── */

import type { Incident } from './score';
import { cfg } from '../config';

/**
 * In-memory incident store with TTL-based expiration.
 * A future version can swap this for SQLite (better-sqlite3) with
 * the same interface by replacing the Map with DB operations.
 */

const incidents = new Map<string, Incident>();
const clusterIndex = new Map<string, string>(); // normalizedHeadline -> incidentId

export function upsertIncident(incident: Incident): void {
  const existing = incidents.get(incident.id);
  if (existing) {
    existing.score = Math.max(existing.score, incident.score);
    existing.status = incident.status;
    existing.source_count = incident.source_count;
    existing.sources = deduplicateSources([...existing.sources, ...incident.sources]);
    existing.verification = incident.verification;
    existing.keywords = [...new Set([...existing.keywords, ...incident.keywords])];
    existing.regions = [...new Set([...existing.regions, ...incident.regions])];
    existing.updated_at = new Date().toISOString();
  } else {
    incidents.set(incident.id, { ...incident });
  }
}

export function findExistingIncidentId(normalizedHeadline: string): string | undefined {
  return clusterIndex.get(normalizedHeadline);
}

export function registerClusterMapping(normalizedHeadline: string, incidentId: string): void {
  clusterIndex.set(normalizedHeadline, incidentId);
}

export function getAllIncidents(): Incident[] {
  return [...incidents.values()].sort((a, b) => b.score - a.score);
}

export function getMajorIncidents(): Incident[] {
  return getAllIncidents().filter((i) => i.status === 'major');
}

export function getIncidentById(id: string): Incident | undefined {
  return incidents.get(id);
}

export function pruneExpiredIncidents(): number {
  const maxAge = cfg.store.maxAgeDays * 24 * 60 * 60 * 1000;
  const cutoff = Date.now() - maxAge;
  let pruned = 0;

  for (const [id, inc] of incidents) {
    const timestamp = new Date(inc.first_seen_at).getTime();
    if (timestamp < cutoff) {
      incidents.delete(id);
      pruned++;
    }
  }

  // Clean up stale cluster index entries
  for (const [headline, id] of clusterIndex) {
    if (!incidents.has(id)) {
      clusterIndex.delete(headline);
    }
  }

  return pruned;
}

export function getStoreStats(): {
  total: number;
  major: number;
  elevated: number;
  watch: number;
} {
  let major = 0;
  let elevated = 0;
  let watch = 0;
  for (const inc of incidents.values()) {
    switch (inc.status) {
      case 'major': major++; break;
      case 'elevated': elevated++; break;
      case 'watch': watch++; break;
    }
  }
  return { total: incidents.size, major, elevated, watch };
}

function deduplicateSources(
  sources: Incident['sources'],
): Incident['sources'] {
  const seen = new Set<string>();
  return sources.filter((s) => {
    const key = `${s.name}::${s.url}`;
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}
