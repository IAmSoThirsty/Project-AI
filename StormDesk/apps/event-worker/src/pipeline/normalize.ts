/* ── Storm Desk — Article Normalization ──────────────────────────── */

import type { RawArticle } from '../sources/newsdata';

export type NormalizedArticle = {
  title: string;
  description: string;
  source: string;
  url: string;
  publishedAt: string;
  country: string;
  language: string;
  titleNormalized: string;
  keywords: string[];
};

const HIGH_IMPACT_KEYWORDS = [
  'earthquake', 'explosion', 'war', 'missile', 'evacuation', 'shooting',
  'hostage', 'airstrike', 'cyberattack', 'blackout', 'tsunami', 'coup',
  'terror', 'emergency', 'breaking', 'mass casualty', 'state of emergency',
  'wildfire', 'hurricane', 'tornado', 'flood', 'nuclear', 'assassination',
  'pandemic', 'martial law', 'chemical attack', 'bioweapon', 'embargo',
  'sanctions', 'ceasefire', 'invasion', 'genocide', 'famine',
];

export function normalizeArticle(raw: RawArticle): NormalizedArticle {
  const title = sanitizeText(raw.title);
  const description = sanitizeText(raw.description ?? '');
  const combined = `${title} ${description}`.toLowerCase();

  return {
    title,
    description,
    source: sanitizeText(raw.source),
    url: raw.url,
    publishedAt: raw.publishedAt,
    country: raw.country ?? '',
    language: raw.language ?? 'en',
    titleNormalized: normalizeHeadline(title),
    keywords: HIGH_IMPACT_KEYWORDS.filter((k) => combined.includes(k)),
  };
}

export function normalizeBatch(articles: RawArticle[]): NormalizedArticle[] {
  const seen = new Set<string>();
  const results: NormalizedArticle[] = [];

  for (const raw of articles) {
    if (!raw.title || !raw.url) continue;

    const urlKey = raw.url.toLowerCase().replace(/\/$/, '');
    if (seen.has(urlKey)) continue;
    seen.add(urlKey);

    results.push(normalizeArticle(raw));
  }

  return results;
}

function normalizeHeadline(s: string): string {
  return s
    .toLowerCase()
    .replace(/[^a-z0-9\s]/g, ' ')
    .replace(/\b(live|update|updates|breaking|report|reports|watch|video)\b/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

function sanitizeText(s: string): string {
  return s
    .replace(/<[^>]+>/g, '')
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .trim();
}

export { HIGH_IMPACT_KEYWORDS };
