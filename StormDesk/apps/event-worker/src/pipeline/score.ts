/* ── Storm Desk — Incident Scoring ──────────────────────────────── */

import type { ArticleCluster } from './dedupe';
import { HIGH_IMPACT_KEYWORDS } from './normalize';

export type IncidentSource = {
  name: string;
  url: string;
  published_at: string;
  title: string;
};

export type IncidentVerification = {
  independent_sources: number;
  wire_confirmed: boolean;
  broadcaster_confirmed: boolean;
};

export type IncidentStatus = 'watch' | 'elevated' | 'major';

export type Incident = {
  id: string;
  headline: string;
  summary: string;
  keywords: string[];
  regions: string[];
  source_count: number;
  sources: IncidentSource[];
  score: number;
  status: IncidentStatus;
  verification: IncidentVerification;
  first_seen_at: string;
  updated_at: string;
};

const WIRES = new Set(['Reuters', 'Associated Press', 'AP', 'AFP', 'Agence France-Presse']);
const BROADCASTERS = new Set([
  'BBC', 'BBC News', 'Sky News', 'ABC News', 'NBC News', 'CBS News',
  'CNN', 'France 24', 'DW', 'Al Jazeera', 'NHK', 'TRT World',
  'CNBC', 'Bloomberg', 'Fox News',
]);

export function buildIncidentFromCluster(cluster: ArticleCluster): Incident {
  const rep = cluster.representative;
  const articles = cluster.articles;

  const uniqueSources = new Map<string, typeof articles[0]>();
  for (const a of articles) {
    if (!uniqueSources.has(a.source)) {
      uniqueSources.set(a.source, a);
    }
  }

  const sources: IncidentSource[] = [];
  for (const [, article] of uniqueSources) {
    sources.push({
      name: article.source,
      url: article.url,
      published_at: article.publishedAt,
      title: article.title,
    });
  }

  const verification = verifyIncident(sources);

  const allKeywords = new Set<string>();
  for (const article of articles) {
    for (const kw of article.keywords) {
      allKeywords.add(kw);
    }
  }

  const allRegions = new Set<string>();
  for (const article of articles) {
    if (article.country) allRegions.add(article.country);
  }

  const incident: Incident = {
    id: crypto.randomUUID(),
    headline: rep.title,
    summary: rep.description || articles.find((a) => a.description)?.description || '',
    keywords: [...allKeywords],
    regions: [...allRegions],
    source_count: uniqueSources.size,
    sources,
    score: 0,
    status: 'watch',
    verification,
    first_seen_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  };

  incident.score = computeIncidentScore(incident);
  incident.status = classifyIncident(incident.score);

  return incident;
}

export function computeIncidentScore(incident: Incident): number {
  const text = `${incident.headline} ${incident.summary} ${incident.keywords.join(' ')}`.toLowerCase();

  const keywordHits = HIGH_IMPACT_KEYWORDS.filter((k) => text.includes(k)).length;

  const sourceScore = Math.min(incident.source_count * 12, 36);
  const keywordScore = Math.min(keywordHits * 9, 27);
  const wireScore = incident.verification.wire_confirmed ? 16 : 0;
  const broadcasterScore = incident.verification.broadcaster_confirmed ? 10 : 0;

  let multiSourceBonus = 0;
  if (incident.verification.independent_sources >= 3) {
    multiSourceBonus = 11;
  } else if (incident.verification.independent_sources >= 2) {
    multiSourceBonus = 6;
  }

  return Math.min(100, sourceScore + keywordScore + wireScore + broadcasterScore + multiSourceBonus);
}

export function classifyIncident(score: number): IncidentStatus {
  if (score >= 72) return 'major';
  if (score >= 45) return 'elevated';
  return 'watch';
}

export function verifyIncident(sources: { name: string }[]): IncidentVerification {
  const sourceNames = [...new Set(sources.map((s) => s.name.trim()))];
  return {
    independent_sources: sourceNames.length,
    wire_confirmed: sourceNames.some((n) => WIRES.has(n)),
    broadcaster_confirmed: sourceNames.some((n) => BROADCASTERS.has(n)),
  };
}

export function canAutoTrigger(
  incident: Incident,
  env: { minScore: number; minSources: number; requireWire: boolean },
): boolean {
  if (incident.score < env.minScore) return false;
  if (incident.verification.independent_sources < env.minSources) return false;
  if (env.requireWire && !incident.verification.wire_confirmed) return false;
  return true;
}
