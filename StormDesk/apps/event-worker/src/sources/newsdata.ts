/* ── Storm Desk — NewsData.io Source Adapter ─────────────────────── */

import { cfg } from '../config';

export type RawArticle = {
  title: string;
  description?: string;
  source: string;
  url: string;
  publishedAt: string;
  country?: string;
  language?: string;
};

const NEWSDATA_BASE = 'https://newsdata.io/api/1/latest';

export async function fetchNewsData(): Promise<RawArticle[]> {
  if (!cfg.newsdata.enabled) return [];

  const params = new URLSearchParams({
    apikey: cfg.newsdata.apiKey,
    language: 'en',
    category: 'politics,world,environment,health,science,technology',
  });

  try {
    const res = await fetch(`${NEWSDATA_BASE}?${params.toString()}`, {
      signal: AbortSignal.timeout(15_000),
      headers: { 'Accept': 'application/json' },
    });

    if (!res.ok) {
      console.warn(`[newsdata] HTTP ${res.status}: ${res.statusText}`);
      return [];
    }

    const body = await res.json();
    const results: any[] = body.results ?? [];

    return results
      .filter((item: any) => item.title && item.link)
      .map((item: any): RawArticle => ({
        title: String(item.title).trim(),
        description: item.description ? String(item.description).trim() : undefined,
        source: item.source_name ?? item.source_id ?? 'NewsData',
        url: String(item.link).trim(),
        publishedAt: item.pubDate
          ? new Date(item.pubDate).toISOString()
          : new Date().toISOString(),
        country: Array.isArray(item.country) ? item.country[0] : item.country,
        language: item.language ?? 'en',
      }));
  } catch (err) {
    console.error('[newsdata] Fetch error:', err);
    return [];
  }
}
